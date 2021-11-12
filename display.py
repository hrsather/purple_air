import numpy as np
import io
import requests
import matplotlib.pyplot as plt

from PIL import Image
from datetime import datetime

import analysis as ana


""" This function uses the MapQuest API, described further in the README, to download an image of the
        geographic area of interest, defiend by a bounding box.

    Args:
        data: The purple air dataframe.
        new (optional): If True, it redownloads the image from the API and saves it to the images directory.
            If False, it loads an image img_name from the images directory.
        img_name (optional): The name of the image to load from the images directory if new == False.

    Returns:
        Nothing. Displays a plot.
"""
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

        # NOTE: This API doesn't return a perfect bounding box. It adds seemingly random margins to all sides.
        key = "wTPDkAtbI9q93RXHsKO1JwWxsFfB4Ao2"
        query = "https://open.mapquestapi.com/staticmap/v5/map?key=" + key + "&boundingBox=" + coords + "&margin=0&size=" + size + "&zoom=12"

        response = requests.get(query)
        imageStream = io.BytesIO(response.content)
        image = Image.open(imageStream)
        image.save("images/org_data" + str(datetime.now()) + ".jpg")

        return image

    return Image.open("images/" + img_name)


""" This function maps and displays the optimal lags from each sensor to the reference sensor
        overlayed on a geographic map of the location. This function is similar to display_map_max_corr,
        except for this image doesn't map the maximum correlation score over all different lags, just
        the instantaneous lag of 0.

    Args:
        data: The purple air dataframe.
        reference_location: The location of which to refererence all the optimal lags to.
        lag_matrix: The lag matrix, given by function get_corr_lag.

    Returns:
        Nothing. Displays a plot.
"""
def map_correlations(data, reference_location):
    map_overlay = load_img(data, new=False)

    color_map = plt.cm.get_cmap('viridis').reversed()
    plt.figure(dpi=1200)
    plt.imshow(map_overlay, cmap=color_map)
    plt.clim(0, 1)
    plt.colorbar()

    reference_location = "Golden Colorado"
    for location in np.unique(data["location"]):
        selected_df = data[data["location"] == location]
        lat = selected_df["lat"].iloc[0]
        long = selected_df["long"].iloc[0]

        min_lat = np.min(data["lat"])
        max_lat = np.max(data["lat"])
        min_long = np.min(data["long"])
        max_long = np.max(data["long"])

        width = map_overlay.size[0]
        long = width * (long - min_long) / (max_long - min_long)

        height = map_overlay.size[1]
        lat = height - height * (lat - min_lat) / (max_lat - min_lat)

        # Scale. This is a rough fix for the weird issues that mapquest has with their API
        lat = int(0.7 * (lat - height / 2) + height / 2)
        long = int(0.5 * (long - width / 2) + width / 2)

        if location == reference_location:
            color = plt.cm.Reds(1.0)
            plt.scatter(long, lat, c=[color], marker="*")
        else:
            corr = ana.get_cor(data, reference_location, location)
            if np.isnan(corr):
                continue
            color = color_map(corr)
            plt.text(long, lat, str(round(corr, 2)), color="red", fontsize=8)
            plt.scatter(long, lat, c=[color])


    plt.title("Comparisons with " + reference_location)
    plt.xticks([])
    plt.yticks([])
    plt.show()