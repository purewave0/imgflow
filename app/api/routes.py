import os
import uuid

from flask import jsonify, request
from flask_login import current_user, login_user
from werkzeug.utils import secure_filename
from PIL import Image
import regex

from app.api import bp
from app.dbapi import (
    create_post, vote_post, comment_on_post, vote_comment, reply_to_comment,
    get_comment_replies, get_public_posts_by_page, search_public_posts_by_page,
    get_post_media, get_post_and_media,
    get_post_comments_by_page, Vote, PostSorting, CommentSorting,
    get_flow, get_flows_overview, suggest_flows_by_name,
    get_public_posts_in_flow_by_page,
    create_user, is_username_taken, get_user_by_name
)
from app.models.post import Post, Flow
from app.models.user import User


flow_regex_pattern = regex.compile(r"""
    [
        \p{L} # letters (from any language)
        \p{N} # numbers
        \-    # hyphen
    ]{2,50}   # between 2 to 50 characters
""", regex.VERBOSE)

# TODO: username_regex_pattern

UPLOADS_MEDIA_PATH      = 'app/static/uploads/media'
UPLOADS_THUMBNAILS_PATH = 'app/static/uploads/thumbnails'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'webp'}

MAX_THUMBNAIL_SIZE = (256, 256)

MAX_COMMENT_LENGTH = 2_000
MAX_DESCRIPTION_LENGTH = 2_000


def is_file_allowed(filename):
    # TODO: stricter file checking
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


def randomize_filename(filename):
    _, extension = os.path.splitext(filename)
    return uuid.uuid4().hex + extension


def thumbnail_from_file(file):
    # TODO: handle invalid image
    image = Image.open(file)
    image.thumbnail(MAX_THUMBNAIL_SIZE)
    return image


@bp.route('/posts', methods=['GET', 'POST'])
def api_posts():
    if request.method == 'GET':
        page = request.args.get('page') or 0
        try:
            page = int(page)
        except ValueError:
            return jsonify({'error': 'invalid_page'}), 400

        try:
            sorting = PostSorting(request.args.get('sort'))
        except ValueError:
            return jsonify({'error': 'invalid_sort'}), 400

        title_query = request.args.get('title')
        posts = None
        if title_query:
            posts = search_public_posts_by_page(title_query, page, sorting)
        else:
            posts = get_public_posts_by_page(page, sorting)

        return jsonify(posts)

    title = request.form.get('title')
    if len(title) > Post.MAX_TITLE_LENGTH:
        return jsonify({'error': 'wrong_title_length'}), 400

    is_public = request.form.get('is_public') == 'true'

    flows = []
    if is_public:
        raw_flows = request.form.getlist('flow')
        if len(raw_flows) > Post.MAX_FLOWS_PER_POST:
            return jsonify({'error': 'too_many_flows'}), 400

        for flow_name in raw_flows:
            name_length = len(flow_name)
            if (
                name_length < Flow.MIN_NAME_LENGTH
                or name_length > Flow.MAX_NAME_LENGTH
            ):
                return jsonify({'error': 'wrong_flow_name_length'}), 400

            if not flow_regex_pattern.fullmatch(flow_name):
                return jsonify({'error': 'invalid_flow_name'}), 400

            flows.append(flow_name)


    uploaded_files = request.files.getlist("media_file")
    descriptions = request.form.getlist("description")

    post_media_list = []
    for file, description in zip(uploaded_files, descriptions):
        clean_description = description.strip() or None
        if (
            clean_description and len(clean_description) > MAX_DESCRIPTION_LENGTH
        ):
            return jsonify({'error': 'wrong_description_length'}), 400

        if is_file_allowed(file.filename):
            filename = secure_filename(randomize_filename(file.filename))

            media_destination = os.path.join(UPLOADS_MEDIA_PATH, filename)
            file.save(media_destination)

            thumbnail_destination = os.path.join(UPLOADS_THUMBNAILS_PATH, filename)
            thumbnail = thumbnail_from_file(file)
            thumbnail.save(thumbnail_destination)

            post_media_list.append({
                'media_url': os.path.join('/static/uploads/media', filename),
                'thumbnail_url': os.path.join('/static/uploads/thumbnails', filename),
                'description': clean_description,
            })
        else:
            return jsonify({'error': 'wrong_filetype'}), 400

    new_post = create_post(title, post_media_list, is_public, flows)
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
        page = request.args.get('page') or 0
        try:
            page = int(page)
        except ValueError:
            return jsonify({'error': 'invalid_page'}), 400

        try:
            sorting = CommentSorting(request.args.get('sort'))
        except ValueError:
            return jsonify({'error': 'invalid_sort'}), 400

        comments = get_post_comments_by_page(post_id, page, sorting)
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
            sorting = CommentSorting(request.args.get('sort'))
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


