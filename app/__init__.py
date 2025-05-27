from datetime import datetime, date

from flask import Flask
from flask.json.provider import DefaultJSONProvider
from flask_login import LoginManager

from config import Config
from app.extensions import db


# Serialize date(time)s to ISO strings.
class UpdatedJSONProvider(DefaultJSONProvider):
    def default(self, o):
        if isinstance(o, (date, datetime)):
            return o.isoformat() + 'Z' # Z = UTC timezone
        return super().default(o)


def create_app(config_class=Config):
    app = Flask(__name__)
    app.json = UpdatedJSONProvider(app)
    app.config.from_object(config_class)

    # Extensions
    db.init_app(app)
    login_manager = LoginManager(app)

    with app.app_context():
        from app.models.post import Post, PostMedia, PostComment, Flow, PostFlow
        from app.models.user import User
        db.create_all()

        @login_manager.user_loader
        def load_user(user_id):
            user = db.session.execute(
                    db.select(User).where(User.id == int(user_id))
                ).scalar_one_or_none()
            return user

    # Blueprints
    from app.api import bp as api_bp
    app.register_blueprint(api_bp, url_prefix='/api')

    from app.main import bp as main_bp
    app.register_blueprint(main_bp)

    from app.search import bp as search_bp
    app.register_blueprint(search_bp, url_prefix='/search')

    from app.posts import bp as posts_bp
    app.register_blueprint(posts_bp, url_prefix='/posts')

    from app.upload import bp as upload_bp
    app.register_blueprint(upload_bp, url_prefix='/upload')

    from app.flows import bp as flows_bp
    app.register_blueprint(flows_bp, url_prefix='/flows')


    return app
