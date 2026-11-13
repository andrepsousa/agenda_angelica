# Agenda Angélica

Aplicação web para organizar agendamentos de serviços, desenvolvida em equipe como projeto acadêmico. Reúne cadastro de clientes e serviços, consulta de horários e acompanhamento de agendamentos em uma aplicação com **Python, Flask e PostgreSQL**, executada com **Docker Compose**.

## O que o projeto faz

- Cadastro e autenticação de usuários com código de verificação enviado por WhatsApp, via Twilio.
- Cadastro, consulta, edição e exclusão de serviços.
- Criação de agendamentos com cliente, serviço, data, horário e observações.
- Consulta de disponibilidade e criação de agendamentos recorrentes.
- Histórico de agendamentos e consulta dos atendimentos do dia.
- Solicitações de alteração e cancelamento, com fluxos de confirmação administrativa.
- Fluxos distintos para clientes e administradores.

As funcionalidades acima estão presentes no código. O projeto tem finalidade acadêmica e ainda precisa de revisões antes de uso em produção.

## Minha participação — Frank Ribeiro (@FrankRibe)

Participei do desenvolvimento em equipe, com contribuições no backend, na interface de agendamento e na configuração do ambiente. Minhas entregas registradas no histórico incluem:

| Área | Contribuição | Registro |
| --- | --- | --- |
| Estrutura da aplicação | Criação da estrutura inicial e separação das rotas para organizar o projeto. | [Estrutura inicial](https://github.com/andrepsousa/agenda_angelica/commit/d699136aafdff0be260ee2dc88dfc66ddde93505) · [Organização de rotas](https://github.com/andrepsousa/agenda_angelica/commit/26cf88e2d06b2b137f46316065d3a0c7f8e2af0e) |
| Ambiente de execução | Integração de Flask e PostgreSQL com Docker Compose e ajuste do fuso horário dos contêineres para America/Sao_Paulo. | [Integração com Docker](https://github.com/andrepsousa/agenda_angelica/commit/d7a582cf91722af753152036124dd28c416f3d28) · [Fuso horário](https://github.com/andrepsousa/agenda_angelica/commit/be91b294b6ed147824804d72f051b52610f46c5e) |
| Regras de agendamento | Ajustes no backend para aceitar horários inteiros entre 10h e 18h. | [Regra de horários](https://github.com/andrepsousa/agenda_angelica/commit/0c39b8e9f19caa02183f59445b5460e766af0d16) |
| Integração entre formulário e backend | Adaptação do formulário para receber data e hora separadamente e combiná-las para o campo datetime esperado pelo backend. | [Data e horário](https://github.com/andrepsousa/agenda_angelica/commit/1465691e09f358f77448a8e1de1267b6ffe93345) |
| Informações do agendamento | Inclusão do campo de observações e ajustes na exibição de data, hora, clientes e serviços. | [Observações e datas](https://github.com/andrepsousa/agenda_angelica/commit/d5fcff7f5faae35326dc1f92df93847f46ab31a1) · [Clientes e serviços](https://github.com/andrepsousa/agenda_angelica/commit/73faf424c7a1e0c43c679cd5ccb16bb9868a822a) |
| Interface | Estilização da tela de agendamento e inclusão de botão para voltar. | [Estilização](https://github.com/andrepsousa/agenda_angelica/commit/8a83980bee6bb9f7f4d15d34167e210791aa5cb0) · [Navegação](https://github.com/andrepsousa/agenda_angelica/commit/3423ed30dfb7918d80da58a921da44abce777c8e) |

Essas contribuições envolveram organização de uma aplicação Flask, integração com banco relacional, configuração de contêineres e tratamento de datas e horários entre formulário, backend e banco de dados.

O projeto é coletivo: esta seção delimita minha participação e não atribui a mim a autoria de todas as funcionalidades.

[Ver histórico de contribuições de FrankRibe](https://github.com/andrepsousa/agenda_angelica/commits/master/?author=FrankRibe)

## Tecnologias

| Camada | Tecnologias |
| --- | --- |
| Backend | Python 3.10 na imagem Docker, Flask e Blueprints |
| Interface | HTML, CSS e templates Jinja2 |
| Persistência | PostgreSQL, SQLAlchemy e Flask-SQLAlchemy |
| Autenticação | Flask-Login e verificação de código via Twilio/WhatsApp |
| Evolução do banco | Flask-Migrate e Alembic |
| Ambiente | Docker, Docker Compose e python-dotenv |

## Organização

```text
agenda_angelica/
├── app/
│   ├── __init__.py       # Criação e configuração da aplicação
│   ├── config.py        # Instâncias de extensões
│   ├── http/            # Integração com WhatsApp
│   ├── models/          # Modelos e operações de persistência
│   ├── routes/          # Rotas de autenticação, serviços e agendamentos
│   ├── static/          # Estilos e recursos da interface
│   └── templates/       # Páginas renderizadas com Jinja2
├── migrations/          # Histórico de migrações do banco
├── scripts/             # Scripts auxiliares
├── Dockerfile
├── docker-compose.yml
├── entrypoint.sh         # Aguarda o banco e inicia run.py
├── requirements.txt
└── run.py               # Inicialização da aplicação
```

## Executar localmente

### Requisitos

- Git.
- Docker com Docker Compose.
- Conta Twilio com WhatsApp Sandbox configurado e destinatário autorizado para testar cadastro e login.

O fluxo atual de acesso depende do envio de códigos pelo WhatsApp. Não há modo de demonstração independente dessa integração documentado no projeto.

### 1. Obter o código

```bash
git clone https://github.com/andrepsousa/agenda_angelica.git
cd agenda_angelica
```

### 2. Configurar o ambiente

Crie um arquivo `.env` na raiz, com valores próprios:

```dotenv
SECRET_KEY=substitua_por_uma_chave_aleatoria
JWT_SECRET_KEY=substitua_por_outra_chave_aleatoria
TWILIO_ACCOUNT_SID=seu_account_sid
TWILIO_AUTH_TOKEN=seu_auth_token
```

Gere valores aleatórios distintos para as duas chaves. Não publique o arquivo `.env` nem credenciais reais.

O Compose já define `DATABASE_URL` para conectar o serviço `web` ao PostgreSQL. As credenciais do banco presentes no Compose destinam-se ao ambiente local de desenvolvimento.

O remetente do WhatsApp está definido em `app/http/whatsapp.py`; confira se corresponde ao Sandbox da sua conta. No formulário, o código atual espera telefone brasileiro com DDD, sem o prefixo +55.

### 3. Iniciar os serviços

Em Linux ou macOS, garanta a permissão de execução do script:

```bash
chmod +x entrypoint.sh
```

Inicie a aplicação:

```bash
docker compose up --build
```

Abra [http://localhost:5000](http://localhost:5000).

O script de entrada aguarda a porta do banco ficar disponível e executa `run.py`. Na inicialização, o código chama `db.create_all()` para criar tabelas ausentes; isso não substitui migrações para atualizar um banco já existente.

### 4. Encerrar

```bash
docker compose down
```

O volume `data_db` preserva os dados entre execuções.

### Observações sobre o ambiente

- As portas 5000 e 5432 precisam estar disponíveis.
- O Compose monta `/etc/timezone` e `/etc/localtime` do host. Conforme o sistema operacional, esses caminhos podem precisar de adaptação.
- O PostgreSQL está configurado sem versão fixa na imagem. A compatibilidade depende da versão obtida; recomenda-se fixar e validar uma versão antes de distribuir um ambiente reproduzível.
- O servidor inicia com `debug=True`, adequado apenas a desenvolvimento.
- Estas instruções foram revisadas a partir dos arquivos do repositório; a execução completa não foi validada nesta revisão de documentação.

## Próximas melhorias

- Revisar autenticação e autorização em todas as rotas, especialmente detalhes e exclusão de agendamentos.
- Remover o ambiente virtual `venv/` versionado e manter apenas a declaração de dependências.
- Adicionar testes de disponibilidade, recorrência e permissões de acesso.
- Disponibilizar configuração de exemplo e um modo de demonstração com dados fictícios.
- Revisar e padronizar a aplicação das migrações do banco.
- Incluir capturas de tela e um vídeo curto do fluxo de agendamento.

## Equipe e licença

Projeto acadêmico desenvolvido em equipe, hospedado no repositório de [andrepsousa](https://github.com/andrepsousa), com participação de [FrankRibe](https://github.com/FrankRibe) e demais colaboradores.

Distribuído sob a [licença MIT](LICENSE), conforme os créditos preservados no arquivo de licença.
