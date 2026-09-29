from flask import Blueprint

bp = Blueprint("admin", __name__, template_folder="../templates/admin")

from app.admin import routes  # noqa: E402,F401
from app.admin import cms_routes  # noqa: E402,F401
