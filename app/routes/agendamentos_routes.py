from flask import Blueprint, request, jsonify, render_template, redirect, url_for, flash, session, current_app
from flask_login import login_user, logout_user, login_required, current_user
from datetime import datetime, time, timedelta
from app.config import db
from app.models.models import Agendamento, User, Service
from app.models.agendamento_models import (
    agendamento_by_id, list_agendamentos, criar_agendamento_simples,
    criar_agendamentos_recorrentes, delete_agendamento, atualizar_agendamento
)
from app.http.whatsapp import WhatsAppService
import logging
from sqlalchemy import and_, or_

# Configuração do logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Define os horários válidos das 12:00 às 19:00 em intervalos de 1 hora
HORARIOS_VALIDOS = [time(hour=h) for h in range(12, 20)]  # De 12:00 a 19:00

bp_agendamentos = Blueprint(
    'bp_agendamentos', __name__, url_prefix='/agendamentos')
whatsapp_service = WhatsAppService()

def verificar_horario_disponivel(data_hora):
    try:
        logger.info(f"Verificando disponibilidade para: {data_hora}")
        
        # Verifica se já existe um agendamento para este horário
        agendamento_existente = Agendamento.query.filter(
            Agendamento.data_hora == data_hora,
            Agendamento.status != 'cancelado'
        ).first()
        
        if agendamento_existente:
            logger.info(f"Horário {data_hora} já está ocupado")
            return False
            
        logger.info(f"Horário {data_hora} está disponível")
        return True
        
    except Exception as e:
        logger.error(f"Erro ao verificar disponibilidade: {e}")
        return False

@bp_agendamentos.route('/horarios-disponiveis/<data>')
@login_required
def horarios_disponiveis(data):
    try:
        logger.info(f"Recebida requisição para data: {data}")
        
        # Converte a string da data para objeto date
        data_obj = datetime.strptime(data, '%Y-%m-%d').date()
        logger.info(f"Data convertida: {data_obj}")
        
        # Lista de todos os horários possíveis (12:00 às 19:00)
        todos_horarios = [
            "12:00", "13:00", "14:00", "15:00", 
            "16:00", "17:00", "18:00", "19:00"
        ]
        
        horarios_disponiveis = []
        
        for horario_str in todos_horarios:
            try:
                # Converte o horário para objeto datetime
                hora = datetime.strptime(horario_str, '%H:%M').time()
                data_hora = datetime.combine(data_obj, hora)
                logger.info(f"Verificando disponibilidade para: {data_hora}")
                
                # Verifica se o horário está disponível
                if verificar_horario_disponivel(data_hora):
                    horarios_disponiveis.append(horario_str)
                    logger.info(f"Horário {horario_str} está disponível")
                else:
                    logger.info(f"Horário {horario_str} não está disponível")
            except Exception as e:
                logger.error(f"Erro ao processar horário {horario_str}: {e}")
                continue
        
        logger.info(f"Horários disponíveis encontrados: {horarios_disponiveis}")
        return jsonify({
            'horarios': horarios_disponiveis
        })
        
    except ValueError as e:
        logger.error(f"Erro ao processar data: {e}")
        return jsonify({
            'erro': 'Data inválida'
        }), 400
    except Exception as e:
        logger.error(f"Erro ao buscar horários disponíveis: {e}")
        return jsonify({
            'erro': 'Erro ao buscar horários disponíveis'
        }), 500

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


@bp_agendamentos.route('/agendamentos', methods=['GET'])
@login_required
def get_agendamentos():
    try:
        # Se for admin, mostra todos os agendamentos
        if current_user.role == 'admin':
            agendamentos = Agendamento.query.order_by(Agendamento.data_hora.desc()).all()
            logger.info(f"Admin visualizando todos os agendamentos ({len(agendamentos)} encontrados)")
        else:
            # Se for cliente, mostra apenas seus agendamentos
            agendamentos = Agendamento.query.filter_by(cliente_id=current_user.id).order_by(Agendamento.data_hora.desc()).all()
            logger.info(f"Cliente visualizando seus agendamentos ({len(agendamentos)} encontrados)")
        
        return render_template('agendamentos/list.html', agendamentos=agendamentos)
    except Exception as e:
        logger.error(f"Erro ao listar agendamentos: {e}")
        flash('Erro ao carregar agendamentos. Tente novamente.', 'error')
        return redirect(url_for('main_bp.index'))


