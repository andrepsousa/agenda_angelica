from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_jwt_extended import JWTManager
from app.routes.main_routes import main_bp
from app.routes.agendamentos_routes import bp_agendamentos
from app.routes.servicos_routes import servicos_bp
from app.routes.usuarios_routes import usuarios_bp
from app.config import db, jwt

def create_app():
    app = Flask(__name__)

    # Configurações
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///db.sqlite3'
    app.config['SECRET_KEY'] = 'minha-chave-secreta'
    app.config['JWT_SECRET_KEY'] = 'chave-jwt'

    db.init_app(app)
    jwt.init_app(app)
    
    app.register_blueprint(main_bp)
    app.register_blueprint(bp_agendamentos)
    app.register_blueprint(servicos_bp)
    app.register_blueprint(usuarios_bp)

    return app
