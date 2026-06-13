# ── Etap 1: build SPA ──────────────────────────────────────────
FROM node:20-alpine AS build
WORKDIR /app

# Zależności (cache na podstawie package-lock.json)
COPY package*.json ./
RUN npm ci

# Kod + build produkcyjny do /app/dist
COPY . .
RUN npm run build

# ── Etap 2: serwowanie przez nginx ─────────────────────────────
FROM nginx:alpine
# Konfiguracja: serwuje SPA i reverse-proxy /api/ -> backend:8000
COPY nginx.conf /etc/nginx/conf.d/default.conf
COPY --from=build /app/dist /usr/share/nginx/html

EXPOSE 80
