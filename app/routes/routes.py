from flask import Blueprint, request, jsonify
from app.models.models import User, db
from app.models.user_models import listar_usuarios, usuarios_by_id, registrar_user, atualizar_user, deletar_user


main = Blueprint("main", __name__)


@main.route('/usuarios', methods=["GET"])
def get_usuarios():
    usuarios = listar_usuarios()
    print("Usuario in get_usuarios:", usuarios)
    return jsonify(usuarios)


@main.route('/usuarios/<int:id_usuarios>', methods=["GET"])
def get_usuarios_id(id_usuarios):
    try:
        usuarios = usuarios_by_id(id_usuarios)
        return jsonify(usuarios)
    except ValueError as e:
        return jsonify({"erro": str(e)}), 404
    except Exception as e:
        print(f"Erro ao tentar achar id: {e}")
        return jsonify({"erro": "Erro interno no servidor"}), 500


@main.route('/usuarios/novo', methods=["POST"])
def novo_usuario():
    try:
        dados = request.json
        if not dados:
            return jsonify({"Erro": "Requisição inválida. Dados ausentes."}), 400

        novo_user = {
            "nome": dados.get("nome"),
            "endereco": dados.get("endereço"),
            "telefone": dados.get("telefone"),
            "cpf": dados.get("cpf"),
            "data_nascimento": dados.get("data_nascimento")
        }

        resultado = registrar_user(
            novo_user, novo_user["cpf"], novo_user["telefone"])
        return jsonify(resultado), 201
    except KeyError as e:
        return jsonify({"erro": f"Todos os campos devem ser preenchidos!: {str(e)}"}), 400
    except ValueError as e:
        return jsonify({"erro": str(e)}), 400
    except Exception as e:
        print(f"Erro ao tentar registrar usuário: {e}")
        return jsonify({"erro": "Erro interno no servidor"}), 500


@main.route('/usuarios/<int:id_usuarios>/editar', methods=["PUT"])
def atualizar_usuario(id_usuarios):
    try:
        dados = request.json
        if not dados:
            return jsonify({"erro": "Requisição inválida. Os dados não foram enviados."}), 400

        usuario_atualizado = atualizar_user(id_usuarios, dados)

        return jsonify({"message": "Usuário atualizado!", "usuario": usuario_atualizado}), 200

    except KeyError as e:
        return jsonify({"erro": f"Todos os campos devem ser preenchidos!: {str(e)}"}), 400
    except ValueError as e:
        return jsonify({"erro": str(e)}), 400
    except Exception as e:
        print(f"Erro ao tentar atualizar usuário: {e}")
        return jsonify({"erro": "Erro interno no servidor"}), 500


@main.route('/usuarios/<int:id_usuarios>/deletar', methods=["DELETE"])
def deletar_usuario(id_usuarios):
    try:
        usuario_deletado = deletar_user(id_usuarios)

        return jsonify({"message": f"Usuário deletado do sistema.", "usuario": usuario_deletado}), 200

    except ValueError as e:
        return jsonify({"erro": str(e)}), 400
    except Exception as e:
        print(f"Erro ao tentar deletar usuário: {e}")
        return jsonify({"erro": "Erro interno no servidor"}), 500
