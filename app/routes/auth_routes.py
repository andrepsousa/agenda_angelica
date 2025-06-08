from flask import (
    Blueprint, request, flash, redirect, url_for, render_template, session
)
from flask_login import login_user, logout_user, login_required
from app.models.models import User
from app.config import db
from datetime import timezone
from app.http.whatsapp import WhatsAppService
import logging
import re

logging.basicConfig(level=logging.DEBUG)
auth_bp = Blueprint('auth_bp', __name__, url_prefix='/auth')
whatsapp_service = WhatsAppService()

def limpar_telefone(telefone):
    return re.sub(r'\D', '', telefone)

@auth_bp.route('/send-code', methods=['GET', 'POST'])
def send_code():
    if request.method == 'POST':
        telefone = limpar_telefone(request.form.get('telefone', '').strip())
        
        if not telefone:
            flash("Por favor, informe um número de telefone válido", "danger")
            return redirect(url_for('auth_bp.send_code'))
            
        user = User.query.filter_by(telefone=telefone).first()
        if not user:
            flash("Usuário não encontrado", "danger")
            return redirect(url_for('auth_bp.send_code'))

        try:
            codigo = whatsapp_service.gerar_codigo()
            resultado = whatsapp_service.enviar_codigo(telefone, codigo)

            if "erro" in resultado:
                flash(f"Erro ao enviar código via WhatsApp: {resultado['erro']}", "danger")
                return redirect(url_for('auth_bp.send_code'))

            # Só atualiza e salva se envio for sucesso
            user.gerar_codigo_verificacao(codigo)
            db.session.commit()
            
            session['telefone'] = telefone
            flash("Código enviado via WhatsApp! Verifique seu celular.", "info")
            return redirect(url_for('auth_bp.verify_code'))
            
        except Exception as e:
            db.session.rollback()
            logging.error(f"Erro ao enviar código: {e}")
            flash("Erro interno ao enviar código. Tente novamente.", "danger")
            return redirect(url_for('auth_bp.send_code'))

    return render_template('auth/login.html')

@auth_bp.route('/verify-code', methods=['GET', 'POST'])
def verify_code():
    telefone = session.get('telefone')

    if not telefone:
        flash("Sessão expirada. Por favor, inicie o processo novamente.", "warning")
        return redirect(url_for('auth_bp.send_code'))

    if request.method == 'POST':
        codigo = request.form.get('codigo', '').strip()
        
        if not codigo:
            flash("Por favor, informe o código recebido", "danger")
            return redirect(url_for('auth_bp.verify_code'))

        user = User.query.filter_by(telefone=telefone).first()
        if not user:
            logging.error(f"Usuário com telefone {telefone} não encontrado")
            flash("Erro: usuário não encontrado. Por favor, tente novamente.", "danger")
            return redirect(url_for('auth_bp.send_code'))

        if user.verificar_codigo(codigo):
            user.codigo_verificacao = None
            user.validade_codigo = None
            db.session.commit()
            login_user(user)
            session.pop('telefone', None)
            flash("Login realizado com sucesso!", "success")
            return redirect(url_for('main_bp.index'))
        else:
            flash("Código inválido ou expirado. Tente novamente.", "danger")

    return render_template('auth/verify_code.html', telefone=telefone)

@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        nome = request.form.get('nome', '').strip()
        telefone = limpar_telefone(request.form.get('telefone', '').strip())
        cpf = re.sub(r'\D', '', request.form.get('cpf', '').strip())

        if not all([nome, telefone, cpf]):
            flash("Por favor, preencha todos os campos corretamente", "danger")
            return redirect(url_for('auth_bp.register'))

        # Verifica se já existe usuário com esse telefone ou CPF
        existing_user_telefone = User.query.filter_by(telefone=telefone).first()
        existing_user_cpf = User.query.filter_by(cpf=cpf).first()
        
        if existing_user_telefone or existing_user_cpf:
            flash("Telefone ou CPF já cadastrado. Tente fazer login.", "warning")
            return redirect(url_for('auth_bp.send_code'))

        try:
            # Cria novo usuário
            user = User(nome=nome, telefone=telefone, cpf=cpf)
            codigo = whatsapp_service.gerar_codigo()
            user.gerar_codigo_verificacao(codigo)
            
            db.session.add(user)
            db.session.commit()

            resultado = whatsapp_service.enviar_codigo(telefone, codigo)
            
            if "erro" in resultado:
                db.session.delete(user)
                db.session.commit()
                flash(f"Erro ao enviar código via WhatsApp: {resultado['erro']}", "danger")
                return redirect(url_for('auth_bp.register'))

            session['telefone'] = telefone
            flash("Código de confirmação enviado via WhatsApp! Verifique seu celular.", "info")
            return redirect(url_for('auth_bp.verify_code'))

        except Exception as e:
            db.session.rollback()
            logging.error(f"Erro ao cadastrar usuário: {e}")
            flash("Erro ao cadastrar usuário. Tente novamente.", "danger")
            return redirect(url_for('auth_bp.register'))

    return render_template('auth/register.html')

@auth_bp.route('/logout')
@login_required
def logout():
    logout_user()
    session.pop('telefone', None)
    flash('Você saiu.', 'info')
    return redirect(url_for('auth_bp.send_code'))

