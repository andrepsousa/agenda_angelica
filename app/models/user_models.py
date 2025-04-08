from app.config import db
from app.models.models import User
from datetime import datetime
import re


def listar_usuarios():
    usuarios = User.query.all()
    return [usuario.to_dict() for usuario in usuarios]


def usuario_by_id(id_usuario):
    usuario = User.query.get(id_usuario)
    if usuario:
        return usuario.to_dict()
    raise ValueError("Usuário não encontrado.")


def criar_usuario(data):
    erros = {}

    # Verificações
    nome = data.get("nome", "").strip()
    telefone = data.get("telefone", "").strip()
    cpf = data.get("cpf", "").strip()
    data_nascimento_str = data.get("data_nascimento", "").strip()

    telefone = re.sub(r'\D', '', telefone)
    cpf = re.sub(r'\D', '', cpf)

    if not nome:
        erros["nome"] = "Nome é obrigatório."
    elif any(char.isdigit() for char in nome):
        erros["nome"] = "Nome inválido. Não deve conter números."

    if not telefone:
        erros["telefone"] = "Telefone é obrigatório."
    elif not telefone.isdigit() or len(telefone) not in [10, 11]:
        erros["telefone"] = "Telefone inválido. Deve conter 10 ou 11 dígitos numéricos."

    if not cpf:
        erros["cpf"] = "CPF é obrigatório."
    elif not cpf.isdigit() or len(cpf) != 11:
        erros["cpf"] = "CPF inválido. Deve conter exatamente 11 dígitos numéricos."
    elif User.query.filter_by(cpf=cpf).first():
        erros["cpf"] = "CPF já cadastrado."

    if User.query.filter_by(telefone=telefone).first():
        erros["telefone"] = "Telefone já cadastrado."

    try:
        data_nasc = datetime.strptime(data_nascimento_str, "%Y-%m-%d").date()
        hoje = datetime.today().date()

        if data_nasc > hoje:
            erros["data_nascimento"] = "Data de nascimento não pode ser futura."

        idade = (hoje - data_nasc).days // 365
        if idade < 15:
            erros["data_nascimento"] = "Usuário deve ter pelo menos 15 anos."
    except ValueError:
        erros["data_nascimento"] = "Data inválida. Use o formato YYYY-MM-DD."

    if erros:
        raise ValueError(erros)

    novo_usuario = User(
        nome=nome,
        endereco=data["endereco"],
        telefone=telefone,
        cpf=cpf,
        data_nascimento=data_nasc
    )

    try:
        db.session.add(novo_usuario)
        db.session.commit()
        return {"message": "Usuário registrado com sucesso!", "id": novo_usuario.id}
    except Exception as e:
        db.session.rollback()
        raise ValueError({"form": f"Erro ao registrar usuário: {e}"})


def atualizar_usuario(id_usuario, data):
    usuario = User.query.get(id_usuario)
    if not usuario:
        raise ValueError("Usuário não encontrado.")

    usuario.nome = data.get("nome", usuario.nome)
    usuario.endereco = data.get("endereco", usuario.endereco)
    usuario.telefone = data.get("telefone", usuario.telefone)
    usuario.cpf = data.get("cpf", usuario.cpf)
    usuario.data_nascimento = data.get(
        "data_nascimento", usuario.data_nascimento)

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
