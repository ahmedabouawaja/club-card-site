FROM python:3.12-slim

WORKDIR /app

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    FLASK_ENV=production \
    SESSION_COOKIE_SECURE=true \
    RATELIMIT_STORAGE_URI=memory:// \
    DATABASE_URL=sqlite:///instance/club.db \
    BOOTSTRAP_ADMIN_EMAIL=asd \
    BOOTSTRAP_ADMIN_PASSWORD=123 \
    BOOTSTRAP_ADMIN_NAME=Admin

RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

RUN mkdir -p instance \
    && python -c "import secrets; open('/tmp/sk','w').write(secrets.token_hex(32))"

ENV SECRET_KEY=change-me-on-first-boot

EXPOSE 7860

CMD ["sh", "-c", "export SECRET_KEY=${SECRET_KEY:-$(python -c 'import secrets; print(secrets.token_hex(32))')} && gunicorn --bind 0.0.0.0:7860 --workers 2 --threads 4 --timeout 120 run:app"]
