from app import create_app, db
from flask import Flask

app = create_app()

from app.models import User, Service, Agendamento

with app.app_context():
    db.create_all()
    print("Banco de dados criado com sucesso!")

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
