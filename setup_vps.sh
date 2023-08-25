#!/bin/bash

# Check for privilege
if [ "$EUID" -ne 0 ]; then
    echo "This script requires root privileges. Please run it with sudo or as the root user."
    exit 1
fi

# Set up non-root user
read -p "Enter the username for the non-root user: " NEW_USER

sudo apt update
sudo apt install -y sudo

if ! id "$NEW_USER" &>/dev/null; then
    sudo adduser $NEW_USER
    sudo adduser $NEW_USER sudo
fi

# Set up Docker and Docker Compose
sudo apt update
sudo apt install -y apt-transport-https ca-certificates curl gnupg2 software-properties-common

if ! command -v docker &>/dev/null; then
    curl -fsSL https://download.docker.com/linux/debian/gpg | sudo apt-key add -
    sudo add-apt-repository "deb [arch=amd64] https://download.docker.com/linux/debian $(lsb_release -cs) stable"
    sudo apt update
    sudo apt install -y docker-ce
    sudo systemctl enable docker.service
    sudo systemctl enable containerd.service
fi

if ! command -v docker-compose &>/dev/null; then
    sudo apt install -y docker-compose
fi

sudo usermod -aG docker $NEW_USER

# Create and populate .env file
echo "Creating and populating .env file..."
read -p "Enter the CERTBOT_EMAIL: " CERTBOT_EMAIL
read -p "Enter the CERTBOT_DOMAIN: " CERTBOT_DOMAIN
read -p "Enter the DB_USERNAME: " DB_USERNAME
read -p "Enter the DB_PASSWORD: " DB_PASSWORD
read -p "Enter the API_AUTH_KEY: " API_AUTH_KEY

echo "CERTBOT_EMAIL=$CERTBOT_EMAIL
CERTBOT_DOMAIN=$CERTBOT_DOMAIN
DB_USERNAME=$DB_USERNAME
DB_PASSWORD=$DB_PASSWORD
API_AUTH_KEY=$API_AUTH_KEY" > /home/$NEW_USER/.env

# Download docker-compose.yml
echo "Downloading docker-compose.yml..."
curl -o /home/$NEW_USER/docker-compose.yml https://raw.githubusercontent.com/Govind-S-B/Certify/main/docker-compose.yml

# Opening ports 8000 and 80
sudo iptables -A INPUT -p tcp --dport 8000 -j ACCEPT
sudo iptables -A INPUT -p tcp --dport 80 -j ACCEPT
sudo iptables-save | sudo tee /etc/iptables/rules.v4

# Install Certbot and generate certificates
sudo apt update
sudo apt install -y certbot

sudo certbot certonly --standalone --preferred-challenges http --email $CERTBOT_EMAIL --agree-tos -d $CERTBOT_DOMAIN --non-interactive

# Copy certificates to the appropriate location
sudo mkdir -p /home/$NEW_USER/certify/ssl
sudo cp /etc/letsencrypt/live/$CERTBOT_DOMAIN/fullchain.pem /home/$NEW_USER/certify/ssl/cert.pem
sudo cp /etc/letsencrypt/live/$CERTBOT_DOMAIN/privkey.pem /home/$NEW_USER/certify/ssl/key.pem

# Update permissions for the copied certificates
sudo chown $NEW_USER:$NEW_USER /home/$NEW_USER/certify/ssl/cert.pem
sudo chown $NEW_USER:$NEW_USER /home/$NEW_USER/certify/ssl/key.pem

# Set up cron job for certificate renewal
(sudo crontab -u $NEW_USER -l 2>/dev/null; echo "0 0 * * * /usr/bin/certbot renew --quiet && cp /etc/letsencrypt/live/$CERTBOT_DOMAIN/fullchain.pem /home/$NEW_USER/certify/ssl/cert.pem && cp /etc/letsencrypt/live/$CERTBOT_DOMAIN/privkey.pem /home/$NEW_USER/certify/ssl/key.pem && docker-compose -f /home/$NEW_USER/docker-compose.yml restart api_server") | sudo crontab -u $NEW_USER -

# Finish setup
echo "Setup complete!"
echo "For security and best practices, it's recommended to use the newly created user ($NEW_USER) for SSHing to the server and performing actions."
echo "Please refrain from using the root account unless necessary."
echo "To start the server, run: docker-compose up -d"
echo "To stop the server, run: docker-compose down"
su - $NEW_USER
