import pickle
import numpy as np
import global_vars as gv
import matplotlib.pyplot as plt
import pandas as pd
import os

import display as ds


def get_rmse(data, location_a, location_b):
    df_a = data[data["location"] == location_a]
    df_b = data[data["location"] == location_b]

    # Drop na and zero ppm values
    merged_df = df_a.merge(df_b, on=[gv.DATE_NAME])
    ppm_x_name = gv.PPM_NAME + "_x"
    ppm_y_name = gv.PPM_NAME + "_y"
    merged_df = merged_df[merged_df[ppm_x_name] > 0]
    merged_df = merged_df[merged_df[ppm_y_name] > 0]
    merged_df.dropna(subset=[ppm_x_name, ppm_y_name])

    merged_df["squared_error"] = np.square(merged_df[ppm_x_name] - merged_df[ppm_y_name])

    return np.sqrt(merged_df["squared_error"].mean())


def get_cor(data, name_a, name_b):
    df_a = data[data["location"] == name_a]
    df_b = data[data["location"] == name_b]

    return get_cor_df(df_a, df_b)


def get_cor_df(df_a, df_b):
    # Merge both dfs on date and get corr of both ppm's
    merged_df = df_a.merge(df_b, on=[gv.DATE_NAME])
    ppm_x_name = gv.PPM_NAME + "_x"
    ppm_y_name = gv.PPM_NAME + "_y"

    corr = merged_df[ppm_x_name].corr(merged_df[ppm_y_name])

    return corr


def get_corr_lag(data, recalculate=False, location_to_show=""):
    if not recalculate:
        with open(os.path.join("pkls", "corr.pkl"), "rb") as fp:
            differences =  pickle.load(fp)
        with open(os.path.join("pkls", "lags.pkl"), "rb") as fp:
            lags =  pickle.load(fp)
        return differences, lags

    all_best_coors = []
    all_lags = []
    for reference_location in np.unique(data["location"]):
        reference_df = data[data["location"] == reference_location]
        best_coors = []
        lags = []
        for location in np.unique(data["location"]):
            selected_df = data[data["location"] == location]
            
            corr_list = []
            for difference in range(-gv.DAYS_LOOKBACK, gv.DAYS_LOOKBACK, gv.DAYS_STEP):
                selected_df_copy = selected_df.copy(deep=True)
                selected_df_copy[gv.date_name] = selected_df_copy[gv.date_name] + pd.Timedelta(difference, "m")
                
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

        all_best_coors.append(best_coors)
        all_lags.append(lags)

    with open(os.path.join("pkls", "corr.pkl"), "wb") as fp:
        pickle.dump(all_best_coors, fp)

    with open(os.path.join("pkls", "lags.pkl"), "wb") as fp:
        pickle.dump(all_lags, fp)
        
    return all_best_coors, all_lags


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