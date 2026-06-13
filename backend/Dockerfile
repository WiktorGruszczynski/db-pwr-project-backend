FROM python:3.12-slim

# Nie buforuj pyc, loguj od razu na stdout (czytelne logi w `docker compose logs`)
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /app

# Najpierw zależności — warstwa cache'uje się, dopóki requirements.txt się nie zmieni
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Kod aplikacji, migracje, seed, entrypoint
COPY . .

# entrypoint.sh mógł zostać zapisany z CRLF na Windows — wymuszamy LF, by /bin/sh go wykonał
RUN sed -i 's/\r$//' entrypoint.sh && chmod +x entrypoint.sh

EXPOSE 8000

ENTRYPOINT ["./entrypoint.sh"]
