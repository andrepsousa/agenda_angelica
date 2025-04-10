from app.config import SQLALCHEMY_DATABASE_URI, SQLALCHEMY_TRACK_MODIFICATIONS
from flask import Flask,redirect,url_for
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
    app.config['SQLALCHEMY_DATABASE_URI'] = SQLALCHEMY_DATABASE_URI
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = SQLALCHEMY_TRACK_MODIFICATIONS
    app.config['JWT_SECRET_KEY'] = 'chave-jwt'

    db.init_app(app)
    jwt.init_app(app)
    
    app.register_blueprint(main_bp)
    app.register_blueprint(bp_agendamentos)
    app.register_blueprint(servicos_bp)
    app.register_blueprint(usuarios_bp)

    @app.route('/')
    def index():
        return redirect(url_for('main_bp.index'))
    return app
