from flask import render_template, request, redirect, url_for, flash
from flask import Blueprint, request, jsonify, render_template, redirect, url_for, flash
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
from app.models.user_models import listar_usuarios, usuarios_by_id, registrar_user, atualizar_user, deletar_user


main = Blueprint("main", __name__)

# Página Inicial
@main.route('/')
def index():
    hoje = datetime.today().date()

    agendamentos_hoje = Agendamento.query.filter(Agendamento.data_hora.cast(db.Date) == hoje).all()
    servicos = Service.query.all()
    return render_template('index.html', agendamentos=agendamentos_hoje, servicos=servicos)

# Agendamentos
@main.route('/agendamentos', methods=['GET'])
def get_agendamentos():
    agendamentos = list_agendamentos()
    return render_template('agendamentos/list.html', agendamentos=agendamentos)


@main.route('/agendamentos/<int:id_agendamento>', methods=['GET'])
def get_agendamentos_id(id_agendamento):
    try:
        agendamento = agendamento_by_id(id_agendamento)
        return render_template('agendamentos/detail.html', agendamento=agendamento)
    except ValueError as e:
        return render_template('agendamentos/error.html', erro=str(e)), 404


@main.route('/agendamentos/novo', methods=['GET', 'POST'])
def criar_agendamento():
    if request.method == 'GET':
        clientes = User.query.all()
        servicos = Service.query.filter_by(status=True).all()
        return render_template('agendamentos/create.html', clientes=clientes, servicos=servicos)

    # Pegando os dados do formulário
    cliente_id = request.form.get("cliente_id")
    servico_id = request.form.get("servico_id")
    # Data no formato 'YYYY-MM-DDTHH:MM'
    data_hora_str = request.form.get("data_hora")
    recorrencia = request.form.get("recorrencia", None)
    # Número de recorrências, padrão 1
    num_recorrencias = int(request.form.get("num_recorrencias", 1))
    status = request.form.get("status", "ativo")

    try:
        # Converte a data_hora para o formato datetime
        data_hora = datetime.strptime(data_hora_str, '%Y-%m-%dT%H:%M')

        data = {
            "cliente_id": cliente_id,
            "servico_id": servico_id,
            "data_hora": data_hora,
            "recorrencia": recorrencia,
            "num_recorrencias": num_recorrencias,
            "status": status
        }

        if recorrencia:
            agendamentos = criar_agendamentos_recorrentes(data)
        else:
            agendamentos = [criar_agendamento_simples(data)]

        return render_template('agendamentos/success.html', agendamentos=agendamentos)

    except ValueError as e:
        return render_template('agendamentos/create.html', erro="Erro no formato da data. Tente novamente.", clientes=User.query.all(), servicos=Service.query.filter_by(status=True).all())


@main.route('/agendamentos/<int:id_agendamento>/editar', methods=['GET', 'POST'])
def editar_agendamento(id_agendamento):
    agendamento = Agendamento.query.get(id_agendamento)

    if not agendamento:
        return jsonify({"erro": "Agendamento não encontrado!"}), 404

    if request.method == 'GET':
        # Exibe o formulário de edição com os dados do agendamento
        return render_template('agendamentos/edit.html', agendamento=agendamento)

    if request.method == 'POST':
        # Atualiza o agendamento com os novos dados
        try:
            # Supondo que você tenha os campos `data_hora`, `recorrencia` e `status` no formulário
            agendamento.data_hora = request.form['data_hora']
            agendamento.recorrencia = request.form['recorrencia']
            agendamento.status = request.form['status']

            # Salva as alterações no banco de dados
            db.session.commit()

            # Redireciona para a página inicial ou para onde desejar
            return redirect(url_for('main.index'))
        except Exception as e:
            db.session.rollback()
            return jsonify({"erro": "Erro ao atualizar o agendamento!"}), 500


