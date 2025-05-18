from app import create_app
from app.config import db
from app.models import User


def usuario_admin():
    app = create_app()
    with app.app_context():
        telefone = "11985331503"
        cpf = "123.456.789-00"

        usuario_existente = User.query.filter_by(telefone=telefone).first()

        if usuario_existente:
            print("Usuária Angelica já existe.")
            return

        admin = User(
            nome="Angelica",
            telefone=telefone,
            cpf=cpf,
            role="admin"
        )
        admin.set_password("Arroz@123")
        db.session.add(admin)
        db.session.commit()
        print("Usuária Angelica criada com sucesso.")


if __name__ == "__main__":
    usuario_admin()
