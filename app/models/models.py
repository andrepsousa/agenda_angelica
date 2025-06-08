from app.config import db
from datetime import datetime, timedelta, timezone
from flask_login import UserMixin
import pytz
import logging


class User(db.Model, UserMixin):
    __tablename__ = "usuarios"

    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(150), nullable=False)
    endereco = db.Column(db.String(255))
    telefone = db.Column(db.String(20), unique=True, nullable=False)
    cpf = db.Column(db.String(14), unique=True, nullable=False)
    data_nascimento = db.Column(db.Date)
    role = db.Column(db.String(20), nullable=False, default='cliente')

    codigo_verificacao = db.Column(db.String(6), nullable=True)
    validade_codigo = db.Column(db.DateTime, nullable=True)

    def gerar_codigo_verificacao(self, codigo, minutos_validade=5):
        self.codigo_verificacao = codigo
        # Usar timezone de São Paulo para validação
        tz = pytz.timezone('America/Sao_Paulo')
        self.validade_codigo = datetime.now(tz) + timedelta(minutes=minutos_validade)

    def verificar_codigo(self, codigo_digitado):
        if not self.codigo_verificacao or not self.validade_codigo:
            return False

        # Usar timezone de São Paulo para validação
        tz = pytz.timezone('America/Sao_Paulo')
        now = datetime.now(tz)
        
        # Garantir que validade_codigo seja aware com timezone de São Paulo
        if self.validade_codigo.tzinfo is None:
            self.validade_codigo = tz.localize(self.validade_codigo)
        elif self.validade_codigo.tzinfo != tz:
            self.validade_codigo = self.validade_codigo.astimezone(tz)

        logging.debug(
            f'DEBUG: Usuário: {self.nome}, código esperado: {self.codigo_verificacao}, '
            f'código recebido: {codigo_digitado}, validade: {self.validade_codigo}, '
            f'agora: {now}'
        )

        if (
            self.codigo_verificacao == codigo_digitado
            and self.validade_codigo > now
        ):
            return True

        return False

    def to_dict(self):
        return {
            "id": self.id,
            "nome": self.nome,
            "endereco": self.endereco,
            "telefone": self.telefone,
            "cpf": self.cpf,
            "data_nascimento": self.data_nascimento.strftime("%d-%m-%Y") if
            self.data_nascimento else None,
            "role": self.role
        }

    def __repr__(self):
        return f"<User {self.nome}, Role: {self.role}>"


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
    cliente_id = db.Column(db.Integer, db.ForeignKey('usuarios.id', ondelete='CASCADE'), nullable=False)
    servico_id = db.Column(db.Integer, db.ForeignKey('servicos.id', ondelete='CASCADE'), nullable=False)
    data_hora = db.Column(db.DateTime, nullable=False)
    status = db.Column(db.String(30), default='confirmado')  # confirmado, cancelado, alteracao_pendente, cancelamento_pendente
    observacoes = db.Column(db.Text)
    motivo_alteracao = db.Column(db.Text)
    motivo_cancelamento = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    recorrencia = db.Column(db.String(20))  # semanal, quinzenal, mensal
    codigo_verificacao = db.Column(db.String(6))
    validade_codigo = db.Column(db.DateTime)

    # Relacionamentos
    cliente = db.relationship('User', backref=db.backref('agendamentos', lazy=True))
    servico = db.relationship('Service', backref=db.backref('agendamentos', lazy=True))

    def gerar_codigo_verificacao(self, codigo):
        """Gera um código de verificação para o agendamento"""
        self.codigo_verificacao = codigo
        self.validade_codigo = datetime.now(pytz.timezone('America/Sao_Paulo')) + timedelta(minutes=5)
        self.status = 'pendente'

    def verificar_codigo(self, codigo):
        """Verifica se o código é válido e atualiza o status do agendamento"""
        if not self.codigo_verificacao or not self.validade_codigo:
            return False

        # Garante que a validade_codigo está no timezone correto
        if not self.validade_codigo.tzinfo:
            self.validade_codigo = pytz.timezone('America/Sao_Paulo').localize(self.validade_codigo)

        agora = datetime.now(pytz.timezone('America/Sao_Paulo'))

        if agora > self.validade_codigo:
            return False

        if self.codigo_verificacao == codigo:
            self.status = 'confirmado'
            self.codigo_verificacao = None
            self.validade_codigo = None
            return True

        return False

    def to_dict(self):
        return {
            'id': self.id,
            'cliente_id': self.cliente_id,
            'servico_id': self.servico_id,
            'data_hora': self.data_hora.isoformat(),
            'status': self.status,
            'observacoes': self.observacoes,
            'recorrencia': self.recorrencia
        }

    def __repr__(self):
        return (
            f"<Agendamento {self.data_hora} - Recorrência: {self.recorrencia} "
            f"- Status: {self.status} - Obs: {self.observacoes}>"
        )

    def get_status_formatado(self):
        status_map = {
            'confirmado': 'Confirmado',
            'cancelado': 'Cancelado',
            'alteracao_pendente': 'Alteração Pendente',
            'cancelamento_pendente': 'Cancelamento Pendente'
        }
        return status_map.get(self.status, self.status)
