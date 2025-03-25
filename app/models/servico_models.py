from app import db
from app.models.models import Service


def listar_servicos():
    servicos = Service.query.all()
    result = [servico.to_dict() for servico in servicos]
    print("Serviços:", result)
    return result


def servicos_by_id(servico_id):
    servico = Service.query.get(servico_id)
    if servico:
        return servico.to_dict()
    raise ValueError("Serviço não encontrado.")


def criar_servico(data):
    if not data.get("nome") or not data.get("preco"):
        raise ValueError("O nome e o preço são obrigatórios.")
    if "status" not in data:
        data["status"] = True
    novo_servico = Service(
        nome=data["nome"],
        descricao=data.get("descricao", ""),
        preco=data["preco"],
        status=data["status"]
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


def delete_servico(servico_id):
    servico = Service.query.get(servico_id)
    if not servico:
        raise ValueError("Serviço não encontrado.")

    try:
        db.session.delete(servico)
        db.session.commit()
        return servico.to_dict()
    except Exception as e:
        db.session.rollback()
        raise ValueError(f"Erro ao deletar derviço: {e}")
