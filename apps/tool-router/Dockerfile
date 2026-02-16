FROM python:3.12-slim

WORKDIR /app

# Create non-root user
RUN groupadd --gid 1000 appuser && \
    useradd --uid 1000 --gid 1000 --shell /bin/bash --create-home appuser

# Copy requirements and install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy package files for installation
COPY apps/tool-router/pyproject.toml apps/tool-router/
COPY apps/tool-router/src apps/tool-router/src

# Install package
RUN pip install --no-cache-dir apps/tool-router

# Change ownership to non-root user
RUN chown -R appuser:appuser /app

# Switch to non-root user
USER appuser

ENV PYTHONPATH=/app

HEALTHCHECK --interval=30s --timeout=3s --start-period=5s --retries=3 \
  CMD python3 -c "import tool_router; import sys; sys.exit(0)"

CMD ["python3", "-m", "tool_router"]
