import pickle
import numpy as np
import global_vars as gv
import matplotlib.pyplot as plt
import pandas as pd
import os

import display as ds


""" This function returns the correlation of the PPM between two locations.
        This serves as a helper function for get_cor_df, which accepts dataframes

    Args:
        data: The purple air dataframe.
        name_a: The name of the first location.
        name_b: The name of the second location.

    Returns:
        The correlation of the PPM from the dataframe between the two locations.
"""
def get_cor(data, name_a, name_b):
    df_a = data[data["location"] == name_a]
    df_b = data[data["location"] == name_b]

    return get_cor_df(df_a, df_b)


""" This function returns the correlation of the PPM between two dataframes.

    Args:
        df_a: The dataframe of the first location.
        df_b: The dataframe of the second location.

    Returns:
        The correlation of the PPM from the dataframe between the two dataframes.
"""
def get_cor_df(df_a, df_b):
    # Merge both dfs on date and get corr of both ppm's
    merged_df = df_a.merge(df_b, on=[gv.DATE_NAME])
    ppm_x_name = gv.PPM_NAME + "_x"
    ppm_y_name = gv.PPM_NAME + "_y"

    corr = merged_df[ppm_x_name].corr(merged_df[ppm_y_name])

    return corr


""" This function finds what the optimal lag is for two locations to have the
        highest correlation to eachother. Then it returns that lag along with its
        optimal correlation.

    Args:
        data: The purple air dataframe.
        recalculate (optional): If True, this recalculates the optimal correlation
            and lags, then saves them as pkls in the pkls directory. If False, this
            loads the already computed pkls and returns them.
        location_to_show (optional): If passed a reference location, it will display the
            correlation given different values of lag for all the other locations to the reference.
            recalculate must be True

    Returns:
        The optimal correlations, the corresponding optimal lags.
"""
def get_corr_lag(data, recalculate=False, location_to_show=""):
    if not recalculate:
        with open(os.path.join("pkls", "corr.pkl"), "rb") as fp:
            differences =  pickle.load(fp)
        with open(os.path.join("pkls", "lags.pkl"), "rb") as fp:
            lags =  pickle.load(fp)
        return differences, lags

    optimal_corr_matrix = []
    lag_matrix = []
    for reference_location in np.unique(data["location"]):
        reference_df = data[data["location"] == reference_location]
        best_coors = []
        lags = []
        for location in np.unique(data["location"]):
            selected_df = data[data["location"] == location]
            
            corr_list = []
            for difference in range(-gv.DAYS_LOOKBACK, gv.DAYS_LOOKBACK, gv.DAYS_STEP):
                selected_df_copy = selected_df.copy(deep=True)
                selected_df_copy[gv.DATE_NAME] = selected_df_copy[gv.DATE_NAME] + pd.Timedelta(difference, "m")
                
                corr = get_cor_df(reference_df, selected_df_copy)
                corr_list.append(corr)

            if reference_location == location_to_show:
                plt.title(reference_location + " " + location)
                plt.plot(range(-gv.DAYS_LOOKBACK, gv.DAYS_LOOKBACK, gv.DAYS_STEP), corr_list)
                plt.show()
                
            best_diff = np.max(corr_list)
            best_coors.append(best_diff)
            lag = 2 * corr_list.index(best_diff) - gv.DAYS_LOOKBACK
            lags.append(lag)

        optimal_corr_matrix.append(best_coors)
        lag_matrix.append(lags)

    with open(os.path.join("pkls", "corr.pkl"), "wb") as fp:
        pickle.dump(optimal_corr_matrix, fp)

    with open(os.path.join("pkls", "lags.pkl"), "wb") as fp:
        pickle.dump(lag_matrix, fp)
        
    return optimal_corr_matrix, lag_matrix


