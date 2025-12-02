FROM python:3.11-slim

WORKDIR /app

# Install uv
COPY --from=ghcr.io/astral-sh/uv:latest /uv /bin/uv

# Copy dependency files
COPY pyproject.toml uv.lock ./

# Install dependencies using uv
RUN uv sync --frozen --no-dev

# Copy application code
COPY main.py ./
COPY core/ ./core/
COPY templates/ ./templates/

# Expose Flask port
EXPOSE 8080

# Set environment variable for Flask
ENV FLASK_APP=main.py
ENV FLASK_ENV=production

# Run the Flask app using uv
CMD ["uv", "run", "flask", "run", "--host", "0.0.0.0", "--port", "8080"]

