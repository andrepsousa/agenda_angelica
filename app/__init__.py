from flask import Flask,redirect,url_for
from flask_migrate import Migrate 
from flask_sqlalchemy import SQLAlchemy
from flask_jwt_extended import JWTManager
from app.routes.main_routes import main_bp
from app.routes.agendamentos_routes import bp_agendamentos
from app.routes.servicos_routes import servicos_bp
from app.routes.usuarios_routes import usuarios_bp
from app.routes.auth_routes import auth_bp
from app.config import db, jwt
from dotenv import load_dotenv
import os

load_dotenv()

def create_app():
    app = Flask(__name__)

    app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL')
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['JWT_SECRET_KEY'] = os.getenv('JWT_SECRET_KEY')
    app.config['SECRET_KEY'] = os.getenv('SECRET_KEY')

    db.init_app(app)
    jwt.init_app(app)

    migrate = Migrate(app, db)
    
    app.register_blueprint(main_bp)
    app.register_blueprint(bp_agendamentos)
    app.register_blueprint(servicos_bp)
    app.register_blueprint(usuarios_bp)
    app.register_blueprint(auth_bp)

    @app.route('/')
    def index():
        return redirect(url_for('main_bp.index'))
    return app
