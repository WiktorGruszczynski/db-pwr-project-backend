#!/bin/sh
set -e

# ─────────────────────────────────────────────
# Czekamy aż baza przyjmie połączenia. Compose z healthcheckiem zwykle
# startuje backend dopiero gdy DB jest zdrowa, ale ta pętla działa też
# w composie bez bazy (wtedy łączymy się z zewnętrznym Postgresem).
# Używa DB_PASSWORD (psycopg2 — tak jak app/seed); migrate.py czyta DB_PASS,
# dlatego compose ustawia OBIE zmienne na tę samą wartość.
# ─────────────────────────────────────────────
echo "[entrypoint] Czekam na bazę ${DB_HOST}:${DB_PORT}..."
until python -c "import os, psycopg2; psycopg2.connect(host=os.getenv('DB_HOST'), port=os.getenv('DB_PORT'), dbname=os.getenv('DB_NAME'), user=os.getenv('DB_USER'), password=os.getenv('DB_PASSWORD')).close()" 2>/dev/null; do
  echo "[entrypoint] Baza jeszcze nie odpowiada — ponawiam za 1s..."
  sleep 1
done
echo "[entrypoint] Baza dostępna."

if [ "${RUN_MIGRATIONS:-true}" = "true" ]; then
  echo "[entrypoint] Nakładam migracje (migrate.py apply)..."
  python migrate.py apply
fi

if [ "${SEED_DB:-false}" = "true" ]; then
  echo "[entrypoint] Seeduję bazę (seed.py — idempotentnie)..."
  python seed.py
fi

echo "[entrypoint] Start uvicorn na 0.0.0.0:8000"
exec uvicorn app.main:app --host 0.0.0.0 --port 8000
