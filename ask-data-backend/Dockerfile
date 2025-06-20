FROM python:3.11-slim

WORKDIR /app
# Copy the Zscaler root certificate
COPY ../certs/zscaler-root.cer /usr/local/share/ca-certificates/zscaler-root-ca.crt
COPY ../certs/zscaler-root.cer /etc/ssl/certs/zscaler-root-ca.crt

# Update the certificate store
RUN update-ca-certificates

ENV REQUESTS_CA_BUNDLE=/etc/ssl/certs/zscaler-root-ca.crt
ENV SSL_CERT_FILE=/etc/ssl/certs/zscaler-root-ca.crt
ENV CURL_CA_BUNDLE=/etc/ssl/certs/zscaler-root-ca.crt

# Install system dependencies
RUN apt-get update && apt-get install -y \
    curl \
    gcc \
    g++ \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first for better caching
COPY ./ask-data-backend/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
# Copy application code
COPY . . 
# Expose port
EXPOSE 8015

# Health check
HEALTHCHECK --interval=1800s --timeout=10s --start-period=120s --retries=3 \
    CMD curl -f http://localhost:8015/health || exit 1

# Start the application
CMD ["python", "app.py"]