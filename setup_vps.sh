#!/bin/bash

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
    sudo systemctl status docker
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

# Add a cron job for certificate renewal
(crontab -l ; echo "0 0 * * 0 docker-compose -f /home/$NEW_USER/docker-compose.yml exec certbot certbot renew --webroot --webroot-path=/var/lib/letsencrypt") | crontab -

# Finish setup
echo "Setup complete!"
echo "For security and best practices, it's recommended to use the newly created user ($NEW_USER) for SSHing to the server and performing actions."
echo "Please refrain from using the root account unless necessary."
echo "To start the server, run: docker-compose up -d"
echo "To stop the server, run: docker-compose down"
su - $NEW_USER
