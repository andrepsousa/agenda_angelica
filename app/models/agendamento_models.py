from app.config import db
from app.models.models import Agendamento
from datetime import datetime, timedelta


def list_agendamentos():
    agendamentos = Agendamento.query.all()
    return [agendamento.to_dict() for agendamento in agendamentos]


def agendamento_by_id(agendamento_id):
    agendamento = Agendamento.query.get(agendamento_id)
    if agendamento:
        return agendamento.to_dict()
    raise ValueError("Agendamento não encontrado.")


def criar_agendamento_simples(data):
    if not data.get("cliente_id") or not data.get("servico_id"):
        raise ValueError("O cliente e o serviço são obrigatórios.")

    if not data.get("status", True):
        raise ValueError("O serviço precisa estar ativo.")

    try:
        novo_agendamento = Agendamento(
            cliente_id=data["cliente_id"],
            servico_id=data["servico_id"],
            data_hora=data["data_hora"],
            recorrencia=data.get("recorrencia"),
            status=data.get("status", "ativo"),
            observacoes=data.get("observacoes")  # suporte a observações
        )

        db.session.add(novo_agendamento)
        db.session.commit()
        return novo_agendamento.to_dict()

    except Exception as e:
        db.session.rollback()
        raise ValueError(f"Erro ao realizar agendamento: {e}")


def criar_agendamentos_recorrentes(data):
    try:
        data_hora = data["data_hora"]
        cliente_id = data["cliente_id"]
        servico_id = data["servico_id"]
        status = data.get("status", "ativo")
        num_recorrencias = data.get("num_recorrencias", 1)
        recorrencia = data.get("recorrencia")
        observacoes = data.get("observacoes")

        agendamentos = []
        for i in range(num_recorrencias):
            novo_agendamento = Agendamento(
                cliente_id=cliente_id,
                servico_id=servico_id,
                data_hora=data_hora + timedelta(weeks=i),
                status=status,
                recorrencia=recorrencia,
                observacoes=observacoes
            )
            agendamentos.append(novo_agendamento)

        db.session.add_all(agendamentos)
        db.session.commit()
        return [a.to_dict() for a in agendamentos]

    except Exception as e:
        db.session.rollback()
        raise ValueError(f"Erro ao criar agendamentos recorrentes: {e}")


def atualizar_agendamento(agendamento_id, novo_agendamento):
    agendamento = Agendamento.query.get(agendamento_id)
    if not agendamento:
        raise ValueError("Agendamento não encontrado!")

    agendamento.cliente_id = novo_agendamento.get("cliente_id", agendamento.cliente_id)
    agendamento.servico_id = novo_agendamento.get("servico_id", agendamento.servico_id)
    agendamento.data_hora = novo_agendamento.get("data_hora", agendamento.data_hora)
    agendamento.recorrencia = novo_agendamento.get("recorrencia", agendamento.recorrencia)
    agendamento.status = novo_agendamento.get("status", agendamento.status)
    agendamento.observacoes = novo_agendamento.get("observacoes", agendamento.observacoes)

    try:
        db.session.commit()
        return agendamento.to_dict()
    except Exception as e:
        db.session.rollback()
        raise ValueError(f"Erro ao atualizar agendamento: {e}")


def delete_agendamento(agendamento_id):
    print(f"Tentando acessar agendamento {agendamento_id}")
    agendamento = Agendamento.query.get(agendamento_id)
    
    if not agendamento:
        raise ValueError("Agendamento não encontrado!")

    try:
        agendamento_dict = agendamento.to_dict()
        db.session.delete(agendamento)
        db.session.commit()
        return agendamento_dict
    except Exception as e:
        db.session.rollback()
        raise ValueError(f"Erro ao deletar o agendamento: {e}")