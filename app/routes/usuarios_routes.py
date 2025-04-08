from flask import Blueprint, request, flash, redirect, url_for, render_template
from datetime import datetime
from app.models.user_models import (
    listar_usuarios as listar_usuarios_model,
    usuario_by_id,
    criar_usuario,
    atualizar_usuario,
    deletar_usuario
)

usuarios_bp = Blueprint('usuarios_bp', __name__, url_prefix='/usuarios')


# Página que lista todos os usuários
@usuarios_bp.route('/', methods=['GET'])
def listar_usuarios():
    try:
        usuarios = listar_usuarios_model()
        return render_template('user/list.html', usuarios=usuarios)
    except Exception as e:
        flash(f"Erro ao listar usuários: {e}", "danger")
        return render_template('user/list.html', usuarios=[])


# Página de detalhes de um usuário
@usuarios_bp.route('/<int:id>', methods=['GET'])
def obter_usuario(id):
    try:
        usuario = usuario_by_id(id)
        return render_template('user/detail.html', usuario=usuario)
    except Exception as e:
        flash(f"Usuário não encontrado: {e}", "danger")
        return redirect(url_for('usuarios_bp.listar_usuarios'))


@usuarios_bp.route('/novo', methods=['GET'])
def novo_usuario_form():
    return render_template('user/create.html', erros=None, valores={})


# POST - Criação de novo usuário
@usuarios_bp.route('/', methods=['POST'])
def criar_novo_usuario():
    data = {
        "nome": request.form.get("nome"),
        "endereco": request.form.get("endereco"),
        "telefone": request.form.get("telefone"),
        "cpf": request.form.get("cpf"),
        "data_nascimento": request.form.get("data_nascimento")
    }

    try:
        criar_usuario(data)
        flash("Usuário criado com sucesso!", "success")
        return redirect(url_for('usuarios_bp.listar_usuarios'))

    except ValueError as e:
        # Aqui esperamos um dicionário de erros
        if isinstance(e.args[0], dict):
            return render_template('user/create.html', erros=e.args[0], valores=data)

        else:
            flash(f"Erro inesperado: {e}", "danger")
            return redirect(url_for('usuarios_bp.novo_usuario_form'))



# Página de atualização de usuário (GET)
@usuarios_bp.route('/editar/<int:id>', methods=['GET'])
def editar_usuario_form(id):
    try:
        usuario = usuario_by_id(id)
        return render_template('user/edit.html', usuario=usuario)
    except Exception as e:
        flash(f"Usuário não encontrado: {e}", "danger")
        return redirect(url_for('usuarios_bp.listar_usuarios'))


# POST - Atualização de usuário
@usuarios_bp.route('/editar/<int:id>', methods=['POST'])
def atualizar_usuario_por_id(id):
    try:
        dados = {
            "nome": request.form.get("nome"),
            "endereco": request.form.get("endereco"),
            "telefone": request.form.get("telefone"),
            "cpf": request.form.get("cpf"),
            "data_nascimento": datetime.strptime(request.form.get("data_nascimento"), "%Y-%m-%d").date()
        }

        atualizar_usuario(id, dados)

        flash("Usuário atualizado com sucesso!", "success")
        return redirect(url_for('usuarios_bp.listar_usuarios'))

    except Exception as e:
        flash(f"Erro ao atualizar usuário: {e}", "danger")
        return redirect(url_for('usuarios_bp.editar_usuario_form', id=id))


# POST - Deleção de usuário
@usuarios_bp.route('/deletar/<int:id>', methods=['POST'])
def deletar_usuario_por_id(id):
    try:
        deletar_usuario(id)
        flash("Usuário removido com sucesso!", "success")
    except Exception as e:
        flash(f"Erro ao remover usuário: {e}", "danger")
    return redirect(url_for('usuarios_bp.listar_usuarios'))
