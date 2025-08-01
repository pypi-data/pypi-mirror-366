# Smithery does not work with base images such as ghcr.io/astral-sh/uv:python3.12-bookworm-slim
FROM python:3.12-alpine3.22
# Install system dependencies
RUN apk add --no-cache gcc musl-dev linux-headers git
# Set the working directory in the container
WORKDIR /app

COPY src pyproject.toml README.md LICENSE requirements.txt ./
# Install the latest version from the cloned repository
RUN pip install --upgrade pip && pip install --no-cache-dir -r requirements.txt

# For stdio transport, we need a direct entrypoint
ENTRYPOINT ["python3", "-m", "frankfurtermcp.server"]
