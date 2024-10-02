from flask import render_template

from app.post import bp
from app.dbapi import get_post_and_media


@bp.route('/<post_id>')
def show_post(post_id):
    full_post = get_post_and_media(post_id)
    return render_template(
        'post/index.html',
        post_title=full_post['title'],
        post_created_on=full_post['created_on'],
        media=full_post['media'],
    )
