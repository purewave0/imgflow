from flask import Blueprint


bp = Blueprint('flows', __name__)

from app.flows import routes
