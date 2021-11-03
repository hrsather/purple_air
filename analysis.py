import numpy as np
import global_vars as gv


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


