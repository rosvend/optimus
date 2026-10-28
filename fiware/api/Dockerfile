# Built from the repo root (see docker-compose.yml) so it can include the dashboard
FROM node:22-alpine AS dashboard
WORKDIR /dashboard
COPY dashboard/package.json dashboard/package-lock.json ./
RUN npm ci
COPY dashboard/ ./
RUN npm run build

FROM python:3.13-slim
WORKDIR /app
COPY fiware/api/requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt
COPY fiware/api/*.py ./
COPY --from=dashboard /dashboard/dist ./static
ENV STATIC_DIR=/app/static
EXPOSE 8000
# One process: it keeps the "subscription exists" flag; threads handle concurrent requests
CMD ["gunicorn", "--bind", "0.0.0.0:8000", "--workers", "1", "--threads", "8", "--access-logfile", "-", "app:from_env()"]
