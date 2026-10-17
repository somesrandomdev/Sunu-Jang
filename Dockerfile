# Image applicative Sunu Jàng (l'inférence tourne dans le service `ollama` de docker-compose).
FROM python:3.11-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    GRADIO_SERVER_NAME=0.0.0.0

WORKDIR /srv/app

COPY requirements.txt ./
RUN pip install -r requirements.txt

COPY app/ app/
COPY scripts/ scripts/

EXPOSE 7860

CMD ["python", "-m", "app.ui"]
