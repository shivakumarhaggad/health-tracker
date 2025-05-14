from flask import Flask
from .routes import routes
from .models import db
from flask_migrate import Migrate
import os

def create_app():
    app = Flask(__name__)
    
    # Configuration
    app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL', 'sqlite:///local_database.db')
    app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'your_secret_key_here')

    db.init_app(app)
    migrate = Migrate(app, db)  # Initialize Flask-Migrate

    app.register_blueprint(routes)

    return app