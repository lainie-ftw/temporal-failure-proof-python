FROM ubuntu:22.04

# Prevent interactive prompts during package installation
ENV DEBIAN_FRONTEND=noninteractive

# Install system dependencies
RUN apt-get update && apt-get install -y \
    python3-full \
    python3-venv \
    git \
    curl \
    unzip \
    nano \
    netcat-openbsd \
    && rm -rf /var/lib/apt/lists/*

# Install Code Server
RUN curl -fsSL https://code-server.dev/install.sh | sh

# Create Code Server configuration directory and settings
RUN mkdir -p /root/.local/share/code-server/User && \
    echo '{\n\
    "workbench.colorTheme": "Default Dark+",\n\
    "workbench.startupEditor": "none",\n\
    "security.workspace.trust.enabled": false\n\
}' > /root/.local/share/code-server/User/settings.json

# Install Temporal CLI
RUN curl -sSf https://temporal.download/cli.sh | sh && \
    chmod +x /root/.temporalio/bin/temporal && \
    ln -sf /root/.temporalio/bin/temporal /usr/local/bin/temporal

# Set up environment variables
ENV PATH=$PATH:/root/.temporalio/bin:/usr/local/bin
ENV TEMPORAL_ADDRESS=127.0.0.1:7233

# Create workspace directory
RUN mkdir -p /workspace

# Set up Python virtual environment and install packages
RUN python3 -m venv /workspace/venv && \
    . /workspace/venv/bin/activate && \
    pip install --upgrade pip && \
    pip install temporalio uv && \
    deactivate

# Clone the repository (parameterizable via build arg)
ARG REPO_URL=https://github.com/lainie-ftw/temporal-failure-proof-python.git
RUN git clone ${REPO_URL} /workspace/temporal-failure-proof-python

# Set working directory
WORKDIR /workspace/temporal-failure-proof-python

# Expose ports
# 8443: code-server
# 8080: Temporal UI
# 7233: Temporal gRPC
EXPOSE 8443 8080 7233

# Copy entrypoint script
COPY docker-entrypoint.sh /usr/local/bin/
RUN chmod +x /usr/local/bin/docker-entrypoint.sh

# Set entrypoint
ENTRYPOINT ["/usr/local/bin/docker-entrypoint.sh"]
