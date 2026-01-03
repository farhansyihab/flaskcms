from flask import Blueprint

public_bp = Blueprint(
    "public",
    __name__,
    template_folder="templates"
)

from .routes.home import *
from .routes.article import *
from .routes.search import *
from .routes.includes import *