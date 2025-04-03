#!/bin/bash

# Update and upgrade the system
echo "Updating and upgrading the system..."
sudo apt update && sudo apt upgrade -y

# Install required packages and dependencies
echo "Installing required packages..."
sudo apt install -y python3-pip python3-dev python3-setuptools python3-smbus i2c-tools python3-pil python3-requests

# Install the necessary Python libraries for OLED display
echo "Installing necessary Python libraries..."
sudo pip3 install luma.oled Pillow

# Enable I2C if not already enabled
echo "Enabling I2C..."
sudo raspi-config nonint do_i2c 0

# Install netplan (if not already installed)
echo "Ensuring netplan is installed..."
sudo apt install -y netplan.io

# Set up the script directory
echo "Setting up script directory..."
mkdir -p ~/scripts

# Create the display temperature script
echo "Creating display_temp.py script..."

cat << 'EOF' > ~/scripts/display_temp.py
from luma.oled.device import ssd1306
from luma.core.interface.serial import i2c
from PIL import Image, ImageDraw, ImageFont
import time
import os
import socket

# Set up the I2C interface and the SSD1306 display
serial = i2c(port=1, address=0x3C)
device = ssd1306(serial)

# Create an image buffer and draw object
width = device.width
height = device.height
image = Image.new('1', (width, height))
draw = ImageDraw.Draw(image)

# Load a larger font for the temperature (you can adjust the path to your font file)
font_large = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 24)  # Larger font for temperature
font_small = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 14)  # Smaller font for IP address

# Set vertical spacing between lines
line_height_large = font_large.getbbox('A')[3] + 4
line_height_small = font_small.getbbox('A')[3] + 4  # Adjust for small font

# Get the IP address of the Raspberry Pi
hostname = socket.gethostname()
ip_address = socket.gethostbyname(hostname)

while True:
    # Get the temperature from the Raspberry Pi
    temp = os.popen("vcgencmd measure_temp").readline()
    temp = temp.replace("temp=", "").replace("'C\n", "")

    # Clear the image buffer at the start of each iteration
    draw.rectangle((0, 0, width, height), outline=0, fill=0)

    # Draw the temperature on the OLED with the larger font
    draw.text((0, 0), "{} C".format(temp), font=font_large, fill=255)  # Temperature in large font

    # Draw the IP address on the OLED with the smaller font
    draw.text((0, line_height_large), "IP: {}".format(ip_address), font=font_small, fill=255)  # IP address in small font

    # Display the image on the OLED
    device.display(image)

    # Wait for a bit before updating again
    time.sleep(1)
EOF

# Make the script executable
echo "Making the script executable..."
chmod +x ~/scripts/display_temp.py

# Create the systemd service to run the script on boot
echo "Creating systemd service to run the script on boot..."

cat << 'EOF' | sudo tee /etc/systemd/system/display_temp.service
[Unit]
Description=Display Temperature on OLED
After=multi-user.target

[Service]
ExecStart=/usr/bin/python3 /home/pi/scripts/display_temp.py
WorkingDirectory=/home/pi/scripts
StandardOutput=inherit
StandardError=inherit
Restart=always
User=pi

[Install]
WantedBy=multi-user.target
EOF

# Enable the systemd service
echo "Enabling the systemd service..."
sudo systemctl daemon-reload
sudo systemctl enable display_temp.service
sudo systemctl start display_temp.service

echo "Installation and setup complete! The script should now be running on your Raspberry Pi."
