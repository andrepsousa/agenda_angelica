from flask import Blueprint, request, jsonify
from app.models.models import User, Service, Agendamento
from datetime import datetime, timedelta
from app import db
from app.models.agendamento_models import (
    agendamento_by_id, list_agendamentos, criar_agendamento_simples,
    criar_agendamentos_recorrentes, delete_agendamento, atualizar_agendamento
)
from app.models.servico_models import (
    criar_servico, delete_servico, listar_servicos,
    atualizar_servico, servicos_by_id
)

main = Blueprint("main", __name__)


@main.route('/')
def home():
    return "Flask rodando"


@main.route('/agendamentos', methods=['GET'])
def get_agendamentos():
    agendamentos = list_agendamentos()
    print("Agendamentos em get_agendamentos:", agendamentos)
    return jsonify(agendamentos)


@main.route('/agendamentos/<int:id_agendamento>', methods=['GET'])
def get_agendamentos_id(id_agendamento):
    try:
        agendamento = agendamento_by_id(id_agendamento)
    except ValueError as e:
        return jsonify({"erro": str(e)}), 404

    return jsonify({
        "id": agendamento["id"],
        "cliente_id": agendamento["cliente_id"],
        "servico_id": agendamento["servico_id"],
        "data_hora": agendamento["data_hora"].strftime("%Y-%m-%d %H:%M:%S"),
        "recorrencia": agendamento["recorrencia"],
        "status": agendamento["status"]
    }), 200


@main.route('/agendamentos', methods=['POST'])
def criar_agendamento():
    data = request.get_json()

    if not isinstance(data, dict):
        return jsonify({
            "erro": "Requisição inválida. Envie um JSON válido."
        }), 400

    try:
        if data.get("recorrencia"):
            agendamentos = criar_agendamentos_recorrentes(data)
        else:
            agendamentos = [criar_agendamento_simples(data)]

        return jsonify({
            "mensagem": "Agendamento(s) realizado(s) com sucesso!",
            "dados": agendamentos
        }), 201
    except ValueError as e:
        return jsonify({"erro": str(e)}), 400


@main.route('/agendamentos/<int:id_agendamento>', methods=['PUT'])
def atualizar_agendamentos(id_agendamento):
    try:
        data = request.json
        if not data:
            return jsonify({"erro": (
                "Requisição inválida. Os dados não foram enviados."
            )}), 400

        agendamento_atualizado = atualizar_agendamento(id_agendamento, data)

        return jsonify({
            "mensagem": "Agendamento atualizado!",
            "agendamento": agendamento_atualizado.to_dict()
        }), 200
    except KeyError as e:
        return jsonify({"erro": "Todos os campos devem ser preenchidos!:"
                        f"{str(e)}"}), 400
    except ValueError as e:
        return jsonify({"erro": str(e)}), 400
    except Exception as e:
        print(f"Erro ao tentar atualizar agendamento: {e}")
        return jsonify({"erro": "Erro interno no servidor"}), 500


@main.route('/agendamentos/<int:id_agendamento>', methods=['DELETE'])
def deletar_agendamento(id_agendamento):
    try:
        agendamento_deletado = delete_agendamento(id_agendamento)

        return jsonify({
            "mensagem": "Agendamento deletado!",
            "agendamento": agendamento_deletado.to_dict()
        }), 200
    except ValueError as e:
        return jsonify({"erro": str(e)}), 400
    except Exception as e:
        print(f"Erro ao tentar deletar agendamento: {e}")
        return jsonify({"erro": "Erro interno no servidor"}), 500


@main.route('/servicos', methods=['GET'])
def get_servicos():
    servicos = listar_servicos()
    print("Serviços em get_servicos:", servicos)
    return jsonify(servicos)


@main.route('/servicos/<int:id_servico>', methods=['GET'])
def get_servicos_id(id_servico):
    try:
        servico = servicos_by_id(id_servico)
        return jsonify(servico), 200

    except ValueError as e:
        print(f"Erro ao obter serviço: {e}")
        return jsonify({"erro": str(e)}), 404


@main.route('/servicos/criar', methods=['POST'])
def set_servico():
    try:
        data = request.json
        if not data:
            return jsonify({
                "erro": "Requisição inválida. Envie um JSON válido"
            }), 400

        novo_servico = {
            "nome": data.get("nome"),
            "descricao": data.get("descricao"),
            "preco": data.get("preco"),
            "status": data.get("status")
        }

        result = criar_servico(novo_servico)
        return jsonify(result), 201
    except KeyError as e:
        return jsonify({
            "erro": f"Todos os campos devem ser preenchidos!: {str(e)}"
        }), 400
    except ValueError as e:
        print(f"Erro ao tentar criar serviço: {e}")
        return jsonify({"erro": str(e)}), 500


@main.route('/servicos/<int:id_servico>/atualizar', methods=['PUT'])
def update_servico(id_servico):
    try:
        data = request.json
        if not data:
            return jsonify({"erro": (
                "Requisição inválida. Os dados não foram enviados."
            )}), 400

        servico_atualizado = atualizar_servico(id_servico, data)

        return jsonify({
            "mensagem": "Serviço atualizado!",
            "serviço": servico_atualizado
        }), 200
    except KeyError as e:
        return jsonify({"erro": "Todos os campos devem ser preenchidos!:"
                        f"{str(e)}"}), 400
    except ValueError as e:
        print(f"Erro ao tentar atualizar agendamento: {e}")
        return jsonify({"erro": "Erro interno no servidor"}), 500


@main.route('/servicos/<int:id_servico>/deletar',  methods=['DELETE'])
def deletar_servico(id_servico):
    try:
        servico_deletado = delete_servico(id_servico)

        return jsonify({
            "mensagem": "Serviço deletado!",
            "serviço": servico_deletado
        }), 200
    except ValueError as e:
        return jsonify({"erro": str(e)}), 400
    except Exception as e:
        print(f"Erro ao tentar  deletar serviço: {e}")
        return jsonify({"erro": "Erro interno no servidor"}), 500
