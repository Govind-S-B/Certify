#!/bin/bash

# Generate SSL keys
openssl genpkey -algorithm RSA -out key.pem
openssl req -new -key key.pem -out cert_csr.pem -subj "/C=IN/ST=KL/L=TVM/O=protoRes/OU=dev/CN=localhost"
openssl x509 -req -days 365 -in cert_csr.pem -signkey key.pem -out cert.pem

# Create the directory if it doesn't exist
mkdir -p ~/certify/ssl

# Move the generated files to the ~/certify/ssl folder
mv key.pem cert.pem ~/certify/ssl/
rm cert_csr.pem

echo "SSL keys generated and moved to ~/certify/ssl folder"