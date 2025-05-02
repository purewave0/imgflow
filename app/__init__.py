from datetime import datetime, date

from flask import Flask
from flask.json.provider import DefaultJSONProvider

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
    with app.app_context():
        from app.models.post import Post, PostMedia, PostComment, Flow, PostFlow
        db.create_all()

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

    from app.contact import bp as contact_bp
    app.register_blueprint(contact_bp, url_prefix='/contact')

    from app.about import bp as about_bp
    app.register_blueprint(about_bp, url_prefix='/about')


    @app.route('/test/')
    def test_page():
        return '<h1>Hello, World!</h1> <p>Hello</p>'

    return app
