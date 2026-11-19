FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1 DATA_DIR=/data DJANGO_DEBUG=0
WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .
RUN python manage.py collectstatic --noinput \
 && useradd -u 1000 -m store && mkdir -p /data && chown -R store:store /data
USER store

EXPOSE 8000

HEALTHCHECK --interval=30s --timeout=5s --start-period=15s --retries=3 \
  CMD python -c "import urllib.request,sys; sys.exit(0 if urllib.request.urlopen('http://127.0.0.1:8000/healthz', timeout=4).status == 200 else 1)"

# Apply database updates, then start the web server (2 processes x 4 threads).
CMD ["sh", "-c", "python manage.py migrate --noinput && exec gunicorn config.wsgi:application -w 2 -k gthread --threads 4 --timeout 60 -b 0.0.0.0:8000 --access-logfile -"]
