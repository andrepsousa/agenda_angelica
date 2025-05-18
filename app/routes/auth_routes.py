from flask import (
    Blueprint, render_template, request, flash,
    redirect, url_for, session
)
from flask_login import login_user, logout_user, login_required, current_user
from app.models.models import User
from app.config import db

auth_bp = Blueprint('auth_bp', __name__, url_prefix='/auth')


@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        nome = request.form['nome']
        telefone = request.form['telefone']
        cpf = request.form['cpf']
        senha = request.form['senha']

        if User.query.filter_by(telefone=telefone).first() or User.query.filter_by(cpf=cpf).first():
            flash('Telefone ou CPF já cadastrado', 'danger')
        else:
            user = User(nome=nome, telefone=telefone, cpf=cpf)
            user.set_password(senha)
            db.session.add(user)
            db.session.commit()
            flash('Conta criada! Faça login.', 'success')
            return redirect(url_for('auth_bp.login'))
    return render_template('auth/register.html')


@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        telefone = request.form['telefone']
        senha = request.form['senha']
        user = User.query.filter_by(telefone=telefone).first()

        if user and user.check_password(senha):
            login_user(user)
            flash('Bem-vindo de volta!', 'success')
            return redirect(url_for('main_bp.index'))
        else:
            flash('Telefone ou senha incorretos', 'danger')

    return render_template('auth/login.html')


@auth_bp.route('/logout')
@login_required
def logout():
    logout_user()
    flash('Você saiu.', 'info')
    return redirect(url_for('auth_bp.login'))
