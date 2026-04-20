FROM python:3.12-slim

# Install uv compiler dependencies and system standard tools
RUN apt-get update && apt-get install -y \
    curl \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Install uv package manager
RUN pip install uv
# uv can install directly from pyproject.toml; this avoids a separate requirements.txt

WORKDIR /app

# Copy dependency configuration
COPY pyproject.toml uv.lock ./

# Install dependencies using uv into the system environment to avoid virtualenv wrapper complexity in Docker
RUN uv pip install --system -r pyproject.toml

# Copy remaining codebase 
COPY . .

# Expose API traffic
EXPOSE 8000

HEALTHCHECK CMD curl --fail http://localhost:8000/health || exit 1

# Start endpoint via Uvicorn explicitly bound to API routes
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
