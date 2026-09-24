FROM python:3.12-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .
RUN useradd --create-home --shell /usr/sbin/nologin appuser \
    && mkdir -p /data /app/media \
    && chmod +x /app/docker-entrypoint.sh \
    && chown -R appuser:appuser /app /data

USER appuser

EXPOSE 8000

CMD ["/app/docker-entrypoint.sh"]
