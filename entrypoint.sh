#!/bin/sh

# Espera o banco de dados estar pronto
echo "Aguardando o banco de dados iniciar..."

while ! nc -z agenda_db 5432; do
  sleep 1
done

echo "Banco de dados pronto! Iniciando aplicação..."

# Executa o script principal
python run.py
