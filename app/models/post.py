from app.extensions import db


class Post(db.Model):
    __tablename__ = 'Post'
    id = db.Column(db.Integer, primary_key=True)
    post_id = db.Column(db.String(8), unique=True, nullable=False)
    title = db.Column(db.String(128), nullable=True)
    media = db.relationship('PostMedia', backref='post')
    score = db.Column(db.Integer, nullable=False)
    comments = db.relationship('PostComment', backref='post')
    views = db.Column(db.Integer, nullable=False)

    def __repr__(self):
        return f'<Post "{self.title}" of ID {self.id}>'


class PostMedia(db.Model):
    __tablename__ = 'PostMedia'
    id = db.Column(db.Integer, primary_key=True)
    media_url = db.Column(db.String(128), nullable=False)
    description = db.relationship('PostDescription', backref='media')
    post_id = db.Column(db.Integer, db.ForeignKey('Post.id'))

    def __repr__(self):
        return f'<Media at {self.media_url}, in post {self.post_id}>'


class PostDescription(db.Model):
    __tablename__ = 'PostDescription'
    id = db.Column(db.Integer, primary_key=True)
    content = db.Column(db.Text, nullable=False)
    media_id = db.Column(db.Integer, db.ForeignKey('PostMedia.id'))

    def __repr__(self):
        return f'<Description in media {self.media_id}>'


class PostComment(db.Model):
    __tablename__ = 'PostComment'
    id = db.Column(db.Integer, primary_key=True)
    content = db.Column(db.Text, nullable=False)
    score = db.Column(db.Integer, nullable=False)
    # TODO: replies
    post_id = db.Column(db.Integer, db.ForeignKey('Post.id'))

    def __repr__(self):
        return f'<Comment in post {self.post_id}'
