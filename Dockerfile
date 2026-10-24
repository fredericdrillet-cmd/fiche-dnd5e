# Image conteneur (Hugging Face Spaces « Docker », Fly.io, Koyeb, Railway…)
FROM python:3.12-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY . .
ENV PORT=7860
EXPOSE 7860
CMD gunicorn app:app --workers 2 --threads 4 --timeout 60 --bind 0.0.0.0:$PORT
