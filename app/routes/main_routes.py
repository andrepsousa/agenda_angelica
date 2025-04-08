from flask import Blueprint, render_template

main_bp = Blueprint('main_bp', __name__, url_prefix='/inicio')

@main_bp.route('/index')
def index():
    return render_template('index.html')  

@main_bp.route('/sobre')
def sobre():
    return render_template('sobre.html')
