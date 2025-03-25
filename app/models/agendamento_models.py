from app import db
from app.models.models import Agendamento
from datetime import datetime, timedelta


def list_agendamentos():
    agendamentos = Agendamento.query.all()
    result = [agendamento.to_dict() for agendamento in agendamentos]
    print("Agendamentos:", result)
    return result


def agendamento_by_id(agendamento_id):
    agendamento = Agendamento.query.get(agendamento_id)
    if agendamento:
        return agendamento.to_dict()
    raise ValueError("Agendamento não encontrado.")


def criar_agendamento_simples(data):
    if not data.get("cliente_id") or not data.get("servico_id"):
        raise ValueError("O cliente e o serviço são obrigatórios.")
    if data.get("status") != "ativo":
        raise ValueError("O serviço precisa estar ativo.")
    novo_agendamento = Agendamento(
        cliente_id=data["cliente_id"],
        servico_id=data["servico_id"],
        data_hora=data["data_hora"],
        recorrencia=data["recorrencia"],
        status=data["status"]
    )

    try:
        db.session.add(novo_agendamento)
        db.session.commit()
        return novo_agendamento
    except Exception as e:
        db.session.rollback()
        raise ValueError(f'Erro ao realizar agendamento: {e}')


def criar_agendamentos_recorrentes(data):
    if not data.get("cliente_id") or not data.get("servico_id"):
        raise ValueError("O cliente e o serviço são obrigatórios.")
    if data.get("status") != "ativo":
        raise ValueError("O serviço precisa estar ativo.")
    data_hora = datetime.strptime(data["data_hora"], "%Y-%m-%d %H:%M:%S")
    recorrencia = data.get("recorrencia")
    repeticoes = int(data.get("repeticoes", 1))

    agendamentos_criados = []
    for i in range(repeticoes):
        novo_agendamento = Agendamento(
            cliente_id=data["cliente_id"],
            servico_id=data["servico_id"],
            data_hora=data_hora +
            timedelta(weeks=i) if recorrencia == "semanal" else data_hora,
            recorrencia=recorrencia,
            status=data["status"]
        )
        db.session.add(novo_agendamento)
        agendamentos_criados.append(novo_agendamento)

    try:
        db.session.commit()
        return [agendamento.to_dict() for agendamento in agendamentos_criados]
    except Exception as e:
        db.session.rollback()
        raise ValueError(f"Erro ao criar agendamentos recorrentes: {e}")


def atualizar_agendamento(agendamento_id, novo_agendamento):
    agendamento = Agendamento.query.get(agendamento_id)
    if not agendamento:
        raise ValueError("Agendamento não encontrado!")

    print(f"Agendamento encontrado: {agendamento}")

    agendamento.cliente_id = novo_agendamento.get(
        "cliente_id", agendamento.cliente_id)
    agendamento.servico_id = novo_agendamento.get(
        "servico_id", agendamento.servico_id)
    agendamento.data_hora = novo_agendamento.get(
        "data_hora", agendamento.data_hora)
    agendamento.recorrencia = novo_agendamento.get(
        "recorrencia", agendamento.recorrencia)
    agendamento.status = novo_agendamento.get(
        "status", agendamento.status)

    try:
        db.session.commit()
        return agendamento
    except Exception as e:
        db.session.rollback()
        raise ValueError(f"Erro ao atualizar agendamento: {e}")


def delete_agendamento(agendamento_id):
    agendamento = Agendamento.query.get(agendamento_id)
    if not agendamento:
        raise ValueError("Agendamento não encontrado!")
    try:
        db.session.delete(agendamento)
        db.session.commit()
        return agendamento
    except Exception as e:
        db.session.rollback()
        raise ValueError(f"Erro ao deletar o agendamento: {e}")
