FROM python:3.11-slim

WORKDIR /app
# Copy the Zscaler root certificate
COPY ../certs/zscaler-root.cer /usr/local/share/ca-certificates/zscaler-root.crt
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
COPY ./ask-data-frontend/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
# Copy application code
COPY . .

# Create embeddings directory
RUN mkdir -p /app/embeddings


# Expose Streamlit default port
EXPOSE 8551

# Run Streamlit app
CMD ["streamlit", "run", "app.py", "--server.port=8551", "--server.address=0.0.0.0"]
