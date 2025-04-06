from flask import Blueprint, request, jsonify, render_template, redirect, url_for, flash
from datetime import datetime
from app.models.models import Agendamento, User, Service
from app.models.agendamento_models import (
    agendamento_by_id, list_agendamentos, criar_agendamento_simples,
    criar_agendamentos_recorrentes, delete_agendamento, atualizar_agendamento
)

bp_agendamentos = Blueprint('bp_agendamentos', __name__, url_prefix='/agendamentos')


@bp_agendamentos.route('/', methods=['GET'])
def get_agendamentos():
    agendamentos = list_agendamentos()
    return render_template('agendamentos/list.html', agendamentos=agendamentos)


@bp_agendamentos.route('/<int:id_agendamento>', methods=['GET'])
def get_agendamentos_id(id_agendamento):
    try:
        agendamento = agendamento_by_id(id_agendamento)
        return render_template('agendamentos/detail.html', agendamento=agendamento)
    except ValueError as e:
        return render_template('agendamentos/error.html', erro=str(e)), 404


@bp_agendamentos.route('/novo', methods=['GET', 'POST'])
def criar_agendamento():
    if request.method == 'GET':
        clientes = User.query.all()
        servicos = Service.query.filter_by(status=True).all()
        return render_template('agendamentos/create.html', clientes=clientes, servicos=servicos)

    # Pegando os dados do formulário
    cliente_id = request.form.get("cliente_id")
    servico_id = request.form.get("servico_id")
    # Data no formato 'YYYY-MM-DDTHH:MM'
    data_hora_str = request.form.get("data_hora")
    recorrencia = request.form.get("recorrencia", None)
    # Número de recorrências, padrão 1
    num_recorrencias = int(request.form.get("num_recorrencias", 1))
    status = request.form.get("status", "ativo")

    try:
        # Converte a data_hora para o formato datetime
        data_hora = datetime.strptime(data_hora_str, '%Y-%m-%dT%H:%M')

        data = {
            "cliente_id": cliente_id,
            "servico_id": servico_id,
            "data_hora": data_hora,
            "recorrencia": recorrencia,
            "num_recorrencias": num_recorrencias,
            "status": status
        }

        if recorrencia:
            agendamentos = criar_agendamentos_recorrentes(data)
        else:
            agendamentos = [criar_agendamento_simples(data)]

        return render_template('agendamentos/success.html', agendamentos=agendamentos)

    except ValueError as e:
        return render_template('agendamentos/create.html', erro="Erro no formato da data. Tente novamente.", clientes=User.query.all(), servicos=Service.query.filter_by(status=True).all())


@bp_agendamentos.route('/<int:id_agendamento>/editar', methods=['GET', 'POST'])
def editar_agendamento(id_agendamento):
    agendamento = Agendamento.query.get(id_agendamento)

    if not agendamento:
        return render_template('agendamentos/error.html', erro="Agendamento não encontrado!"), 404

    if request.method == 'GET':
        clientes = User.query.all()
        servicos = Service.query.filter_by(status=True).all()
        return render_template('agendamentos/edit.html', agendamento=agendamento, clientes=clientes, servicos=servicos)

    if request.method == 'POST':
        try:
            dados = {
                "cliente_id": request.form.get("cliente_id"),
                "servico_id": request.form.get("servico_id"),
                "data_hora": datetime.strptime(request.form.get("data_hora"), '%Y-%m-%dT%H:%M'),
                "recorrencia": request.form.get("recorrencia"),
                "status": request.form.get("status")
            }

            atualizar_agendamento(id_agendamento, dados)
            flash("Agendamento atualizado com sucesso!", "success")
            return redirect(url_for('agendamentos.get_agendamentos'))

        except ValueError as e:
            flash(str(e), "danger")
            clientes = User.query.all()
            servicos = Service.query.filter_by(status=True).all()
            return render_template('agendamentos/edit.html', agendamento=agendamento, clientes=clientes, servicos=servicos)


@bp_agendamentos.route('/<int:id_agendamento>/delete', methods=['GET', 'POST'])
def deletar_agendamento(id_agendamento):
    try:
        print(f"Tentando acessar agendamento {id_agendamento}")  # 🟢 Debug
        agendamento = Agendamento.query.get(id_agendamento)

        if not agendamento:
            print("Erro: Agendamento não encontrado!")  # 🟢 Debug
            raise ValueError("Agendamento não encontrado!")

        if request.method == 'POST':
            print(f"Deletando agendamento {id_agendamento}")  # 🟢 Debug
            delete_agendamento(id_agendamento)
            return redirect(url_for('agendamentos.get_agendamentos'))

        return render_template('agendamentos/delete.html', agendamento=agendamento)

    except ValueError as e:
        print(f"Erro de valor: {e}")  # 🟢 Debug
        return render_template('agendamentos/error.html', erro=str(e)), 404
    except Exception as e:
        print(f"Erro ao tentar deletar agendamento: {e}")  # 🟢 Debug
        return render_template('agendamentos/error.html', erro="Erro interno no servidor"), 500
