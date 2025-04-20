FROM python:3.10

# Define o timezone como Brasília
ENV TZ=America/Sao_Paulo

# Define diretório de trabalho
WORKDIR /app

# Copia os arquivos da aplicação
COPY . .

# Instala netcat e o tzdata para configurar timezone
RUN apt-get update && apt-get install -y netcat-openbsd tzdata && \
    ln -fs /usr/share/zoneinfo/America/Sao_Paulo /etc/localtime && \
    dpkg-reconfigure -f noninteractive tzdata

# Instala dependências Python
RUN pip install --no-cache-dir -r requirements.txt

# Comando para iniciar a aplicação
CMD ["python", "app.py"]

