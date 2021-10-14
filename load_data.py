import os
import pandas as pd


def get_filename_info(filename):
    first_open_parenthesis_index = filename.find("(")
    first_closing_parenthesis_index = filename.find(")")
    second_open_parenthesis_index = filename.find("(", first_open_parenthesis_index + 1)
    second_closing_perenthesis_index = filename.find(")", second_open_parenthesis_index)
    secondary_primary_space = filename.find(" ", second_closing_perenthesis_index + 2)

    location = filename[:first_open_parenthesis_index - 1]
    inside_outside = filename[first_open_parenthesis_index + 1 : first_closing_parenthesis_index]
    coordinates_list = (filename[second_open_parenthesis_index + 1 : second_closing_perenthesis_index]).split()
    lat, long = float(coordinates_list[0]), float(coordinates_list[1])
    primary_secondary = filename[second_closing_perenthesis_index + 2 : secondary_primary_space]
    return location, inside_outside, lat, long, primary_secondary


def get_raw_data(directory="data"):
    header = ["created_at", "PM2.5_ATM_ug/m3"]
    dataframes = []
    for filename in os.listdir(directory):
        if filename.endswith(".csv"):
            info_list = get_filename_info(filename)
            if info_list[4] == "Secondary":
                continue
            full_path = directory + "/" + filename
            new_df = pd.read_csv(full_path, usecols=header)
            # Parse filename and add info
            new_columns = ["location", "inside_outside", "lat", "long"]
            for column_name, info in zip(new_columns, info_list[:-1]):
                new_df[column_name] = info
            # Convert date to datetime
            new_df["created_at"] = new_df["created_at"].str[:-4]
            new_df["created_at"] = pd.to_datetime(new_df["created_at"])
            # Round to nearest 2 minute
            new_df["created_at"] = new_df["created_at"].dt.round("2min")
            dataframes.append(new_df)

    data_df = pd.concat(dataframes)
    return data_df


def remove_outliers(df, ppm_name, cutoff=300):
    previous_value = df[ppm_name].iloc[0]
    for i in range(len(df[ppm_name]) - 1):
        current_value = df[ppm_name].iloc[i]
        next_value = df[ppm_name].iloc[i + 1]
        if (current_value - previous_value > cutoff or
            current_value - next_value > cutoff):  # Too big of difference
            df[ppm_name].iloc[i] = previous_value
        else:
            previous_value = (current_value + next_value) / 2
    return df


def merge_a_b(df_a, df_b, date_name):
    merged = df_a.merge(df_b, how="outer", on=date_name)
    merged = merged.sort_values(by=date_name)
    # Take first
    col_names = ["location", "inside_outside"]
    for col_name in col_names:
        merged = merged.assign(**{col_name:df_a[col_name].iloc[0]})
        merged = merged.drop([col_name + "_x", col_name + "_y"], axis=1)

    # Take average
    col_names = ["PM2.5_ATM_ug/m3", "lat", "long"]
    for col_name in col_names:
        merged[col_name] = merged[[col_name + "_x", col_name + "_y"]].mean(axis=1)
        merged = merged.drop([col_name + "_x", col_name + "_y"], axis=1)

    return merged


def load_data(date_name, ppm_name, directory="data", recompute=False, pkl_name="data.pkl"):
    if not recompute:
        return pd.read_pickle(pkl_name)

    raw_data = get_raw_data(directory)

    data = pd.DataFrame()
    agg_func = {"PM2.5_ATM_ug/m3":"mean", "location":"first", "inside_outside":"first", "lat":"first", "long":"first"}
    for location in raw_data["location"].unique():
        if location[-1].strip() == "B":
            continue
        location_df_a = raw_data[raw_data["location"] == location]
        location_df_a = location_df_a.groupby(date_name, as_index=False).agg(agg_func)
        location_df_a = remove_outliers(location_df_a, ppm_name)

        location_df_b = raw_data[raw_data["location"] == location + " B"]
        location_df_b = location_df_b.groupby(date_name, as_index=False).agg(agg_func)
        location_df_b = remove_outliers(location_df_b, ppm_name)

        location_df = merge_a_b(location_df_a, location_df_b, date_name)
        data = data.append(location_df)

    data.to_pickle(pkl_name)
    return data