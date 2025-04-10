# 📒 Agenda Angélica

Sistema de agendamento simples com Flask e PostgreSQL, containerizado com Docker.

---

## ✅ Requisitos

- [Docker](https://www.docker.com/products/docker-desktop) instalado
- Git instalado (opcionalmente, [GitHub CLI](https://cli.github.com/))

---

## 🚀 Como rodar o projeto

1. **Clone este repositório:**

```bash
git clone https://github.com/seu-usuario/agenda_angelica.git
cd agenda_angelica
```

2. **Suba a aplicação com Docker Compose:**

```bash
docker-compose up --build
```

3. **Acesse no navegador:**

```
http://localhost:5000
```

> A aplicação iniciará automaticamente após o banco estar pronto.

---

## 🛑 Parar a aplicação

Para parar os containers:

```bash
CTRL + C
```

ou

```bash
docker-compose down
```

---

## 📂 Estrutura básica do projeto

```
agenda_angelica/
├── app/                # Código da aplicação Flask
├── Dockerfile          # Instruções de build da imagem do Flask
├── docker-compose.yml  # Orquestração com Flask + PostgreSQL
├── requirements.txt    # Dependências Python
├── entrypoint.sh       # Script de inicialização
└── README.md           # Este arquivo
```

---

## 🛠️ Tecnologias utilizadas

- Python 3.10
- Flask
- PostgreSQL
- Docker & Docker Compose

---
