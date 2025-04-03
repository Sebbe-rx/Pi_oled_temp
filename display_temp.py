from luma.oled.device import ssd1306
from luma.core.interface.serial import i2c
from PIL import Image, ImageDraw, ImageFont
import time
import os
import socket
import netifaces as ni

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
font_small = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 10)  # Smaller font for IP address

# Set vertical spacing between lines
line_height_large = font_large.getbbox('A')[3] + 4
line_height_small = font_small.getbbox('A')[3] + 4  # Adjust for small font

# Get the correct IP address of the Raspberry Pi
def get_ip_address():
    interfaces = ni.interfaces()
    for interface in interfaces:
        try:
            ip = ni.ifaddresses(interface)[ni.AF_INET][0]['addr']
            if ip != '127.0.0.1':  # Exclude the loopback address
                return ip
        except KeyError:
            continue
    return 'No IP found'

# Get the IP address
ip_address = get_ip_address()

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