@bp_agendamentos.route('/<int:id_agendamento>', methods=['GET'])
def get_agendamentos_id(id_agendamento):
    try:
        agendamento = Agendamento.query.get_or_404(id_agendamento)
        return render_template('agendamentos/detail.html', agendamento=agendamento)
    except Exception as e:
        flash(f"Erro ao buscar agendamento: {str(e)}", "danger")
        return redirect(url_for('bp_agendamentos.get_agendamentos'))


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
        clientes = User.query.filter_by(role='cliente').all()
        servicos = Service.query.filter_by(status=True).all()
        return render_template('agendamentos/create.html',
                             clientes=clientes,
                             servicos=servicos,
                             current_user=current_user,
                             now=datetime.now())

    try:
        # Obtém os dados do formulário
        data = request.form.get("data")
        hora = request.form.get("hora")
        servico_id = request.form.get("servico")
        observacoes = request.form.get("observacoes", "")
        recorrencia = request.form.get("recorrencia")
        num_recorrencias = int(request.form.get("num_recorrencias", 1))

        # Define o cliente_id conforme o tipo de usuário
        if current_user.role == 'cliente':
            cliente_id = current_user.id
        else:
            cliente_id = request.form.get("cliente")

        # Validações
        if not data or not hora:
            raise ValueError("Por favor, forneça a data e hora para o agendamento.")

        if not servico_id:
            raise ValueError("Por favor, selecione um serviço.")

        if current_user.role != 'cliente' and not cliente_id:
            raise ValueError("Por favor, selecione um cliente.")

        data_hora = datetime.strptime(f"{data} {hora}", '%Y-%m-%d %H:%M')
        
        # Validação de data passada
        agora = datetime.now()
        if data_hora < agora:
            raise ValueError("Não é possível criar agendamentos para datas/horários passados.")

        if data_hora.time() not in HORARIOS_VALIDOS:
            raise ValueError("Horário inválido. Escolha um horário entre 12:00 e 19:00.")

        if not verificar_horario_disponivel(data_hora):
            raise ValueError("Este horário já está agendado. Escolha outro.")

        # Cria agendamentos recorrentes
        if recorrencia:
            # Cria agendamentos recorrentes
            agendamentos = []
            for i in range(num_recorrencias):
                if recorrencia == 'semanal':
                    nova_data_hora = data_hora + timedelta(weeks=i)
                elif recorrencia == 'quinzenal':
                    nova_data_hora = data_hora + timedelta(weeks=i*2)
                elif recorrencia == 'mensal':
                    nova_data_hora = data_hora + timedelta(days=30*i)
                
                # Verifica se a data ainda está no mesmo mês
                if nova_data_hora.month != data_hora.month or nova_data_hora.year != data_hora.year:
                    break

                # Validação de data passada para recorrências
                if nova_data_hora < agora:
                    continue

                if verificar_horario_disponivel(nova_data_hora):
                    agendamento = Agendamento(
                        cliente_id=cliente_id,
                        servico_id=servico_id,
                        data_hora=nova_data_hora,
                        recorrencia=recorrencia,
                        status='pendente',
                        observacoes=observacoes
                    )
                    agendamentos.append(agendamento)
                else:
                    raise ValueError(f"O horário {nova_data_hora.strftime('%H:%M')} do dia {nova_data_hora.strftime('%d/%m/%Y')} já está ocupado.")

            if not agendamentos:
                raise ValueError("Não foi possível criar nenhum agendamento recorrente.")

            # Gera e envia código de verificação para o primeiro agendamento
            codigo = whatsapp_service.gerar_codigo()
            agendamentos[0].gerar_codigo_verificacao(codigo)
            
            # Obtém o telefone do cliente
            cliente = User.query.get(cliente_id)
            resultado = whatsapp_service.enviar_codigo(cliente.telefone, codigo)

            if "erro" in resultado:
                raise ValueError(f"Erro ao enviar código via WhatsApp: {resultado['erro']}")

            db.session.add_all(agendamentos)
            db.session.commit()
            
            # Armazena o ID do primeiro agendamento na sessão para verificação
            session['agendamento_id'] = agendamentos[0].id
            
            flash(f"Agendamentos recorrentes criados com sucesso! Código de confirmação enviado via WhatsApp.", "success")
        else:
            # Cria um único agendamento
            agendamento = Agendamento(
                cliente_id=cliente_id,
                servico_id=servico_id,
                data_hora=data_hora,
                recorrencia=recorrencia,
                status='pendente',
                observacoes=observacoes
            )

            # Gera e envia código de verificação
            codigo = whatsapp_service.gerar_codigo()
            agendamento.gerar_codigo_verificacao(codigo)
            
            # Obtém o telefone do cliente
            cliente = User.query.get(cliente_id)
            resultado = whatsapp_service.enviar_codigo(cliente.telefone, codigo)

            if "erro" in resultado:
                raise ValueError(f"Erro ao enviar código via WhatsApp: {resultado['erro']}")
            
            db.session.add(agendamento)
            db.session.commit()
            
            # Armazena o ID do agendamento na sessão para verificação
            session['agendamento_id'] = agendamento.id
            
            flash("Código de confirmação enviado via WhatsApp! Por favor, verifique seu celular.", "success")

        return redirect(url_for('bp_agendamentos.verificar_agendamento'))
    
    except ValueError as e:
        flash(str(e), "error")
        return redirect(url_for('bp_agendamentos.criar_agendamento'))
    except Exception as e:
        db.session.rollback()
        logger.error(f"Erro ao criar agendamento: {e}")
        flash("Erro ao criar agendamento. Tente novamente.", "error")
        return redirect(url_for('bp_agendamentos.criar_agendamento'))

