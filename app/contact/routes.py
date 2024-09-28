from flask import render_template

from app.contact import bp


@bp.route('/')
def index():
    return render_template('contact/index.html')
