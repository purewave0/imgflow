import os
import uuid

from flask import jsonify, request
from werkzeug.utils import secure_filename

from app.api import bp
from app.dbapi import (
    create_post,
    get_posts, get_post_media, get_post_and_media, get_post_comments, 
)
from app.models.post import Post


# TODO: not explicitly write the full path
MEDIA_UPLOAD_FOLDER = '/home/will/proj/imgflow/app/static/uploads'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'webp'}

def is_file_allowed(filename):
    # TODO: stricter file checking
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


def randomize_filename(filename):
    _, extension = os.path.splitext(filename)
    return uuid.uuid4().hex + extension



@bp.route('/posts', methods=['GET', 'POST'])
def api_posts():
    if request.method == 'GET':
        posts = get_posts()
        return jsonify(posts)

    title = request.form.get('title')
    uploaded_files = request.files.getlist("file")

    media_urls = []
    for file in uploaded_files:
        if is_file_allowed(file.filename):
            filename = secure_filename(randomize_filename(file.filename))
            media_destination = os.path.join(MEDIA_UPLOAD_FOLDER, filename)
            file.save(media_destination)
            media_urls.append(os.path.join('/static/uploads', filename))
        else:
            return jsonify({'error': 'wrong_filetype'}), 400

    # TODO: descriptions
    post_media_list = tuple(
        {'media_url': media_url, 'description': None}
        for media_url in media_urls
    )

    new_post = create_post(title, post_media_list)
    return jsonify(new_post)


@bp.route('/posts/<post_id>')
def api_post(post_id):
    if len(post_id) != Post.POST_ID_LENGTH:
        return '', 404;
    post = get_post_and_media(post_id)
    return jsonify(post)


@bp.route('/posts/<post_id>/comments')
def api_post_comments(post_id):
    if len(post_id) != Post.POST_ID_LENGTH:
        return '', 404;
    comments = get_post_comments(post_id)
    return jsonify(comments)
