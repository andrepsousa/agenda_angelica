from app.config import db
from app.models.models import User


def listar_usuarios():
    usuarios = User.query.all()
    usuarios_infos = [{"id": usuario.id,
                       "nome": usuario.nome,
                       "endereco": usuario.endereco,
                       "telefone": usuario.telefone,
                       "cpf": usuario.cpf,
                       "data_nascimento": usuario.data_nascimento}
                      for usuario in usuarios]
    print("Usuários:", usuarios_infos)
    return usuarios_infos


def usuarios_by_id(id_usuario):
    usuario = User.query.get(id_usuario)
    if usuario:
        return {
            "id": usuario.id,
            "nome": usuario.nome,
            "endereco": usuario.endereco,
            "telefone": usuario.telefone,
            "cpf": usuario.cpf,
            "data_nascimento": usuario.data_nascimento
        }
    raise ValueError("Usuario não encontrado.")


def registrar_user(novo_user, cpf, telefone):
    if User.query.filter_by(cpf=cpf).first():
        raise ValueError("Usuário já existe.")
    if User.query.filter_by(telefone=telefone).first():
        raise ValueError("Telefone cadastrado no sistema.")

    novo_user = User(
        nome=novo_user.get("nome"),
        endereco=novo_user.get("endereco"),
        telefone=novo_user.get("telefone"),
        cpf=novo_user.get("cpf"),
        data_nascimento=novo_user.get("data_nascimento")
    )

    db.session.add(novo_user)
    db.session.commit()
    return {"message": "Usuário registrado com sucesso!", "id": novo_user.id}


def atualizar_user(id_usuario, novo_usuario):
    usuario = User.query.get(id_usuario)
    if not usuario:
        raise ValueError("Usuário não cadastrado.")

    print(f"Usuário encontrado: {usuario}")

    usuario.nome = novo_usuario.get("nome", usuario.nome)
    usuario.endereco = novo_usuario.get("endereco", usuario.endereco)
    usuario.telefone = novo_usuario.get("telefone", usuario.telefone)
    usuario.cpf = novo_usuario.get("cpf", usuario.cpf)
    usuario.data_nascimento = novo_usuario.get(
        "data_nascimento", usuario.data_nascimento)

    try:
        db.session.commit()

        usuario_atualizado = {
            "id": usuario.id,
            "nome": usuario.nome,
            "endereco": usuario.endereco,
            "telefone": usuario.telefone,
            "cpf": usuario.cpf,
            "data_nascimento": usuario.data_nascimento
        }

        return usuario_atualizado
    except Exception as e:

        db.session.rollback()
        print(f"Erro ao tentar atualizar usuário: {e}")
        raise ValueError("Erro ao tentar atualizar usuário. Verifique os dados ou tente novamente.")


def deletar_user(id_usuario):
    usuario = User.query.get(id_usuario)

    if not usuario:
        raise ValueError("Usuário não encontrado.")
    
    try:
        usuario_deletado = {
            "id": usuario.id,
            "nome": usuario.nome,
            "endereco": usuario.endereco,
            "telefone": usuario.telefone,
            "cpf": usuario.cpf,
            "data_nascimento": usuario.data_nascimento
        }

        db.session.delete(usuario)
        db.session.commit()

        return usuario_deletado
    
    except Exception as e:
        db.session.rollback()
        print(f"Erro ao tentar excluir usuario: {e}")
        raise e
