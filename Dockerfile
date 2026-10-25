# Multi-stage Dockerfile for Agentic DevOps AI
FROM python:3.11-slim as builder

WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    curl \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir --user -r requirements.txt

FROM python:3.11-slim as runner

WORKDIR /app

# Create non-root user for security
RUN groupadd -g 10001 devops && \
    useradd -u 10001 -g devops -m devops

COPY --from=builder /root/.local /home/devops/.local
COPY --chown=devops:devops . .

ENV PATH=/home/devops/.local/bin:$PATH \
    PYTHONUNBUFFERED=1 \
    DEV_AGENT_DRY_RUN=true

USER devops

ENTRYPOINT ["python", "-m", "agentic_devops.cli"]
CMD ["triage", "--service", "payment-service", "--severity", "critical"]
