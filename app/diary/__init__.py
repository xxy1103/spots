from flask import Blueprint

diary = Blueprint('diary', __name__)

from . import routes