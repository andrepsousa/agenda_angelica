FROM python:3.10

WORKDIR /app

COPY . .

RUN apt-get update && apt-get install -y netcat-openbsd

RUN pip install --no-cache-dir -r requirements.txt

CMD ["python", "app.py"]
