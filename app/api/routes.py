from flask import jsonify

from app.api import bp
from app.dbapi import (
    create_post,
    get_posts, get_post_media, get_post_and_media, get_post_comments, 
)
from app.models.post import Post


@bp.route('/posts')
def api_posts():
    posts = get_posts()
    return jsonify(posts)


@bp.route('/posts/<post_id>')
def api_post(post_id):
    if len(post_id) != Post.POST_ID_LENGTH:
        return '', 404;
    post = get_post_and_media(post_id)
    return jsonify(post)
