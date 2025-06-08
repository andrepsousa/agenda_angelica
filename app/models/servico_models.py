from app.config import db
from app.models.models import Service


def listar_servicos():
    servicos = Service.query.all()
    return [servico.to_dict() for servico in servicos]


def servico_by_id_dict(id):
    servico = Service.query.get(id)
    if not servico:
        raise ValueError("Serviço não encontrado.")
    return servico.to_dict()


def servico_by_id_obj(id):
    servico = Service.query.get(id)
    if not servico:
        raise ValueError("Serviço não encontrado.")
    return servico


def criar_servico(data):
    if not data.get("nome") or not data.get("preco"):
        raise ValueError("O nome e o preço são obrigatórios.")

    novo_servico = Service(
        nome=data["nome"],
        descricao=data.get("descricao", ""),
        preco=data["preco"],
        status=data.get("status", True)  # padrão ativo
    )

    try:
        db.session.add(novo_servico)
        db.session.commit()
        return novo_servico.to_dict()
    except Exception as e:
        db.session.rollback()
        raise ValueError(f"Erro ao criar serviço: {e}")


def atualizar_servico(servico_id, data):
    servico = Service.query.get(servico_id)
    if not servico:
        raise ValueError("Serviço não encontrado.")

    servico.nome = data.get("nome", servico.nome)
    servico.descricao = data.get("descricao", servico.descricao)
    servico.preco = data.get("preco", servico.preco)
    servico.status = data.get("status", servico.status)

    try:
        db.session.commit()
        return servico.to_dict()
    except Exception as e:
        db.session.rollback()
        raise ValueError(f"Erro ao atualizar serviço: {e}")


def deletar_servico(servico_id):
    servico = Service.query.get(servico_id)
    if not servico:
        raise ValueError("Serviço não encontrado.")

    try:
        db.session.delete(servico)
        db.session.commit()
        return servico.to_dict()
    except Exception as e:
        db.session.rollback()
        raise ValueError(f"Erro ao deletar serviço: {e}")
