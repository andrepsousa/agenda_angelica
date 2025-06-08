from app import create_app
from app.models.models import User
from app.config import db

def create_admin():
    app = create_app()
    with app.app_context():
        # Busca o usuário da Angélica pelo telefone
        telefone = input("Digite o número de telefone da Angélica (com DDD, apenas números): ")
        
        # Formata o telefone para o padrão do WhatsApp (+55)
        telefone_formatado = f"+55{telefone}"
        
        # Busca o usuário
        usuario = User.query.filter_by(telefone=telefone_formatado).first()
        
        if usuario:
            # Atualiza o papel para admin
            usuario.role = 'admin'
            db.session.commit()
            print(f"Usuário {usuario.nome} agora é administrador!")
        else:
            print(f"Usuário com telefone {telefone_formatado} não encontrado.")
            print("Por favor, verifique se o número está correto e se o usuário já está cadastrado.")

if __name__ == '__main__':
    create_admin() 