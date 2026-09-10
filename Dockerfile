FROM openpolicyagent/opa:latest-static AS opa
FROM python:3.11-slim

# Copy OPA binary
COPY --from=opa /opa /usr/local/bin/opa

WORKDIR /app

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy all project files
COPY . .

# Start OPA in background and run FastAPI
CMD opa run --server --addr localhost:8181 /app/rules/ & \
    uvicorn app.main:app --host 0.0.0.0 --port 10000