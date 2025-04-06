from flask import Blueprint, jsonify

servicos_bp = Blueprint('servicos_bp', __name__, url_prefix='/servicos')

@servicos_bp.route('/', methods=['GET'])
def listar_servicos():
    return jsonify({"message": "Lista de serviços"})

@servicos_bp.route('/servicos/<int:id>', methods=['GET'])
def obter_servico(id):
    return jsonify({"message": f"Detalhes do serviço {id}"})
