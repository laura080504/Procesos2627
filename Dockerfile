FROM python:3.13-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY main.py .
COPY Servidor ./Servidor
COPY Cliente ./Cliente

ENV HOST=0.0.0.0
ENV PORT=8080
ENV COOKIE_SEGURA=true

CMD ["python", "main.py"]