@bp_agendamentos.route('/verificar', methods=['GET', 'POST'])
@login_required
def verificar_agendamento():
    if request.method == 'GET':
        agendamento_id = session.get('agendamento_id')
        if not agendamento_id:
            flash("Nenhum agendamento pendente de verificação.", "warning")
            return redirect(url_for('bp_agendamentos.get_agendamentos'))
        
        agendamento = Agendamento.query.get(agendamento_id)
        if not agendamento:
            flash("Agendamento não encontrado.", "error")
            return redirect(url_for('bp_agendamentos.get_agendamentos'))
        
        return render_template('agendamentos/verify.html', agendamento=agendamento)

    try:
        codigo = request.form.get('codigo')
        agendamento_id = request.form.get('agendamento_id')
        
        if not codigo or not agendamento_id:
            raise ValueError("Código de verificação e ID do agendamento são obrigatórios.")

        agendamento = Agendamento.query.get(agendamento_id)
        if not agendamento:
            raise ValueError("Agendamento não encontrado.")

        if agendamento.verificar_codigo(codigo):
            agendamento.status = 'confirmado'
            db.session.commit()
            
            # Limpa o ID do agendamento da sessão
            session.pop('agendamento_id', None)
            
            flash("Agendamento confirmado com sucesso!", "success")
            return redirect(url_for('bp_agendamentos.get_agendamentos'))
        else:
            raise ValueError("Código de verificação inválido.")

    except ValueError as e:
        flash(str(e), "error")
        return redirect(url_for('bp_agendamentos.verificar_agendamento'))
    except Exception as e:
        db.session.rollback()
        logger.error(f"Erro ao verificar agendamento: {e}")
        flash("Erro ao verificar agendamento. Tente novamente.", "error")
        return redirect(url_for('bp_agendamentos.verificar_agendamento'))

@bp_agendamentos.route('/<int:id_agendamento>/cancelar', methods=['POST'])
@login_required
def cancelar_agendamento(id_agendamento):
    agendamento = Agendamento.query.get_or_404(id_agendamento)
    
    # Apenas admin pode cancelar agendamentos
    if current_user.role != 'admin':
        flash("Você não tem permissão para cancelar agendamentos.", "danger")
        return redirect(url_for('bp_agendamentos.get_agendamentos'))
    
    agendamento.status = 'cancelado'
    db.session.commit()
    flash("Agendamento cancelado com sucesso!", "success")
    return redirect(url_for('bp_agendamentos.get_agendamentos'))

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

