import os
import uuid

from flask import jsonify, request
from werkzeug.utils import secure_filename

from app.api import bp
from app.dbapi import (
    create_post, vote_post, comment_on_post, vote_comment, reply_to_comment,
    get_comment_replies, get_public_posts, get_post_media, get_post_and_media,
    get_post_comments, Vote, Sorting
)
from app.models.post import Post


MEDIA_UPLOAD_FOLDER = 'app/static/uploads'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'webp'}

MAX_TITLE_LENGTH = 128
MAX_COMMENT_LENGTH = 2_000


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
        posts = get_public_posts()
        return jsonify(posts)

    title = request.form.get('title')
    if len(title) > MAX_TITLE_LENGTH:
        return jsonify({'error': 'wrong_title_length'}), 400

    is_public = request.form.get('is_public') == 'true'
    uploaded_files = request.files.getlist("media_file")
    descriptions = request.form.getlist("description")

    post_media_list = []
    for file, description in zip(uploaded_files, descriptions):
        if is_file_allowed(file.filename):
            filename = secure_filename(randomize_filename(file.filename))
            media_destination = os.path.join(MEDIA_UPLOAD_FOLDER, filename)
            file.save(media_destination)
            clean_description = description.strip()
            post_media_list.append({
                'media_url': os.path.join('/static/uploads', filename),
                'description':
                    clean_description if clean_description else None,
            })
        else:
            return jsonify({'error': 'wrong_filetype'}), 400

    new_post = create_post(title, post_media_list, is_public)
    return jsonify(new_post)


@bp.route('/posts/<post_id>')
def api_post(post_id):
    if len(post_id) != Post.POST_ID_LENGTH:
        return '', 404;
    post = get_post_and_media(post_id)
    return jsonify(post)


@bp.route('/posts/<post_id>/votes', methods=['POST'])
def api_vote_post(post_id):
    if len(post_id) != Post.POST_ID_LENGTH:
        return '', 404

    try:
        vote = request.json['vote']
    except KeyError:
        return jsonify({'error': 'missing_vote'}), 400

    if vote not in ('upvote', 'downvote'):
        return jsonify({'error': 'invalid_vote'}), 400

    # TODO: check if post and comment id exist
    vote_post(
        post_id,
        Vote.UPVOTE if vote == 'upvote' else Vote.DOWNVOTE
    )
    return '', 204




@bp.route('/posts/<post_id>/comments', methods=['GET', 'POST'])
def api_post_comments(post_id):
    if len(post_id) != Post.POST_ID_LENGTH:
        return '', 404;
    # TODO: check if post id exists

    if request.method == 'GET':
        try:
            sorting = Sorting(request.args.get('sort'))
        except ValueError:
            return jsonify({'error': 'invalid_sort'}), 400

        comments = get_post_comments(post_id, sorting)
        return jsonify(comments)

    try:
        content = request.json['content']
    except KeyError:
        return jsonify({'error': 'missing_content'}), 400

    content = content.strip()
    if not content or len(content) > MAX_COMMENT_LENGTH:
        return jsonify({'error': 'wrong_content_length'}), 400


    comment = comment_on_post(post_id, content)
    return jsonify(comment), 201


@bp.route('/posts/<post_id>/comments/<comment_id>/votes', methods=['POST'])
def api_vote_comment(post_id, comment_id):
    if len(post_id) != Post.POST_ID_LENGTH:
        return '', 404

    try:
        vote = request.json['vote']
    except KeyError:
        return jsonify({'error': 'missing_vote'}), 400

    if vote not in ('upvote', 'downvote'):
        return jsonify({'error': 'invalid_vote'}), 400

    # TODO: check if post and comment id exist
    vote_comment(
        post_id,
        comment_id,
        Vote.UPVOTE if vote == 'upvote' else Vote.DOWNVOTE
    )
    return '', 204


@bp.route('/posts/<post_id>/comments/<comment_id>/replies', methods=['GET', 'POST'])
def api_comment_replies(post_id, comment_id):
    if len(post_id) != Post.POST_ID_LENGTH:
        return '', 404;
    # TODO: check if post id and comment id exist

    if request.method == 'GET':
        try:
            sorting = Sorting(request.args.get('sort'))
        except ValueError:
            return jsonify({'error': 'invalid_sort'}), 400

        replies = get_comment_replies(post_id, comment_id, sorting)
        return jsonify(replies)

    try:
        content = request.json['content']
    except KeyError:
        return jsonify({'error': 'missing_content'}), 400

    content = content.strip()
    if not content or len(content) > MAX_COMMENT_LENGTH:
        return jsonify({'error': 'wrong_content_length'}), 400


    reply = reply_to_comment(post_id, comment_id, content)
    return jsonify(reply), 201
