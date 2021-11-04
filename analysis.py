import pickle
import numpy as np
import global_vars as gv
import matplotlib.pyplot as plt


def get_rmse(data, location_a, location_b):
    df_a = data[data["location"] == location_a]
    df_b = data[data["location"] == location_b]

    # Drop na and zero ppm values
    merged_df = df_a.merge(df_b, on=[gv.date_name])
    ppm_x_name = gv.ppm_name + "_x"
    ppm_y_name = gv.ppm_name + "_y"
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
    merged_df = df_a.merge(df_b, on=[gv.date_name])
    ppm_x_name = gv.ppm_name + "_x"
    ppm_y_name = gv.ppm_name + "_y"

    corr = merged_df[ppm_x_name].corr(merged_df[ppm_y_name])

    return corr


def get_lag_corr(data, recalculate=False):
    if not recalculate:
        with open("corr.pkl", "rb") as fp:
            differences =  pickle.load(fp)
        with open("lags.pkl", "rb") as fp:
            lags =  pickle.load(fp)
        return differences, lags

    all_differences = []
    all_lags = []
    for reference_location in np.unique(data["location"]):
        reference_df = data[data["location"] == reference_location]
        best_differences = []
        lags = []
        for location in np.unique(data["location"]):
            selected_df = data[data["location"] == location]
            
            difference_list = []
            for lag in range(-120, 120, 2):
                selected_df_copy = selected_df.copy(deep=True)
                selected_df_copy[gv.date_name] = selected_df_copy[gv.date_name] + pd.Timedelta(lag, "m")
                
                corr = get_cor_df(reference_df, selected_df_copy)
                difference_list.append(corr)

            best_diff = np.max(difference_list)
            best_differences.append(best_diff)
            lags.append(lag)

        all_differences.append(best_differences)
        all_lags.append(lags)


    with open("corr.pkl", "wb") as fp:
        pickle.dump(all_differences, fp)

    with open("lags.pkl", "wb") as fp:
        pickle.dump(all_differences, fp)
        
    return all_differences, all_lags