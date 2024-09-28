from flask import Flask

from config import Config


def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)

    # Blueprints
    from app.main import bp as main_bp
    app.register_blueprint(main_bp)

    from app.contact import bp as contact_bp
    app.register_blueprint(contact_bp, url_prefix='/contact')

    from app.about import bp as about_bp
    app.register_blueprint(about_bp, url_prefix='/about')

    @app.route('/test/')
    def test_page():
        return '<h1>Hello, World!</h1> <p>Hello</p>'

    return app
