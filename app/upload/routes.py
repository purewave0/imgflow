from flask import render_template

from app.upload import bp


@bp.route('/')
def show_upload():
    return render_template('upload/index.html')