# -- flows --

@bp.route('/flow-suggestions')
def api_flow_suggestions():
    partial_name = request.args.get('name')
    if not partial_name:
        return jsonify({'error':'missing_name'}), 400

    return jsonify(suggest_flows_by_name(partial_name))


@bp.route('/flows')
def api_flows():
    is_overview = bool(request.args.get('overview'))
    if is_overview:
        return jsonify(get_flows_overview())

    # TODO: by pages
    return jsonify('TODO')


@bp.route('/flows/<flow_name>')
def api_flow(flow_name):
    if len(flow_name) > Flow.MAX_NAME_LENGTH:
        return jsonify(None), 404

    flow = get_flow(flow_name)
    if not flow:
        return jsonify(None), 404

    # don't return the ID
    del flow['id']

    return jsonify(flow)


@bp.route('/flows/<flow_name>/posts')
def api_posts_in_flow(flow_name):
    page = request.args.get('page') or 0
    try:
        page = int(page)
    except ValueError:
        return jsonify({'error': 'invalid_page'}), 400

    try:
        sorting = PostSorting(request.args.get('sort'))
    except ValueError:
        return jsonify({'error': 'invalid_sort'}), 400

    name_length = len(flow_name)
    if (
        name_length < Flow.MIN_NAME_LENGTH
        or name_length > Flow.MAX_NAME_LENGTH
    ):
        return jsonify(None), 404

    flow = get_flow(flow_name)
    if not flow:
        return jsonify(None), 404

    posts = get_public_posts_in_flow_by_page(flow['id'], page, sorting)
    return jsonify(posts)


# -- authentication --

@bp.route('/users', methods=['POST'])
def api_create_user():
    try:
        username = request.json['username']
        password = request.json['password']
    except KeyError:
        return jsonify({'error': 'missing_username_password'}), 400

    username_length = len(username)
    if (
        username_length < User.MIN_NAME_LENGTH
        or username_length > User.MAX_NAME_LENGTH
    ):
        return jsonify({'error': 'wrong_username_length'}), 400

    password_length = len(password)
    if (
        password_length < User.MIN_PASSWORD_LENGTH
        or password_length > User.MAX_PASSWORD_LENGTH
    ):
        return jsonify({'error': 'wrong_password_length'}), 400

    # TODO: validate username with regex

    if is_username_taken(username):
        return jsonify({'error': 'username_already_taken'}), 400

    new_user = create_user(username, password)
    login_user(new_user, remember=True)

    return jsonify({
        'name': new_user.name,
        'created_on': new_user.created_on,
    }), 201


@bp.route('/usernames/<username>')
def api_username_exists(username):
    if is_username_taken(username):
        return '', 204

    return '', 404


@bp.route('/login', methods=['POST'])
def api_login():
    try:
        username = request.json['username']
        password = request.json['password']
    except KeyError:
        return jsonify({'error': 'missing_username_password'}), 400

    username_length = len(username)
    password_length = len(password)
    if (
        username_length < User.MIN_NAME_LENGTH
        or username_length > User.MAX_NAME_LENGTH
        or password_length < User.MIN_PASSWORD_LENGTH
        or password_length > User.MAX_PASSWORD_LENGTH
    ):
        return jsonify({'error': 'incorrect_login'}), 401

    if current_user.is_authenticated:
        # already logged in
        return '', 204

    user = get_user_by_name(username)
    if user is None or not user.check_password(password):
        return jsonify({'error': 'incorrect_login'}), 401

    login_user(user, remember=True)
    return '', 204