@main.route('/agendamentos/<int:id_agendamento>/delete', methods=['GET', 'POST'])
def deletar_agendamento(id_agendamento):
    try:
        print(f"Tentando acessar agendamento {id_agendamento}")  # 🟢 Debug
        agendamento = Agendamento.query.get(id_agendamento)

        if not agendamento:
            print("Erro: Agendamento não encontrado!")  # 🟢 Debug
            raise ValueError("Agendamento não encontrado!")

        if request.method == 'POST':
            print(f"Deletando agendamento {id_agendamento}")  # 🟢 Debug
            delete_agendamento(id_agendamento)
            return redirect(url_for('main.get_agendamentos'))

        return render_template('agendamentos/delete.html', agendamento=agendamento)

    except ValueError as e:
        print(f"Erro de valor: {e}")  # 🟢 Debug
        return render_template('agendamentos/error.html', erro=str(e)), 404
    except Exception as e:
        print(f"Erro ao tentar deletar agendamento: {e}")  # 🟢 Debug
        return render_template('agendamentos/error.html', erro="Erro interno no servidor"), 500

# Serviços
@main.route('/servicos', methods=['GET'])
def list_servicos():
    servicos = listar_servicos()
    return render_template('servicos/list.html', servicos=servicos)


@main.route('/servicos/<int:id_servico>', methods=['GET'])
def service_detail(id_servico):
    try:
        servico = servicos_by_id(id_servico)
        return render_template('servicos/detail.html', servico=servico)
    except ValueError as e:
        print(f"Erro ao obter serviço: {e}")
        return jsonify({"erro": str(e)}), 404


@main.route('/servicos/novo', methods=['GET', 'POST'])
def set_servico():
    if request.method == 'POST':
        # Recebe os dados do formulário
        nome = request.form.get("nome")
        descricao = request.form.get("descricao", "")
        preco = request.form.get("preco")
        # Checkbox envia 'on' quando marcado
        status = request.form.get("status") == "on"

        # Valida se os campos obrigatórios foram preenchidos
        if not nome or not preco:
            flash("O nome e o preço são obrigatórios.", "error")
            return redirect(url_for('main.set_servico'))

        # Criação do novo serviço
        novo_servico = {
            "nome": nome,
            "descricao": descricao,
            "preco": float(preco),
            "status": status
        }

        try:
            # Chama a função para criar o serviço no banco de dados
            criar_servico(novo_servico)
            flash("Serviço criado com sucesso!", "success")
            # Redireciona para a lista de serviços
            return redirect(url_for('main.list_servicos'))
        except ValueError as e:
            flash(f"Erro ao tentar criar serviço: {e}", "error")
            return redirect(url_for('main.set_servico'))

    # Exibe o formulário de criação do serviço
    return render_template('servicos/create.html')


@main.route('/servicos/<int:id_servico>/edit', methods=['GET', 'PUT'])
def editar_servico(id_servico):
    if request.method == 'GET':
        # Carregar os dados do serviço para exibir no formulário
        try:
            servico = servicos_by_id(id_servico)
            return render_template('servicos/edit.html', servico=servico)
        except ValueError as e:
            print(f"Erro ao obter serviço: {e}")
            return jsonify({"erro": str(e)}), 404

    elif request.method == 'PUT':
        # Atualizar o serviço com os dados enviados
        try:
            data = request.json
            if not data:
                return jsonify({"erro": "Requisição inválida. Os dados não foram enviados."}), 400

            servico_atualizado = atualizar_servico(id_servico, data)

            return jsonify({
                "mensagem": "Serviço atualizado!",
                "serviço": servico_atualizado
            }), 200
        except KeyError as e:
            return jsonify({"erro": "Todos os campos devem ser preenchidos! " + f"{str(e)}"}), 400
        except ValueError as e:
            print(f"Erro ao tentar atualizar serviço: {e}")
            return jsonify({"erro": "Erro interno no servidor"}), 500


@main.route('/servicos/<int:id_servico>/delete', methods=['GET', 'POST'])
def deletar_servico(id_servico):
    if request.method == 'GET':
        try:
            servico = servicos_by_id(id_servico)
            return render_template('servicos/delete.html', servico=servico)
        except ValueError as e:
            flash(f"Erro: {str(e)}", 'error')
            return redirect(url_for('main.list_servicos'))

    elif request.method == 'POST':  # Alterado de DELETE para POST
        try:
            delete_servico(id_servico)
            flash('Serviço deletado com sucesso!', 'success')
            return redirect(url_for('main.list_servicos'))
        except ValueError as e:
            flash(f"Erro: {str(e)}", 'error')
        except Exception as e:
            flash("Erro interno ao tentar deletar o serviço", 'error')

        return redirect(url_for('main.list_servicos'))

