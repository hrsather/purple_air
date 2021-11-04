import numpy as np
import io
import requests

from PIL import Image
from datetime import datetime


def load_img(data, new=False, img_name="correct.jpg"):
    if new:
        min_lat = np.min(data["lat"])
        max_lat = np.max(data["lat"])
        min_long = np.min(data["long"])
        max_long = np.max(data["long"])

        upper_left = str(min_lat) + "," + str(min_long)
        lower_right = str(max_lat) + "," + str(max_long)
        coords = lower_right + "," + upper_left
        
        width = 1200  # Max size of image
        height = int(width * abs((min_lat - max_lat) / (min_long - max_long)))
        size = str(width) + "," + str(height)

        # TODO: Normalize size. Calculate size by bounding boxes
        key = "wTPDkAtbI9q93RXHsKO1JwWxsFfB4Ao2"
        query = "https://open.mapquestapi.com/staticmap/v5/map?key=" + key + "&boundingBox=" + coords + "&margin=0&size=" + size + "&zoom=12"

        response = requests.get(query)
        imageStream = io.BytesIO(response.content)
        image = Image.open(imageStream)
        image.save("images/org_data" + str(datetime.now()) + ".jpg")

        return image

    return Image.open("images/" + img_name)