from app import create_app, db
from flask import Flask

app = create_app()

with app.app_context():
    db.create_all()
    print("Banco de dados criado com sucesso!")

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5001, debug=True)