@bp_agendamentos.route('/historico')
@login_required
def get_historico():
    try:
        logger.info(f"Buscando histórico para o usuário {current_user.id} (role: {current_user.role})")
        
        # Busca agendamentos passados
        hoje = datetime.now().date()
        inicio_do_dia = datetime.combine(hoje, datetime.min.time())

        # Se for admin, mostra todos os agendamentos passados
        if current_user.role == 'admin':
            agendamentos = Agendamento.query.filter(
                Agendamento.data_hora < inicio_do_dia
            ).order_by(Agendamento.data_hora.desc()).all()
            logger.info(f"Admin visualizando histórico de todos os agendamentos ({len(agendamentos)} encontrados)")
        else:
            # Se for cliente, mostra apenas seus agendamentos passados
            agendamentos = Agendamento.query.filter(
                Agendamento.cliente_id == current_user.id,
                Agendamento.data_hora < inicio_do_dia
            ).order_by(Agendamento.data_hora.desc()).all()
            logger.info(f"Cliente visualizando seu histórico de agendamentos ({len(agendamentos)} encontrados)")
        
        return render_template('agendamentos/historico.html', agendamentos=agendamentos)
    except Exception as e:
        logger.error(f"Erro ao buscar histórico: {str(e)}")
        flash("Erro ao buscar histórico", "danger")
        return render_template('agendamentos/historico.html', agendamentos=[])

@bp_agendamentos.route('/<int:id_agendamento>/solicitar-alteracao', methods=['GET', 'POST'])
@login_required
def solicitar_alteracao(id_agendamento):
    agendamento = Agendamento.query.get_or_404(id_agendamento)
    
    # Verifica se o usuário tem permissão para alterar este agendamento
    if current_user.role != 'admin' and agendamento.cliente_id != current_user.id:
        flash('Você não tem permissão para alterar este agendamento.', 'error')
        return redirect(url_for('bp_agendamentos.get_agendamentos'))
    
    # Verifica se o agendamento pode ser alterado
    if agendamento.status not in ['confirmado', 'alteracao_pendente']:
        flash('Este agendamento não pode ser alterado.', 'error')
        return redirect(url_for('bp_agendamentos.get_agendamentos'))
    
    if request.method == 'POST':
        nova_data = datetime.strptime(request.form['data'], '%Y-%m-%d')
        novo_horario = datetime.strptime(request.form['hora'], '%H:%M').time()
        nova_data_hora = datetime.combine(nova_data.date(), novo_horario)
        novo_servico_id = request.form.get('servico_id')
        motivo = request.form.get('motivo')
        
        # Verifica se o novo horário está disponível
        if novo_servico_id:
            servico = Service.query.get(novo_servico_id)
            if not servico:
                flash('Serviço não encontrado.', 'error')
                return redirect(url_for('bp_agendamentos.solicitar_alteracao', id_agendamento=id_agendamento))
            
            # Verifica disponibilidade para o novo serviço
            agendamentos_existentes = Agendamento.query.filter(
                and_(
                    Agendamento.servico_id == int(novo_servico_id),
                    Agendamento.data_hora == nova_data_hora,
                    Agendamento.id != id_agendamento,
                    Agendamento.status == 'confirmado'
                )
            ).first()
            
            if agendamentos_existentes:
                flash('Horário não disponível para este serviço.', 'error')
                return redirect(url_for('bp_agendamentos.solicitar_alteracao', id_agendamento=id_agendamento))
        else:
            # Verifica disponibilidade para o serviço atual
            agendamentos_existentes = Agendamento.query.filter(
                and_(
                    Agendamento.servico_id == agendamento.servico_id,
                    Agendamento.data_hora == nova_data_hora,
                    Agendamento.id != id_agendamento,
                    Agendamento.status == 'confirmado'
                )
            ).first()
            
            if agendamentos_existentes:
                flash('Horário não disponível para este serviço.', 'error')
                return redirect(url_for('bp_agendamentos.solicitar_alteracao', id_agendamento=id_agendamento))
        
        # Atualiza o agendamento
        agendamento.data_hora = nova_data_hora
        if novo_servico_id:
            agendamento.servico_id = novo_servico_id
        agendamento.status = 'alteracao_pendente'
        agendamento.motivo_alteracao = motivo
        
        db.session.commit()
        flash('Solicitação de alteração enviada com sucesso!', 'success')
        return redirect(url_for('bp_agendamentos.get_agendamentos'))
    
    servicos = Service.query.all()
    return render_template('agendamentos/solicitar_alteracao.html',
                         agendamento=agendamento,
                         servicos=servicos,
                         now=datetime.now())

