from flask import Flask

from config import Config
from app.extensions import db


def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)

    # Extensions
    db.init_app(app)
    with app.app_context():
        from app.models.post import Post, PostMedia, PostDescription, PostComment
        db.create_all()

    # Blueprints
    from app.api import bp as api_bp
    app.register_blueprint(api_bp, url_prefix='/api')

    from app.main import bp as main_bp
    app.register_blueprint(main_bp)

    from app.post import bp as post_bp
    app.register_blueprint(post_bp, url_prefix='/post')

    from app.contact import bp as contact_bp
    app.register_blueprint(contact_bp, url_prefix='/contact')

    from app.about import bp as about_bp
    app.register_blueprint(about_bp, url_prefix='/about')


    @app.route('/test/')
    def test_page():
        return '<h1>Hello, World!</h1> <p>Hello</p>'

    return app
