from twilio.rest import Client
import random
from dotenv import load_dotenv
import os
import logging
import re

logging.basicConfig(level=logging.DEBUG)
load_dotenv()

class WhatsAppService:
    def __init__(self):
        self.account_sid = os.getenv("TWILIO_ACCOUNT_SID")
        self.auth_token = os.getenv("TWILIO_AUTH_TOKEN")
        self.twilio_number = 'whatsapp:+14155238886'
        self.client = Client(self.account_sid, self.auth_token)

    def gerar_codigo(self, digitos=6):
        return ''.join([str(random.randint(0, 9)) for _ in range(digitos)])

    def formatar_telefone(self, telefone):
        # Remove todos os caracteres não numéricos
        telefone = re.sub(r'\D', '', telefone)
        
        # Garante que o número tem 10 ou 11 dígitos (com DDD)
        if len(telefone) not in [10, 11]:
            raise ValueError("Número de telefone inválido. Deve conter 10 ou 11 dígitos (com DDD)")
            
        return telefone

    def enviar_codigo(self, numero_destino, codigo):
        try:
            # Formata o número de telefone
            numero_destino = self.formatar_telefone(numero_destino)
            
            mensagem = f"Seu código de ativação é: {codigo}"
            numero_completo = f"whatsapp:+55{numero_destino}"
            
            logging.debug(f"Enviando mensagem para {numero_completo}")
            
            message = self.client.messages.create(
                from_=self.twilio_number,
                body=mensagem,
                to=numero_completo
            )
            
            logging.debug(f"Mensagem enviada com sucesso. SID: {message.sid}")
            return {"codigo": codigo, "sid": message.sid}
            
        except ValueError as ve:
            logging.error(f"Erro de validação do número: {ve}")
            return {"erro": str(ve)}
        except Exception as e:
            logging.error(f"Erro ao enviar mensagem: {e}")
            return {"erro": str(e)}
