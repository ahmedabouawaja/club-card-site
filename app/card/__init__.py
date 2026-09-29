from flask import Blueprint

bp = Blueprint("card", __name__, template_folder="../templates/card")

from app.card import routes  # noqa: E402,F401
