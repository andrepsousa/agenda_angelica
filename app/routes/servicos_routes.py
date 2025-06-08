# Imports organizados
from flask import Blueprint, request, render_template, redirect, url_for, flash
from app.models.servico_models import (
    listar_servicos,
    servico_by_id_dict,
    servico_by_id_obj,
    criar_servico,
    deletar_servico,
    atualizar_servico
)
from flask_login import login_user, logout_user, login_required, current_user

servicos_bp = Blueprint('servicos_bp', __name__, url_prefix='/servicos')


# Página que lista todos os serviços
@servicos_bp.route('/servicos', methods=['GET'])
def get_servicos():
    servicos = listar_servicos()
    return render_template('servicos/list.html', servicos=servicos)

# Página de detalhe de um serviço


@servicos_bp.route('/<int:id>', methods=['GET'])
def get_servico_por_id(id):
    try:
        servico = servico_by_id_dict(id)
        return render_template('servicos/detail.html', servico=servico)
    except Exception as e:
        flash(f'Serviço não encontrado: {e}', 'danger')
        return redirect(url_for('servicos_bp.get_servicos'))


# Formulário de criação de serviço (GET)
@servicos_bp.route('/novo', methods=['GET'])
def get_servico():
    return render_template('servicos/create.html')

# Criação de serviço (POST)


@servicos_bp.route('/', methods=['POST'])
def post_servico():
    try:
        data = {
            "nome": request.form.get("nome"),
            "descricao": request.form.get("descricao"),
            "preco": float(request.form.get("preco")),
            "status": bool(request.form.get("status"))
        }

        criar_servico(data)
        flash("Serviço criado com sucesso!", "servico_create_success")
        return redirect(url_for('servicos_bp.get_servicos'))

    except Exception as e:
        flash(f"Erro ao criar serviço: {e}", "servico_create_error")
        return redirect(url_for('servicos_bp.get_servicos'))


@servicos_bp.route('/editar/<int:id_servico>', methods=['GET', 'POST'])
def editar_servico(id_servico):
    try:
        servico = servico_by_id_obj(id_servico)
    except Exception as e:
        # categoria específica
        flash(f'Serviço não encontrado: {e}', 'servico_error')
        return redirect(url_for('servicos_bp.get_servicos'))

    if request.method == 'POST':
        data = {
            "nome": request.form['nome'],
            "descricao": request.form['descricao'],
            "preco": float(request.form['preco']),
            "status": 'status' in request.form
        }

        try:
            atualizar_servico(id_servico, data)
            flash("Serviço atualizado com sucesso!",
                  "servico_success")  # categoria específica
        except Exception as e:
            # categoria específica
            flash(f"Erro ao atualizar serviço: {e}", "servico_error")

        return redirect(url_for('servicos_bp.get_servicos'))

    return render_template('servicos/edit.html', servico=servico)


# Rota para deletar um serviço (por GET ou POST via botão no HTML)
@servicos_bp.route('/deletar/<int:id>', methods=['POST'])
def delete_servico(id):
    try:
        deletar_servico(id)
        flash("Serviço deletado com sucesso!", "success")
    except Exception as e:
        flash(f"Erro ao deletar serviço: {e}", "danger")
    return redirect(url_for('servicos_bp.get_servicos'))
