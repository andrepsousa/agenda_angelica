from flask_sqlalchemy import SQLAlchemy
from app import db


class User(db.Model):
    __tablename__ = 'usuarios'
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(50), nullable=False)
    endereco = db.Column(db.String(150))
    telefone = db.Column(db.String(15))
    cpf = db.Column(db.String(11))
    data_nascimento = db.Column(db.Date)
    