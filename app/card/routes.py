from flask import render_template, abort
from flask_login import login_required, current_user

from app.branding import present_card
from app.card import bp


@bp.route("/")
@login_required
def my_card():
    card = current_user.card
    if card is None:
        abort(404)
    return render_template("card/my_card.html", card=card, presentation=present_card(card, current_user))
