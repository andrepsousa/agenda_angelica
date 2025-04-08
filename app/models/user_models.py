from app.config import db
from app.models.models import User
from datetime import datetime


def listar_usuarios():
    usuarios = User.query.all()
    return [usuario.to_dict() for usuario in usuarios]


def usuario_by_id(id_usuario):
    usuario = User.query.get(id_usuario)
    if usuario:
        return usuario.to_dict()
    raise ValueError("Usuário não encontrado.")


def criar_usuario(data):

    if User.query.filter_by(cpf=data.get("cpf")).first():
        raise ValueError("CPF já cadastrado.")
    if User.query.filter_by(telefone=data.get("telefone")).first():
        raise ValueError("Telefone já cadastrado.")

    # Converte a data de nascimento para objeto date
    data_nasc = datetime.strptime(data.get("data_nascimento"), "%Y-%m-%d").date()

    novo_usuario = User(
        nome=data.get("nome"),
        endereco=data.get("endereco"),
        telefone=data.get("telefone"),
        cpf=data.get("cpf"),
        data_nascimento=data_nasc
    )

    try:
        db.session.add(novo_usuario)
        db.session.commit()
        return {"message": "Usuário registrado com sucesso!", "id": novo_usuario.id}
    except Exception as e:
        db.session.rollback()
        raise ValueError(f"Erro ao registrar usuário: {e}")


def atualizar_usuario(id_usuario, data):
    usuario = User.query.get(id_usuario)
    if not usuario:
        raise ValueError("Usuário não encontrado.")

    usuario.nome = data.get("nome", usuario.nome)
    usuario.endereco = data.get("endereco", usuario.endereco)
    usuario.telefone = data.get("telefone", usuario.telefone)
    usuario.cpf = data.get("cpf", usuario.cpf)
    usuario.data_nascimento = data.get("data_nascimento", usuario.data_nascimento)

    try:
        db.session.commit()
        return usuario.to_dict()
    except Exception as e:
        db.session.rollback()
        raise ValueError(f"Erro ao atualizar usuário: {e}")


def deletar_usuario(id_usuario):
    usuario = User.query.get(id_usuario)
    if not usuario:
        raise ValueError("Usuário não encontrado.")

    try:
        usuario_dict = usuario.to_dict()
        db.session.delete(usuario)
        db.session.commit()
        return usuario_dict
    except Exception as e:
        db.session.rollback()
        raise ValueError(f"Erro ao deletar usuário: {e}")