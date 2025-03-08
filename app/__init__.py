from flask import Flask
from flask_jwt_extended import JWTManager
from flask_sqlalchemy import SQLAlchemy
import os
from datetime import timedelta
from dotenv import load_dotenv


load_dotenv()
db = SQLAlchemy()
jwt = JWTManager()


def create_app():
    app = Flask(__name__)

    app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(minutes=10)
    app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL')
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['JWT_SECRET_KEY'] = os.getenv('JWT_SECRET_KEY')

    app.config['SECRET_KEY'] = os.getenv('SECRET_KEY')

    db.init_app(app)
    print("DATABASE_URL:", repr(os.getenv("DATABASE_URL")))

    jwt.init_app(app)

    from app.routes.routes import main
    app.register_blueprint(main)

    return app
