FROM python:3.13-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY main.py .
COPY servidor ./servidor
COPY cliente ./cliente

ENV HOST=0.0.0.0
ENV PORT=8080

CMD ["python", "main.py"]
