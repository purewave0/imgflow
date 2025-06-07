import random
import string

from app.extensions import db
from app.models.util import utcnow


_post_id_charset = string.ascii_letters + string.digits # a-z A-Z 0-9

def _random_post_id():
    return ''.join(
        random.choices(_post_id_charset, k=Post.POST_ID_LENGTH)
    )


class Post(db.Model):
    __tablename__ = 'Post'
    POST_ID_LENGTH = 8
    MAX_TITLE_LENGTH = 128
    MAX_FLOWS_PER_POST = 3
    id = db.Column(db.Integer, primary_key=True)
    post_id = db.Column(db.String(POST_ID_LENGTH), unique=True, nullable=False)
    title = db.Column(db.String(MAX_TITLE_LENGTH), nullable=True)
    media = db.relationship('PostMedia', backref='post')
    thumbnail_url = db.Column(db.String(128), nullable=False)
    score = db.Column(db.Integer, nullable=False)
    comments = db.relationship('PostComment', backref='post')
    comment_count = db.Column(db.Integer, nullable=False)
    views = db.Column(db.Integer, nullable=False)
    created_on = db.Column(db.DateTime, server_default=utcnow())
    updated_on = db.Column(db.DateTime, onupdate=utcnow())
    is_public = db.Column(db.Boolean, nullable=False, default=False)
    flows = db.relationship('Flow', secondary='PostFlow', backref='posts')

    def __init__(self, title, media, thumbnail_url, is_public, flows):
        self.post_id = _random_post_id()
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
    __tablename__ = 'PostMedia'
    id = db.Column(db.Integer, primary_key=True)
    media_url = db.Column(db.String(128), nullable=False)
    description = db.Column(db.Text, nullable=True)
    post_id = db.Column(db.String(Post.POST_ID_LENGTH), db.ForeignKey('Post.post_id'))

    def __repr__(self):
        return f'<Media media_url:"{self.media_url}" id:{self.id} post_id:{self.post_id}>'


class PostComment(db.Model):
    __tablename__ = 'PostComment'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('User.id'))
    content = db.Column(db.Text, nullable=False)
    parent_id = db.Column(db.Integer, nullable=True)
    reply_count = db.Column(db.Integer, nullable=False)
    score = db.Column(db.Integer, nullable=False)
    created_on = db.Column(db.DateTime, server_default=utcnow())
    post_id = db.Column(db.String(Post.POST_ID_LENGTH), db.ForeignKey('Post.post_id'))

    def __init__(self, user_id, content, parent_id, post_id):
        self.user_id = user_id
        self.content = content
        self.parent_id = parent_id
        self.reply_count = 0
        self.score = 0
        self.post_id = post_id

    def __repr__(self):
        return f'<Comment id:{self.id} post_id:{self.post_id} score:{self.score}'


class PostUpvote(db.Model):
    __tablename__ = 'PostUpvote'
    post_id = db.Column(db.String(Post.POST_ID_LENGTH), db.ForeignKey('Post.post_id'), primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('User.id'), primary_key=True)

    def __init__(self, post_id, user_id):
        self.post_id = post_id
        self.user_id = user_id

    def __repr__(self):
        return f'<post_id:{self.post_id} upvoted by user_id:{self.user_id}>'


class CommentUpvote(db.Model):
    __tablename__ = 'CommentUpvote'
    comment_id = db.Column(db.Integer, db.ForeignKey('PostComment.id'), primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('User.id'), primary_key=True)

    def __init__(self, comment_id, user_id):
        self.comment_id = comment_id
        self.user_id = user_id

    def __repr__(self):
        return f'<comment_id:{self.comment_id} upvoted by user_id:{self.user_id}>'


class Flow(db.Model):
    __tablename__ = 'Flow'
    MIN_NAME_LENGTH = 2
    MAX_NAME_LENGTH = 50
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(MAX_NAME_LENGTH), unique=True, nullable=False, index=True)
    post_count = db.Column(db.Integer, nullable=False)

    def __init__(self, name):
        self.name = name
        self.post_count = 0


class PostFlow(db.Model):
    __tablename__ = 'PostFlow'
    post_id = db.Column(db.Integer, db.ForeignKey('Post.id'), primary_key=True)
    flow_id = db.Column(db.Integer, db.ForeignKey('Flow.id'), primary_key=True)
