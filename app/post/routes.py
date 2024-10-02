from flask import render_template

from app.post import bp
from app.dbapi import get_post_and_media, increment_post_views


@bp.route('/<post_id>')
def show_post(post_id):
    full_post = get_post_and_media(post_id)
    increment_post_views(post_id)

    return render_template(
        'post/index.html',
        post_title=full_post['title'],
        post_created_on=full_post['created_on'].isoformat() + 'Z',
        media=full_post['media'],
    )
