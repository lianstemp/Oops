# Lightweight Tools-Only Dockerfile for Oops Sandbox
# This container only contains pentesting tools, not the Oops application

FROM alpine:3.19

# Install pentesting tools and utilities
RUN apk add --no-cache \
    # Core utilities
    bash \
    curl \
    curl-dev \
    wget \
    git \
    jq \
    bind-tools \
    whois \
    ca-certificates \
    # Network reconnaissance
    nmap \
    nmap-scripts \
    netcat-openbsd \
    tcpdump \
    masscan \
    # Python for Python-based tools
    python3 \
    py3-pip \
    # Build dependencies for Python packages
    gcc \
    musl-dev \
    libffi-dev \
    # Additional utilities
    openssh-client

# Install Python-based security tools
RUN pip3 install --no-cache-dir --break-system-packages \
    sqlmap \
    httpx

# Create non-root user
RUN addgroup -g 1000 sandbox && \
    adduser -D -u 1000 -G sandbox sandbox

# Create output directory
RUN mkdir -p /output && \
    chown -R sandbox:sandbox /output

# Switch to non-root user
USER sandbox

# Set working directory
WORKDIR /output

# Health check
HEALTHCHECK --interval=30s --timeout=3s --start-period=5s --retries=3 \
    CMD pgrep -x tail || exit 1

# Keep container running
CMD ["tail", "-f", "/dev/null"]
