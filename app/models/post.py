from sqlalchemy.sql import expression, case
from sqlalchemy.ext.compiler import compiles
from sqlalchemy.types import Numeric

from app.extensions import db


class utcnow(expression.FunctionElement):
    type = db.DateTime()
    inherit_cache = True

@compiles(utcnow, 'mariadb')
def pg_utcnow(element, compiler, **kw):
    return "UTC_TIMESTAMP"


class Post(db.Model):
    __tablename__ = 'Post'
    POST_ID_LENGTH = 8
    id = db.Column(db.Integer, primary_key=True)
    post_id = db.Column(db.String(POST_ID_LENGTH), unique=True, nullable=False)
    title = db.Column(db.String(128), nullable=True)
    media = db.relationship('PostMedia', backref='post')
    thumbnail_url = db.Column(db.String(128), nullable=False)
    score = db.Column(db.Integer, nullable=False)
    comments = db.relationship('PostComment', backref='post')
    comment_count = db.Column(db.Integer, nullable=False)
    views = db.Column(db.Integer, nullable=False)
    created_on = db.Column(db.DateTime, server_default=utcnow())
    updated_on = db.Column(db.DateTime, onupdate=utcnow())

    def __repr__(self):
        return f'<Post title:"{self.title}" id:{self.id} post_id:{self.post_id}>'


class PostMedia(db.Model):
    __tablename__ = 'PostMedia'
    id = db.Column(db.Integer, primary_key=True)
    media_url = db.Column(db.String(128), nullable=False)
    description = db.relationship('PostDescription', backref='media', uselist=False)
    post_id = db.Column(db.String(Post.POST_ID_LENGTH), db.ForeignKey('Post.post_id'))

    def __repr__(self):
        return f'<Media media_url:"{self.media_url}" id:{self.id} post_id:{self.post_id}>'


class PostDescription(db.Model):
    __tablename__ = 'PostDescription'
    id = db.Column(db.Integer, primary_key=True)
    content = db.Column(db.Text, nullable=False)
    media_id = db.Column(db.Integer, db.ForeignKey('PostMedia.id'))

    def __repr__(self):
        return f'<Description id:{self.id} media_id:{self.media_id}>'


class PostComment(db.Model):
    __tablename__ = 'PostComment'
    id = db.Column(db.Integer, primary_key=True)
    content = db.Column(db.Text, nullable=False)
    score = db.Column(db.Integer, nullable=False)
    created_on = db.Column(db.DateTime, server_default=utcnow())
    # TODO: replies
    post_id = db.Column(db.String(Post.POST_ID_LENGTH), db.ForeignKey('Post.post_id'))

    def __repr__(self):
        return f'<Comment id:{self.id} post_id:{self.post_id} score:{self.score}'