@bp_agendamentos.route('/<int:id_agendamento>/solicitar-cancelamento', methods=['GET', 'POST'])
@login_required
def solicitar_cancelamento(id_agendamento):
    agendamento = Agendamento.query.get_or_404(id_agendamento)
    
    # Verifica se o usuário tem permissão para cancelar este agendamento
    if current_user.role != 'admin' and agendamento.cliente_id != current_user.id:
        flash("Você não tem permissão para cancelar este agendamento.", "danger")
        return redirect(url_for('bp_agendamentos.get_agendamentos'))
    
    if request.method == 'GET':
        return render_template('agendamentos/solicitar_cancelamento.html',
                             agendamento=agendamento)

    try:
        motivo = request.form.get("motivo")
        if not motivo:
            raise ValueError("Por favor, informe o motivo do cancelamento.")

        # Atualiza o agendamento com status de cancelamento pendente
        agendamento.status = 'cancelamento_pendente'
        agendamento.motivo_cancelamento = motivo

        db.session.commit()
        flash("Solicitação de cancelamento enviada com sucesso! Aguarde a confirmação.", "success")
        return redirect(url_for('bp_agendamentos.get_agendamentos'))

    except ValueError as e:
        flash(str(e), "error")
        return redirect(url_for('bp_agendamentos.solicitar_cancelamento', id_agendamento=id_agendamento))
    except Exception as e:
        db.session.rollback()
        logger.error(f"Erro ao solicitar cancelamento: {e}")
        flash("Erro ao solicitar cancelamento. Tente novamente.", "error")
        return redirect(url_for('bp_agendamentos.solicitar_cancelamento', id_agendamento=id_agendamento))

@bp_agendamentos.route('/<int:id_agendamento>/confirmar-alteracao', methods=['POST'])
@login_required
def confirmar_alteracao(id_agendamento):
    if current_user.role != 'admin':
        flash("Você não tem permissão para confirmar alterações.", "danger")
        return redirect(url_for('bp_agendamentos.get_agendamentos'))
    
    agendamento = Agendamento.query.get_or_404(id_agendamento)
    
    try:
        agendamento.status = 'confirmado'
        db.session.commit()
        flash("Alteração confirmada com sucesso!", "success")
    except Exception as e:
        db.session.rollback()
        logger.error(f"Erro ao confirmar alteração: {e}")
        flash("Erro ao confirmar alteração.", "error")
    
    return redirect(url_for('bp_agendamentos.get_agendamentos'))

@bp_agendamentos.route('/<int:id_agendamento>/confirmar-cancelamento', methods=['POST'])
@login_required
def confirmar_cancelamento(id_agendamento):
    if current_user.role != 'admin':
        flash("Você não tem permissão para confirmar cancelamentos.", "danger")
        return redirect(url_for('bp_agendamentos.get_agendamentos'))
    
    agendamento = Agendamento.query.get_or_404(id_agendamento)
    
    try:
        agendamento.status = 'cancelado'
        db.session.commit()
        flash("Cancelamento confirmado com sucesso!", "success")
    except Exception as e:
        db.session.rollback()
        logger.error(f"Erro ao confirmar cancelamento: {e}")
        flash("Erro ao confirmar cancelamento.", "error")
    
    return redirect(url_for('bp_agendamentos.get_agendamentos'))
