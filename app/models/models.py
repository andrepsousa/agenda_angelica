from flask_sqlalchemy import SQLAlchemy
from app import db


class User(db.Model):
    __tablename__ = 'usuarios'
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(100), nullable=False)
    endereco = db.Column(db.String(150),nullable=False )
    telefone = db.Column(db.String(15),nullable=False)
    cpf = db.Column(db.String(11),unique=True, nullable=False)
    data_nascimento = db.Column(db.Date)
