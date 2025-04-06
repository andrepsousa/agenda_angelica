from app.config import db
from datetime import datetime

class User(db.Model):
    __tablename__ = 'usuarios'
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(100), nullable=False)
    endereco = db.Column(db.String(150),nullable=False )
    telefone = db.Column(db.String(15),nullable=False)
    cpf = db.Column(db.String(11),unique=True, nullable=False)
    data_nascimento = db.Column(db.Date)


class Service(db.Model):
    __tablename__ = 'servicos'
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(255), nullable=False)
    descricao = db.Column(db.Text, nullable=True)
    preco = db.Column(db.Float, nullable=False, default=0.0)
    status = db.Column(db.Boolean, default=True)

    def to_dict(self):
        return {
            'id': self.id,
            'nome': self.nome,
            'descricao': self.descricao,
            'preco': self.preco,
            'status': self.status
        }

    def __repr__(self):
        return f"<Service {self.nome}>"


class Agendamento(db.Model):
    __tablename__ = 'agendamentos'
    id = db.Column(db.Integer, primary_key=True)
    cliente_id = db.Column(db.Integer, db.ForeignKey(
        'usuarios.id'), nullable=False)
    servico_id = db.Column(db.Integer, db.ForeignKey(
        'servicos.id'), nullable=False)
    data_hora = db.Column(db.DateTime, nullable=False)
    recorrencia = db.Column(db.String(20), nullable=True)
    status = db.Column(db.String(20), default='ativo')

    usuario = db.relationship('User', backref='agendamentos')
    servico = db.relationship('Service', backref='agendamentos')

    def to_dict(self):
        return {
            'id': self.id,
            'cliente_id': self.cliente_id,
            'cliente_nome': self.usuario.nome,
            'servico_id': self.servico_id,
            'servico_nome': self.servico.nome,
            'data_hora': self.data_hora,
            'recorrencia': self.recorrencia,
            'status': self.status
        }

    def __repr__(self):
        return (
            f"<Agendamento {self.data_hora} - Recorrência: {self.recorrencia} "
            f"- Status: {self.status}>"
        )
