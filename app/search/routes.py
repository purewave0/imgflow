from flask import render_template

from app.search import bp


@bp.route('/')
def search_posts():
    return render_template('search/index.html')
