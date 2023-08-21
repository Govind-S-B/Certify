#!/bin/bash

if [ $# -ne 1 ]; then
    echo "Usage: $0 <username>"
    exit 1
fi

username="$1"

# Generate SSL keys
openssl genpkey -algorithm RSA -out key.pem
openssl req -new -key key.pem -out cert_csr.pem -subj "/C=IN/ST=KL/L=TVM/O=protoRes/OU=dev/CN=localhost"
openssl x509 -req -days 365 -in cert_csr.pem -signkey key.pem -out cert.pem

# Create the directory if it doesn't exist
mkdir -p "/home/$username/certify/ssl"

# Move the generated files to the /home/username/certify/ssl folder
mv key.pem cert.pem "/home/$username/certify/ssl/"
rm cert_csr.pem

echo "SSL keys generated and moved to /home/$username/certify/ssl folder"
