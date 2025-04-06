from flask import Blueprint, jsonify, request

usuarios_bp = Blueprint('usuarios_bp', __name__, url_prefix='/usuarios')

@usuarios_bp.route('/', methods=['GET'])
def listar_usuarios():
    return jsonify({"message": "Lista de usuários"})

@usuarios_bp.route('/usuarios/<int:id>', methods=['GET'])
def obter_usuario(id):
    return jsonify({"message": f"Detalhes do usuário {id}"})

@usuarios_bp.route('/usuarios', methods=['POST'])
def criar_usuario():
    dados = request.json
    return jsonify({"message": "Usuário criado", "dados": dados})
