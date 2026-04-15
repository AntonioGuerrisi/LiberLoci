#!/bin/sh
# Generate a self-signed certificate if one does not already exist.
# This enables HTTPS, which is required by browsers for camera access
# (getUserMedia) when connecting from a remote IP (non-localhost).

CERT_DIR="/etc/nginx/certs"
CERT_FILE="$CERT_DIR/selfsigned.crt"
KEY_FILE="$CERT_DIR/selfsigned.key"

if [ ! -f "$CERT_FILE" ] || [ ! -f "$KEY_FILE" ]; then
  mkdir -p "$CERT_DIR"
  echo "Generating self-signed TLS certificate..."
  openssl req -x509 -nodes -days 3650 \
    -newkey rsa:2048 \
    -keyout "$KEY_FILE" \
    -out "$CERT_FILE" \
    -subj "/CN=liberloci/O=LiberLoci/C=US"
  echo "Certificate generated at $CERT_FILE"
else
  echo "TLS certificate already exists, skipping generation."
fi
