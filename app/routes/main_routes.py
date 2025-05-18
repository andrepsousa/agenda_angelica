from flask import Blueprint, render_template
from datetime import date, datetime, timedelta
from app.models.models import Agendamento, Service
from flask_login import login_user, logout_user, login_required, current_user

main_bp = Blueprint('main_bp', __name__, url_prefix='/inicio')

@main_bp.route('/index')
def index():
    hoje = date.today()
    inicio_do_dia = datetime.combine(hoje, datetime.min.time())
    fim_do_dia = inicio_do_dia + timedelta(days=1) - timedelta(seconds=1)

    print(f"Hoje: {hoje}")
    print(f"Início do dia: {datetime.combine(hoje, datetime.min.time())}")
    print(f"Fim do dia: {datetime.combine(hoje, datetime.max.time())}")


    # Busca agendamentos de hoje
    agendamentos = Agendamento.query.filter(
        Agendamento.data_hora >= inicio_do_dia,
        Agendamento.data_hora <= fim_do_dia
    ).all()

    print(f"Agendamentos encontrados: {agendamentos}")  

    servicos = Service.query.filter_by(status=True).all()

    return render_template(
        'index.html',
        agendamentos=agendamentos,
        servicos=servicos
    )


@main_bp.route('/sobre')
def sobre():
    return render_template('sobre.html')
