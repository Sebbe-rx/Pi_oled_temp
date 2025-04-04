from luma.oled.device import ssd1306
from luma.core.interface.serial import i2c
from PIL import Image, ImageDraw, ImageFont, ImageOps
import time
import os
import socket
import netifaces as ni
import psutil  # Import for RAM & CPU usage

# Set up the I2C interface and the SSD1306 display
serial = i2c(port=1, address=0x3C)
device = ssd1306(serial)

# Load the 16x16 monochrome image
image = Image.open("/home/sebbe/monokr.bmp").convert("1")  # Convert to 1-bit
image = ImageOps.invert(image)  # Invert the colors

# Create an image buffer and draw object
width = device.width
height = device.height
background = Image.new('1', (width, height), 0)  # Create a black background image
draw = ImageDraw.Draw(background)

# Load fonts
font_temp = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 15)  # Smaller temp font
font_medium = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 12)  # CPU & RAM
font_small = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 9)  # IP

# Set vertical spacing
line_height_temp = font_temp.getbbox('A')[3] + 4
line_height_medium = font_medium.getbbox('A')[3] + 4
line_height_small = font_small.getbbox('A')[3] + 4

# Function to get the correct IP address of the Raspberry Pi
def get_ip_address():
    interfaces = ni.interfaces()
    for interface in interfaces:
        try:
            ip = ni.ifaddresses(interface)[ni.AF_INET][0]['addr']
            if ip != '127.0.0.1':  # Exclude loopback
                return ip
        except KeyError:
            continue
    return 'No IP found'

# Get IP address
ip_address = get_ip_address()

while True:
    # Get CPU temperature
    temp = os.popen("vcgencmd measure_temp").readline().replace("temp=", "").replace("'C\n", "")

    # Get CPU load
    cpu_load = psutil.cpu_percent(interval=1)  # Get CPU usage

    # Get RAM usage
    ram_usage = psutil.virtual_memory().percent  # RAM usage in %

    # Clear image buffer (background is black, so this will just clear the screen)
    draw.rectangle((0, 0, width, height), outline=0, fill=0)

    # Draw temperature
    draw.text((0, 0), "{} °C".format(temp), font=font_temp, fill=255)

    # Draw CPU usage
    draw.text((0, line_height_temp), "CPU: {}%".format(cpu_load), font=font_medium, fill=255)

    # Draw RAM usage
    draw.text((0, line_height_temp + line_height_medium), "RAM: {}%".format(ram_usage), font=font_medium, fill=255)

    # Draw IP address
    draw.text((0, line_height_temp + 2 * line_height_medium), "IP: {}".format(ip_address), font=font_small, fill=255)

    # Set position to draw the 16x16 image
    x_offset = 111
    y_offset = 1
    # Paste the image on the background at the specified position
    background.paste(image, (x_offset, y_offset))

    # Display on OLED
    device.display(background)

    # Wait before updating again
    time.sleep(5)
