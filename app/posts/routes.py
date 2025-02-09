from flask import render_template

from app.posts import bp
from app.dbapi import get_post_and_media, increment_post_views


@bp.route('/<post_id>')
def show_post(post_id):
    full_post = get_post_and_media(post_id)
    if not full_post:
        return render_template('posts/404.html')

    increment_post_views(post_id)
    return render_template(
        'posts/index.html',
        post_id=full_post['post_id'],
        post_title=full_post['title'],
        post_score=full_post['score'],
        post_comment_count=full_post['comment_count'],
        post_views=full_post['views'] + 1, # because it was just viewed
        post_created_on=full_post['created_on'].isoformat() + 'Z',
        media=full_post['media'],
    )
