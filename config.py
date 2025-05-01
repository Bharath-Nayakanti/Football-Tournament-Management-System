import os

BASE_DIR = os.path.abspath(os.path.dirname(__file__))

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'your-secret-key'  # Replace 'your-secret-key' with a real one
    SQLALCHEMY_DATABASE_URI = 'sqlite:///' + os.path.join(BASE_DIR, 'instance', 'db.sqlite3')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
