FROM debian:bullseye-slim

ENV DEBIAN_FRONTEND=noninteractive \
    GLAMA_VERSION="0.2.0" \
    PATH="/home/service-user/.local/bin:${PATH}"

# Create service user and set up directories
RUN (groupadd -r service-user) && \
    (useradd -u 1987 -r -m -g service-user service-user) && \
    (mkdir -p /home/service-user/.local/bin /app) && \
    (chown -R service-user:service-user /home/service-user /app)

# Install system dependencies
# Added libgl1-mesa-glx, libglib2.0-0, python3-dev for OpenCV and other ML libraries
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
    build-essential \
    curl \
    wget \
    software-properties-common \
    libssl-dev \
    zlib1g-dev \
    git \
    libgl1-mesa-glx \
    libglib2.0-0 \
    python3-dev \
    ffmpeg \
    libsm6 \
    libxext6 && \
    rm -rf /var/lib/apt/lists/* && \
    curl -LsSf https://astral.sh/uv/install.sh | UV_INSTALL_DIR="/usr/local/bin" sh && \
    uv python install 3.10 --default --preview && \
    ln -s $(uv python find) /usr/local/bin/python && \
    python --version && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/* && \
    rm -rf /tmp/* && \
    rm -rf /var/tmp/* && \
    su - service-user -c "uv python install 3.10 --default --preview && python --version"

USER service-user
WORKDIR /app

# Clone repository (keeping this from the template)
# In a production environment, you might want to install from PyPI instead
RUN git clone https://github.com/sunriseapps/imagesorcery-mcp . && \
    git checkout 78d9170edc391edaf02a9f78cb71145221e2a507

# Install the package and run post-install
RUN python -m venv /home/service-user/venv && \
    . /home/service-user/venv/bin/activate && \
    pip install -e . && \
    # Install CLIP manually to ensure it's available
    pip install git+https://github.com/ultralytics/CLIP.git && \
    # Run post-install script to download models
    imagesorcery-mcp --post-install

# Expose port for HTTP transport
EXPOSE 8000

# Start the MCP server with HTTP transport
CMD ["/home/service-user/venv/bin/imagesorcery-mcp", "--transport=streamable-http", "--host=0.0.0.0", "--port=8000", "--path=/mcp"]