#Usuários
@main.route('/usuarios', methods=["GET"])
def get_usuarios():
    usuarios = listar_usuarios()
    return render_template('user/list.html', usuarios=usuarios)


@main.route('/usuarios/<int:id_usuarios>', methods=["GET"])
def get_usuarios_id(id_usuarios):
    try:
        usuario = usuarios_by_id(id_usuarios)
        return render_template('user/detail.html', usuario=usuario)
    except ValueError as e:
        return render_template('user/error.html', erro=str(e)), 404
    except Exception as e:
        print(f"Erro ao tentar achar id: {e}")
        return render_template('user/error.html', erro="Erro interno no servidor"), 500


@main.route('/usuarios/novo', methods=["GET", "POST"])
def novo_usuario():
    if request.method == "GET":
        return render_template("user/create.html")

    try:
        dados = request.form  # Captura os dados do formulário enviado via POST

        if not dados:
            return render_template("user/create.html", erro="Requisição inválida. Dados ausentes.")

        novo_user = {
            "nome": dados.get("nome"),
            "endereco": dados.get("endereco"),
            "telefone": dados.get("telefone"),
            "cpf": dados.get("cpf"),
            "data_nascimento": dados.get("data_nascimento")
        }

        resultado = registrar_user(
            novo_user, novo_user["cpf"], novo_user["telefone"])
        return render_template("user/create.html", mensagem=resultado["message"])

    except KeyError as e:
        return render_template("user/create.html", erro=f"Todos os campos devem ser preenchidos!: {str(e)}")
    except ValueError as e:
        return render_template("user/create.html", erro=str(e))
    except Exception as e:
        print(f"Erro ao tentar registrar usuário: {e}")
        return render_template("user/create.html", erro="Erro interno no servidor")


@main.route('/usuarios/<int:id_usuarios>/update', methods=["GET", "POST"])
def editar_usuario(id_usuarios):
    usuario = User.query.get(id_usuarios)
    if not usuario:
        return jsonify({"erro": "Usuário não encontrado."}), 404

    if request.method == "GET":
        return render_template("user/edit.html", usuario=usuario)

    try:
        dados = request.form  # Dados do formulário via POST

        if not dados:
            return render_template("user/edit.html", erro="Requisição inválida. Dados ausentes.", usuario=usuario)

        usuario_atualizado = {
            "nome": dados.get("nome"),
            "endereco": dados.get("endereco"),
            "telefone": dados.get("telefone"),
            "cpf": dados.get("cpf"),
            "data_nascimento": dados.get("data_nascimento")
        }

        resultado = atualizar_user(id_usuarios, usuario_atualizado)
        return render_template("user/edit.html", mensagem="Usuário atualizado com sucesso!", usuario=resultado)

    except KeyError as e:
        return render_template("user/edit.html", erro=f"Todos os campos devem ser preenchidos!: {str(e)}", usuario=usuario)
    except ValueError as e:
        return render_template("user/edit.html", erro=str(e), usuario=usuario)
    except Exception as e:
        print(f"Erro ao tentar atualizar usuário: {e}")
        return render_template("user/edit.html", erro="Erro interno no servidor", usuario=usuario)


@main.route('/usuarios/<int:id_usuarios>/delete', methods=["GET", "POST"])
def deletar_usuario(id_usuarios):
    usuario = User.query.get(id_usuarios)
    if not usuario:
        return render_template("user/delete.html", erro="Usuário não encontrado.")

    if request.method == "GET":
        return render_template("user/delete.html", usuario=usuario)

    try:
        usuario_deletado = deletar_user(id_usuarios)
        # Retorne apenas a mensagem de sucesso, sem a variável 'usuario' já deletada.
        return render_template("user/delete.html", mensagem=f"Usuário {usuario_deletado['nome']} deletado com sucesso.")

    except ValueError as e:
        return render_template("user/delete.html", erro=str(e), usuario=usuario)
    except Exception as e:
        print(f"Erro ao tentar deletar usuário: {e}")
        return render_template("user/delete.html", erro="Erro interno no servidor", usuario=usuario)
