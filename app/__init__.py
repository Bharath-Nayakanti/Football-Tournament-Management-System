from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from config import Config
from flask_migrate import Migrate

# Initialize the db object
db = SQLAlchemy()
migrate = Migrate()

def create_app():
    app = Flask(__name__, instance_relative_config=True)
    app.config.from_object(Config)

    # Initialize the db with the app
    db.init_app(app)
    migrate.init_app(app, db)

    # Register the blueprint
    from .routes import bp
    app.register_blueprint(bp)

    return app
