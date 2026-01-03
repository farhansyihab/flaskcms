from flask import Blueprint

admin_bp = Blueprint(
    "admin",
    __name__,
    template_folder="templates"
)

from .routes.dashboard import *
from .routes.pages import *
from .routes.news import *
from .routes.auth import *