from PIL import Image, ImageDraw, ImageFont
import requests
from io import BytesIO

# Open image from URL
url = "https://card-generator.onrender.com/api/template/"

# Coordinates for writing text on the image
# Each template image has its own coordinates for the text "to" and "from"
coordinates = {
    "1.jpg": {
        "to": (170, 560),
        "from": (210, 640)
    },
    "2.jpg": {
        "to": (375, 765),
        "from": (490, 890)
    },
    "3.jpg": {
        "to": (495, 440),
        "from": (570, 540)
    },
    "4.jpg": {
        "to": (450, 290),
        "from": (490, 360)
    },
    "5.jpg": {
        "to": (530, 500),
        "from": (620, 610)
    },
    "6.jpg": {
        "to": (330, 300),
        "from": (350, 390)
    }
}


def create_card(data, user_id):
    # Get template image from URL
    template = data['template']
    response = requests.get(url+template)
    # Open image using the content from the response
    image = Image.open(BytesIO(response.content))

    # Create ImageDraw and ImageFont objects
    draw = ImageDraw.Draw(image)
    font = ImageFont.truetype("fonts/arial.ttf", 35)

    # Write text on image using the coordinates for the current template
    draw.text(coordinates[template]['to'], data['receiver_name'], font=font, fill=(0, 0, 0))
    draw.text(coordinates[template]['from'], data['sender_name'], font=font, fill=(0, 0, 0))

    # Save modified image
    filename = f"{user_id}.jpg"
    image.save(filename)
    return filename
