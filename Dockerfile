# Stage 1: Build the React Frontend
FROM node:20-alpine AS frontend-builder
WORKDIR /app/frontend
COPY frontend/package*.json ./
RUN npm install
COPY frontend/ ./
RUN npm run build

# Stage 2: Setup Python Backend & Production Server
FROM python:3.11-slim
WORKDIR /app

# Install backend dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt gunicorn

# Copy all necessary Python modules and data
COPY backend/ ./backend/
COPY ingestion/ ./ingestion/
COPY data/ ./data/

# Copy the compiled React build from Stage 1
COPY --from=frontend-builder /app/frontend/dist ./frontend/dist

# Set Python path so the backend can find 'ingestion' package
ENV PYTHONPATH=/app

# Google Cloud Run uses the PORT environment variable (defaults to 8080)
ENV PORT=8080
EXPOSE 8080

# Run using Gunicorn, a production-grade WSGI server
# Note: Google Cloud Run dynamically assigns the port, so we bind to $PORT
CMD exec gunicorn --bind 0.0.0.0:$PORT --workers 1 --threads 8 --timeout 0 --chdir /app/backend "app:create_app()"
