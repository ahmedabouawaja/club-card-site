from datetime import datetime, timedelta, date

from flask import render_template, redirect, url_for, flash, request
from flask_login import login_user, logout_user, login_required, current_user

from app.auth import bp
from app.auth.forms import RegisterForm, LoginForm
from app.extensions import db, limiter
from app.models import User, MembershipCard
from app.utils import log_action, generate_member_no

MAX_FAILED_ATTEMPTS = 5
LOCKOUT_MINUTES = 15


@bp.route("/register", methods=["GET", "POST"])
@limiter.limit("10 per hour")  # slow down mass account creation
def register():
    if current_user.is_authenticated:
        return redirect(url_for("card.my_card"))

    form = RegisterForm()
    if form.validate_on_submit():
        user = User(name=form.name.data.strip(), email=form.email.data.lower().strip())
        user.set_password(form.password.data)
        db.session.add(user)
        db.session.flush()  # get user.id before creating the card

        card = MembershipCard(
            user_id=user.id,
            member_no=generate_member_no(),
            tier="member",
            valid_until=date.today() + timedelta(days=365),
        )
        db.session.add(card)
        db.session.commit()

        log_action("register", detail=f"user_id={user.id}")
        flash("Account created — please log in.", "success")
        return redirect(url_for("auth.login"))

    return render_template("auth/register.html", form=form)


@bp.route("/login", methods=["GET", "POST"])
@limiter.limit("10 per minute")  # throttles password-guessing scripts regardless of account lock
def login():
    if current_user.is_authenticated:
        return redirect(url_for("card.my_card"))

    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data.lower().strip()).first()

        # Same generic error whether the email doesn't exist or the password is wrong —
        # never reveal which one, that's a user-enumeration leak.
        generic_error = "Invalid email or password."

        if user is None:
            flash(generic_error, "danger")
            return render_template("auth/login.html", form=form)

        if user.locked_until and user.locked_until > datetime.utcnow():
            minutes_left = int((user.locked_until - datetime.utcnow()).total_seconds() // 60) + 1
            flash(f"Account temporarily locked. Try again in {minutes_left} minute(s).", "danger")
            return render_template("auth/login.html", form=form)

        if not user.is_active_account:
            flash("This account has been disabled. Contact the club.", "danger")
            return render_template("auth/login.html", form=form)

        if user.check_password(form.password.data):
            user.failed_login_attempts = 0
            user.locked_until = None
            db.session.commit()

            login_user(user, remember=form.remember.data)
            log_action("login_success")
            flash(f"Welcome back, {user.name}.", "success")

            next_page = request.args.get("next")
            # Only ever redirect to a same-site relative path — never follow an
            # attacker-supplied absolute/external `next` (open-redirect guard).
            if next_page and next_page.startswith("/"):
                return redirect(next_page)
            if user.is_admin:
                return redirect(url_for("admin.content"))
            return redirect(url_for("card.my_card"))

        user.failed_login_attempts += 1
        if user.failed_login_attempts >= MAX_FAILED_ATTEMPTS:
            user.locked_until = datetime.utcnow() + timedelta(minutes=LOCKOUT_MINUTES)
            log_action("account_locked", detail=f"user_id={user.id}")
        db.session.commit()

        log_action("login_failed", detail=f"user_id={user.id}")
        flash(generic_error, "danger")

    return render_template("auth/login.html", form=form)


@bp.route("/logout", methods=["POST"])
@login_required
def logout():
    log_action("logout")
    logout_user()
    flash("You've been logged out.", "info")
    return redirect(url_for("main.index"))