""" This function maps and displays the optimal lags from each sensor to the reference sensor
        overlayed on a geographic map of the location. This function is similar to display_map_max_corr,
        except for this displays the lags.

    Note: There is probably a smart way to merge this with display_map_lag because they are so similar

    Args:
        data: The purple air dataframe.
        reference_location: The location of which to refererence all the optimal lags to.
        lag_matrix: The lag matrix, given by function get_corr_lag.

    Returns:
        Nothing. Displays a plot.
"""
def display_map_lag(data, reference_location, lag_matrix):
    image = ds.load_img(data, new=False)

    plt.figure(dpi=1200)
    color_map = plt.cm.PuOr
    plt.imshow(image, cmap=color_map)
    plt.clim(-gv.DAYS_LOOKBACK, gv.DAYS_LOOKBACK)
    plt.colorbar()

    for location in np.unique(data["location"]):
        selected_df = data[data["location"] == location]
        lat = selected_df["lat"].iloc[0]
        long = selected_df["long"].iloc[0]

        min_lat = np.min(data["lat"])
        max_lat = np.max(data["lat"])
        min_long = np.min(data["long"])
        max_long = np.max(data["long"])

        width = image.size[0]
        long = width * (long - min_long) / (max_long - min_long)

        height = image.size[1]
        lat = height - height * (lat - min_lat) / (max_lat - min_lat)

        # NOTE: 0.5 and 0.7 were determined by experimentation and seemed to give the best results for resizing the image
        lat = int(0.7 * (lat - height / 2) + height / 2)
        long = int(0.5 * (long - width / 2) + width / 2)

        if location == reference_location:
            color = plt.cm.Reds(1.0)
            plt.scatter(long, lat, c=[color], marker="*")
        else:
            reference_index = np.where(np.unique(data["location"]) == reference_location)[0][0]
            new_index = np.where(np.unique(data["location"]) == location)[0][0]
            corr = lag_matrix[reference_index][new_index]
            normed_corr = corr / 120 + 0.5
            color = color_map(normed_corr)
            plt.text(long, lat, str(round(corr, 2)), color="red", fontsize=8)
            plt.scatter(long, lat, c=[color])

    plt.title("Lag Comparisons with " + reference_location)
    plt.xlabel("(Positive lag means that it happens after the reference)")
    plt.xticks([])
    plt.yticks([])
    plt.show()


""" This function maps and displays the optimal correlations from each sensor to the reference sensor
        overlayed on a geographic map of the location. This function is similar to display_map_lag,
        except for this displays the optimal correlations.

    Note: There is probably a smart way to merge this with display_map_lag because they are so similar

    Args:
        data: The purple air dataframe.
        reference_location: The location of which to refererence all the optimal lags to.
        correlation_matrix: The correlation_matrix matrix, given by function get_corr_lag.

    Returns:
        Nothing. Displays a plot.
"""
def display_map_max_corr(data, reference_location, correlation_matrix):
    image = ds.load_img(data, new=False)

    plt.figure(dpi=1200)
    color_map = plt.cm.PuOr
    plt.imshow(image, cmap=color_map)
    plt.clim(-1, 1)
    plt.colorbar()

    for location in np.unique(data["location"]):
        selected_df = data[data["location"] == location]
        lat = selected_df["lat"].iloc[0]
        long = selected_df["long"].iloc[0]

        min_lat = np.min(data["lat"])
        max_lat = np.max(data["lat"])
        min_long = np.min(data["long"])
        max_long = np.max(data["long"])

        width = image.size[0]
        long = width * (long - min_long) / (max_long - min_long)

        height = image.size[1]
        lat = height - height * (lat - min_lat) / (max_lat - min_lat)

        # NOTE: 0.5 and 0.7 were determined by experimentation and seemed to give the best results for resizing the image
        lat = int(0.7 * (lat - height / 2) + height / 2)
        long = int(0.5 * (long - width / 2) + width / 2)

        if location == reference_location:
            color = plt.cm.Reds(1.0)
            plt.scatter(long, lat, c=[color], marker="*")
        else:
            reference_index = np.where(np.unique(data["location"]) == reference_location)[0][0]
            new_index = np.where(np.unique(data["location"]) == location)[0][0]
            corr = correlation_matrix[reference_index][new_index]
            color = color_map(corr)
            plt.text(long, lat, str(round(corr, 2)), color="red", fontsize=8)
            plt.scatter(long, lat, c=[color])

    plt.title("Max Comparisons with " + reference_location)
    plt.xticks([])
    plt.yticks([])
    plt.show()