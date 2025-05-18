from flask import Blueprint, request, jsonify, render_template, redirect, url_for, flash
from flask_login import login_user, logout_user, login_required, current_user
from datetime import datetime, time
from app.config import db
from app.models.models import Agendamento, User, Service
from app.models.agendamento_models import (
    agendamento_by_id, list_agendamentos, criar_agendamento_simples,
    criar_agendamentos_recorrentes, delete_agendamento, atualizar_agendamento
)

# Defina os horários válidos das 10:00 às 18:00 em intervalos de 1 hora
HORARIOS_VALIDOS = [time(hour=h) for h in range(10, 19)]  # De 10:00 a 18:00

bp_agendamentos = Blueprint(
    'bp_agendamentos', __name__, url_prefix='/agendamentos')


@bp_agendamentos.route('/horarios', methods=['GET', 'POST'])
def horarios():
    mensagem = " "

    # Gera a lista de horários válidos (10h às 18h)
    todos_horarios = [f"{hora:02}:00" for hora in range(10, 18)]

    # Extrai apenas a parte do horário (HH:MM) dos agendamentos existentes
    horarios_agendados = [
        a.data_hora.strftime('%H:%M') for a in Agendamento.query.all()
    ]

    horarios_disponiveis = [
        h for h in todos_horarios if h not in horarios_agendados
    ]

    if request.method == "POST":
        horario = request.form.get('horario')

        if not horario:
            mensagem = "Por favor, selecione um horário."
        elif horario not in horarios_disponiveis:
            mensagem = f"O horário {horario} não está mais disponível."
        else:
            # Cria um datetime com data de hoje e o horário selecionado
            hoje = datetime.now().date()
            hora_selecionada = datetime.strptime(horario, '%H:%M').time()
            data_hora = datetime.combine(hoje, hora_selecionada)

            novo_agendamento = Agendamento(data_hora=data_hora)
            db.session.add(novo_agendamento)
            db.session.commit()
            mensagem = f"Agendamento para {horario} realizado com sucesso!"

            # Atualiza os horários disponíveis
            horarios_agendados = [
                a.data_hora.strftime('%H:%M') for a in Agendamento.query.all()
            ]
            horarios_disponiveis = [
                h for h in todos_horarios if h not in horarios_agendados
            ]

        return render_template('agendamentos/detail.html', horarios=horarios_disponiveis, mensagem=mensagem)

    return render_template('agendamentos/detail.html', horarios=horarios_disponiveis, mensagem=mensagem)


@bp_agendamentos.route('/', methods=['GET'])
@login_required
def get_agendamentos():
    # Filtra agendamentos conforme o tipo de usuário
    if current_user.role == 'cliente':
        agendamentos = Agendamento.query.filter_by(
            cliente_id=current_user.id).all()
    else:
        agendamentos = Agendamento.query.all()

    # Formata os dados para o template
    agendamentos_json = [{
        'id': ag.id,
        'cliente_nome': ag.usuario.nome,
        'servico_nome': ag.servico.nome,
        'data_hora': ag.data_hora.strftime('%d/%m/%Y %H:%M'),
        'status': ag.status,
        'recorrencia': ag.recorrencia
    } for ag in agendamentos]

    return render_template('agendamentos/list.html', agendamentos=agendamentos_json)


@bp_agendamentos.route('/<int:id_agendamento>', methods=['GET'])
def get_agendamentos_id(id_agendamento):
    try:
        agendamento = agendamento_by_id(id_agendamento)
        return render_template('agendamentos/detail.html', agendamento=agendamento)
    except ValueError as e:
        return render_template('agendamentos/error.html', erro=str(e)), 404


@bp_agendamentos.route('/hoje')
@login_required
def agendamentos_hoje():
    hoje = datetime.now().date()

    if current_user.role == 'cliente':
        agendamentos = Agendamento.query.filter(
            Agendamento.cliente_id == current_user.id,
            db.func.date(Agendamento.data_hora) == hoje
        ).all()
    else:
        agendamentos = Agendamento.query.filter(
            db.func.date(Agendamento.data_hora) == hoje
        ).all()

    return render_template('index.html', agendamentos=agendamentos)


