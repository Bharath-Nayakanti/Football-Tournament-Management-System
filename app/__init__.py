from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from config import Config

# Initialize the db object
db = SQLAlchemy()

def create_app():
    app = Flask(__name__, instance_relative_config=True)
    app.config.from_object(Config)

    # Initialize the db with the app
    db.init_app(app)

    # Register the blueprint
    from .routes import bp
    app.register_blueprint(bp)

    return app
