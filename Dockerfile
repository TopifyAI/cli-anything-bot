FROM python:3.12-slim

RUN apt-get update && apt-get install -y git && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Copy bot code
COPY bot/ ./bot/

# Copy HARNESS.md methodology (referenced by builder.py)
COPY cli-anything-plugin/HARNESS.md ./cli-anything-plugin/HARNESS.md

RUN pip install --no-cache-dir -r bot/requirements.txt

WORKDIR /app/bot

CMD ["python", "main.py"]
