from flask import Blueprint, jsonify

main_bp = Blueprint('main_bp', __name__, url_prefix='/inicio')

@main_bp.route('/')
def index():
    return jsonify({"message": "Bem-vindo a API!"})

@main_bp.route('/sobre')
def sobre():
    return jsonify({"message": "Informações sobre a API"})