@bp_agendamentos.route('/novo', methods=['GET', 'POST'])
@login_required
def criar_agendamento():
    if request.method == 'GET':
        clientes = User.query.all()
        servicos = Service.query.filter_by(status=True).all()
        return render_template('agendamentos/create.html',
                               clientes=clientes,
                               servicos=servicos,
                               current_user=current_user)

    try:
        # Obtém os dados do formulário
        data_hora_str = request.form.get("data_hora")
        servico_id = request.form.get("servico_id")
        observacoes = request.form.get("observacoes", "")
        recorrencia = request.form.get("recorrencia", None)
        num_recorrencias = int(request.form.get("num_recorrencias", 1))

        # Define o cliente_id conforme o tipo de usuário
        if current_user.role == 'cliente':
            cliente_id = current_user.id
            status = "ativo"  # Status fixo para clientes
        else:
            cliente_id = request.form.get("cliente_id")
            status = request.form.get("status", "ativo")  # Admin pode definir

        # Validações
        if not data_hora_str:
            raise ValueError(
                "Por favor, forneça a data e hora para o agendamento.")

        data_hora = datetime.strptime(data_hora_str, '%Y-%m-%dT%H:%M')

        if data_hora.time() not in HORARIOS_VALIDOS:
            raise ValueError(
                "Horário inválido. Escolha um horário inteiro entre 10:00 e 18:00.")

        if Agendamento.query.filter_by(data_hora=data_hora).first():
            raise ValueError("Este horário já está agendado. Escolha outro.")

        # Dados do agendamento
        data = {
            "cliente_id": cliente_id,
            "servico_id": servico_id,
            "data_hora": data_hora,
            "recorrencia": recorrencia,
            "num_recorrencias": num_recorrencias,
            "status": status,
            "observacoes": observacoes
        }

        # Criação do agendamento
        if recorrencia:
            agendamentos = criar_agendamentos_recorrentes(data)
        else:
            agendamentos = [criar_agendamento_simples(data)]

        return render_template('agendamentos/success.html', agendamentos=agendamentos)

    except ValueError as e:
        clientes = User.query.all()
        servicos = Service.query.filter_by(status=True).all()
        return render_template('agendamentos/create.html',
                               erro=str(e),
                               clientes=clientes,
                               servicos=servicos,
                               current_user=current_user)


@bp_agendamentos.route('/<int:id_agendamento>/editar', methods=['GET', 'POST'])
@login_required
def editar_agendamento(id_agendamento):
    agendamento = Agendamento.query.get_or_404(id_agendamento)

    if request.method == 'GET':
        clientes = User.query.all()
        servicos = Service.query.filter_by(status=True).all()
        return render_template('agendamentos/edit.html',
                               agendamento=agendamento,
                               clientes=clientes,
                               servicos=servicos,
                               current_user=current_user)

    if request.method == 'POST':
        try:
            dados = {
                "servico_id": request.form.get("servico_id"),
                "data_hora": datetime.strptime(request.form.get("data_hora"), '%Y-%m-%dT%H:%M'),
                "recorrencia": request.form.get("recorrencia"),
                "observacoes": request.form.get("observacoes", "")
            }

            # Apenas admin pode alterar cliente_id e status
            if current_user.role != 'cliente':
                dados["cliente_id"] = request.form.get("cliente_id")
                dados["status"] = request.form.get("status", "ativo")

            atualizar_agendamento(id_agendamento, dados)
            flash("Agendamento atualizado com sucesso!", "success")
            return redirect(url_for('bp_agendamentos.get_agendamentos'))

        except ValueError as e:
            flash(str(e), "danger")
            clientes = User.query.all()
            servicos = Service.query.filter_by(status=True).all()
            return render_template('agendamentos/edit.html',
                                   agendamento=agendamento,
                                   clientes=clientes,
                                   servicos=servicos,
                                   current_user=current_user)


@bp_agendamentos.route('/<int:id_agendamento>/delete', methods=['GET', 'POST'])
def deletar_agendamento(id_agendamento):
    try:
        agendamento = Agendamento.query.get(id_agendamento)

        if not agendamento:
            raise ValueError("Agendamento não encontrado!")

        if request.method == 'POST':
            delete_agendamento(id_agendamento)
            return redirect(url_for("bp_agendamentos.get_agendamentos"))

        return render_template('agendamentos/delete.html', agendamento=agendamento)

    except ValueError as e:
        return render_template('agendamentos/error.html', erro=str(e)), 404
    except Exception as e:
        return render_template('agendamentos/error.html', erro="Erro interno no servidor"), 500
