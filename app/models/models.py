from app import db
from datetime import datetime


class Service(db.Model):
    __tablename__ = 'servicos'
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(255), nullable=False)
    descricao = db.Column(db.Text, nullable=True)
    preco = db.Column(db.Float, nullable=False, default=0.0)
    status = db.Column(db.Boolean, default=True)

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

    def __repr__(self):
        return (
            f"<Agendamento {self.data_hora} - Recorrência: {self.recorrencia} "
            f"- Status: {self.status}>"
        )
