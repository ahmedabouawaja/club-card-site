from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField
from wtforms.validators import DataRequired, Email, Length, EqualTo, ValidationError

from app.models import User


class RegisterForm(FlaskForm):
    name = StringField("الاسم", validators=[DataRequired(), Length(min=2, max=120)])
    email = StringField("الإيميل", validators=[DataRequired(), Email(), Length(max=255)])
    password = PasswordField(
        "كلمة السر",
        validators=[
            DataRequired(),
            Length(min=10, message="استخدم 10 حروف على الأقل."),
        ],
    )
    confirm = PasswordField(
        "تأكيد كلمة السر",
        validators=[DataRequired(), EqualTo("password", message="كلمتا السر غير متطابقتين.")],
    )

    def validate_email(self, field):
        if User.query.filter_by(email=field.data.lower().strip()).first():
            raise ValidationError("An account with this email already exists.")

    def validate_password(self, field):
        pw = field.data
        # Basic strength check without an external service: mixed character classes.
        classes = sum([
            any(c.islower() for c in pw),
            any(c.isupper() for c in pw),
            any(c.isdigit() for c in pw),
            any(not c.isalnum() for c in pw),
        ])
        if classes < 3:
            raise ValidationError("Use a mix of upper/lowercase letters, numbers, and symbols.")


class LoginForm(FlaskForm):
    email = StringField("الإيميل", validators=[DataRequired(), Length(max=255)])
    password = PasswordField("كلمة السر", validators=[DataRequired()])
    remember = BooleanField("خلّيني داخل")
