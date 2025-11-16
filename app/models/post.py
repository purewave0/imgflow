from collections.abc import Iterable
import random
import string

from app.extensions import db
from app.models.util import utcnow


_post_id_charset = string.ascii_letters + string.digits # a-z A-Z 0-9

def _random_post_id() -> str:
    """Return a new random post ID with `Post.POST_ID_LENGTH` characters."""
    return ''.join(
        random.choices(_post_id_charset, k=Post.POST_ID_LENGTH)
    )


class Post(db.Model):
    """A post with media."""
    __tablename__ = 'Post'
    POST_ID_LENGTH = 8
    MAX_TITLE_LENGTH = 128
    MAX_FLOWS_PER_POST = 3
    id = db.Column(db.Integer, primary_key=True)
    post_id = db.Column(db.String(POST_ID_LENGTH), unique=True, nullable=False)
    """The post ID string used in URLs."""
    user_id = db.Column(db.Integer, db.ForeignKey('User.id'), nullable=True)
    """The ID of the user who made the post."""
    title = db.Column(db.String(MAX_TITLE_LENGTH), nullable=True)
    """The post title (optional)."""
    media = db.relationship('PostMedia', backref='post')
    """One or more media files."""
    thumbnail_url = db.Column(db.String(128), nullable=False)
    """The URL of the auto-generated thumbnail, based on the 1st media item."""
    score = db.Column(db.Integer, nullable=False)
    """How many times the post was upvoted."""
    comments = db.relationship('PostComment', backref='post')
    """Comments (including replies) on the post."""
    comment_count = db.Column(db.Integer, nullable=False)
    """How many times users wrote comments or replies on the post."""
    views = db.Column(db.Integer, nullable=False)
    """How many times the post was viewed."""
    created_on = db.Column(db.DateTime, server_default=utcnow())
    """When the post was made."""
    updated_on = db.Column(db.DateTime, onupdate=utcnow())
    """When the post was last updated."""
    is_public = db.Column(db.Boolean, nullable=False, default=False)
    """Whether the post is public (shows up on the feed) or private (only accessible via
    the URL)."""
    flows = db.relationship('Flow', secondary='PostFlow', backref='posts')
    """The flows this post belongs to."""

    def __init__(
        self,
        user_id: int | None,
        title: str | None,
        media: Iterable['PostMedia'],
        thumbnail_url: str,
        is_public: bool,
        flows: Iterable['Flow']
    ):
        self.post_id = _random_post_id()
        self.user_id = user_id
        self.title = title
        self.media = media
        self.thumbnail_url = thumbnail_url
        self.score = 0
        self.comments = []
        self.comment_count = 0
        self.views = 0
        self.is_public = is_public
        self.flows = flows

    def __repr__(self):
        return f'<Post title:"{self.title}" id:{self.id} post_id:{self.post_id}>'


class PostMedia(db.Model):
    """A media item belonging to a post."""
    __tablename__ = 'PostMedia'
    id = db.Column(db.Integer, primary_key=True)
    media_url = db.Column(db.String(128), nullable=False)
    """The URL of the media file."""
    description = db.Column(db.Text, nullable=True)
    """An optional description."""
    post_id = db.Column(db.String(Post.POST_ID_LENGTH), db.ForeignKey('Post.post_id'))
    """The ID of the post this media item belongs to."""

    def __repr__(self):
        return f'<Media media_url:"{self.media_url}" id:{self.id} post_id:{self.post_id}>'


class PostComment(db.Model):
    """A comment (or a reply to one) on a post."""
    __tablename__ = 'PostComment'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('User.id'))
    """The ID of the user who wrote the comment."""
    content = db.Column(db.Text, nullable=False)
    """The content of the post, supporting Markdown."""
    parent_id = db.Column(db.Integer, nullable=True)
    """If None, this is a top-level comment; else, it's a reply to the comment of the
    given ID."""
    reply_count = db.Column(db.Integer, nullable=False)
    """How many times this comment was replied to."""
    score = db.Column(db.Integer, nullable=False)
    """How many times the comment was upvoted."""
    created_on = db.Column(db.DateTime, server_default=utcnow())
    """When the comment was written."""
    post_id = db.Column(db.String(Post.POST_ID_LENGTH), db.ForeignKey('Post.post_id'))
    """The post this comment belongs to."""

    def __init__(
        self,
        user_id: int,
        content: str,
        parent_id: int | None,
        post_id: str
    ):
        self.user_id = user_id
        self.content = content
        self.parent_id = parent_id
        self.reply_count = 0
        self.score = 0
        self.post_id = post_id

    def __repr__(self):
        return f'<Comment id:{self.id} post_id:{self.post_id} score:{self.score}'


class PostUpvote(db.Model):
    """An upvote on a post."""
    __tablename__ = 'PostUpvote'
    post_id = db.Column(
        db.String(Post.POST_ID_LENGTH), db.ForeignKey('Post.post_id'), primary_key=True
    )
    """The ID of the upvoted post."""
    user_id = db.Column(db.Integer, db.ForeignKey('User.id'), primary_key=True)
    """The ID of the user who upvoted the post."""

    def __init__(self, post_id: str, user_id: int):
        self.post_id = post_id
        self.user_id = user_id

    def __repr__(self):
        return f'<post_id:{self.post_id} upvoted by user_id:{self.user_id}>'


class CommentUpvote(db.Model):
    """An upvote on a comment."""
    __tablename__ = 'CommentUpvote'
    comment_id = db.Column(
        db.Integer, db.ForeignKey('PostComment.id'), primary_key=True
    )
    """The ID of the upvoted comment."""
    user_id = db.Column(db.Integer, db.ForeignKey('User.id'), primary_key=True)
    """The ID of the user who upvoted the comment."""

    def __init__(self, comment_id: int, user_id: int):
        self.comment_id = comment_id
        self.user_id = user_id

    def __repr__(self):
        return f'<comment_id:{self.comment_id} upvoted by user_id:{self.user_id}>'


class Flow(db.Model):
    """A named grouping of posts with similar topics."""
    __tablename__ = 'Flow'
    MIN_NAME_LENGTH = 2
    MAX_NAME_LENGTH = 50
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(MAX_NAME_LENGTH), unique=True, nullable=False, index=True)
    """The name of the flow."""
    post_count = db.Column(db.Integer, nullable=False)
    """How many posts belong to this flow."""

    def __init__(self, name: str):
        self.name = name
        self.post_count = 0


class PostFlow(db.Model):
    """The association between posts and flows."""
    __tablename__ = 'PostFlow'
    post_id = db.Column(db.Integer, db.ForeignKey('Post.id'), primary_key=True)
    """The ID of the post in the flow."""
    flow_id = db.Column(db.Integer, db.ForeignKey('Flow.id'), primary_key=True)
    """The ID of the flow the post belongs to."""
