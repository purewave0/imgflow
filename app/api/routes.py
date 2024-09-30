from flask import jsonify

from app.api import bp
from app.dbapi import (
    create_post,
    get_posts, get_post_media, get_post_comments
)


@bp.route('/posts')
def api_posts():
    posts = get_posts()
    return jsonify(posts)
