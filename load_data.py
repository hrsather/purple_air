import os
import pandas as pd

import global_vars as gv


""" This function parses the filename to find important metadata about the data.
        This function is not used outside of this class

    Args:
        filename: The name of the file.

    Returns:
        A 5-tuple of the location, whether the sensor is inside or outside,
            the latitude, the longitude, and whether the sensor is primary or secondary.
"""
def _get_filename_info(filename):
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


""" This function loads all the data from the csv files from the given directory and saves it to a dataframe
        without cleaning any of the data.

    Args:
        directory (optional): The name of the directory.

    Returns:
        The dataframe with all the data from all the csv files in the directory.
"""
def get_raw_data(directory="data"):
    header = ["created_at", "PM2.5_ATM_ug/m3"]
    dataframes = []
    for filename in os.listdir(directory):
        if filename.endswith(".csv"):
            info_list = _get_filename_info(filename)
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


""" This function applies a moving filter over the PPM_NAME column. If a value is larger than its previous and
        subsequent values by a given cutoff value, then it is seen as an outlier and takes on the value
        of the average of its previous and subsequent values.
        This function is not used outside of this class

    Note: This may be able to be parallelized, but I didn't figure out how to do it. It is a slow function.

    Args:
        data: The purple air dataframe.
        cutoff (optional): The cutoff value that determines if a jump in values is large enough to be considered an outlier.

    Returns:
        The given dataframe but with the outlier values removed.
"""
def _remove_outliers(df, cutoff=300):
    previous_value = df[gv.PPM_NAME].iloc[0]
    for i in range(len(df[gv.PPM_NAME]) - 1):
        current_value = df[gv.PPM_NAME].iloc[i]
        next_value = df[gv.PPM_NAME].iloc[i + 1]
        if (current_value - previous_value > cutoff or
            current_value - next_value > cutoff):  # Too big of difference
            df[gv.PPM_NAME].iloc[i] = previous_value
        else:
            previous_value = (current_value + next_value) / 2
    return df


""" This function merges two dataframes on the DATENAME column. It then drops duplicate columns.
        It merges location and inside_outside by taking the first value and merges.
        It merges PPM_NAME, lat, and long by averaging the values.
        This function is not used outside of this class

    Args:
        df_a: The first dataframe.
        df_b: The second dataframe.

    Returns:
        A dataframe resulting from the two input dataframes being merged.
"""
def _merge_a_b(df_a, df_b):
    merged = df_a.merge(df_b, how="outer", on=gv.DATE_NAME)
    merged = merged.sort_values(by=gv.DATE_NAME)
    # Take first
    col_names = ["location", "inside_outside"]
    for col_name in col_names:
        merged = merged.assign(**{col_name:df_a[col_name].iloc[0]})
        merged = merged.drop([col_name + "_x", col_name + "_y"], axis=1)

    # Take average
    col_names = [gv.PPM_NAME, "lat", "long"]
    for col_name in col_names:
        merged[col_name] = merged[[col_name + "_x", col_name + "_y"]].mean(axis=1)
        merged = merged.drop([col_name + "_x", col_name + "_y"], axis=1)

    return merged


""" This function loads the dataframe by either loading it from a pkl file or by calling get_raw_data
        then merging and cleaning the data.

    Args:
        directory (optional): The directory that holds the cvs files to load if recompute==False
        recompute (optional): If recompute==False, load the data quickly from a pkl.
            If recompute==True, reload and clean all the data from the csv files from the given directory.
            Then save the pkl with the given pkl_name
        pkl_name (optional): If recompute==False, this is the pkl where the previously computed data is loaded from

    Returns:
        A cleaned dataframe of all the sensors at every location from the given directory.
"""
def load_data(directory="data", recompute=False, pkl_name="data.pkl"):
    if not recompute:
        return pd.read_pickle(os.path.join("pkls", pkl_name))

    raw_data = get_raw_data(directory)

    data = pd.DataFrame()
    agg_func = {"PM2.5_ATM_ug/m3":"mean", "location":"first",
                "inside_outside":"first", "lat":"first", "long":"first"}
    for location in raw_data["location"].unique():
        if location[-1].strip() == "B":
            continue
        location_df_a = raw_data[raw_data["location"] == location]
        location_df_a = location_df_a.groupby(gv.DATE_NAME, as_index=False).agg(agg_func)
        location_df_a = _remove_outliers(location_df_a)

        location_df_b = raw_data[raw_data["location"] == location + " B"]
        location_df_b = location_df_b.groupby(gv.DATE_NAME, as_index=False).agg(agg_func)
        location_df_b = _remove_outliers(location_df_b)

        location_df = _merge_a_b(location_df_a, location_df_b)
        data = data.append(location_df)

    # Drop broken entry
    data = data[data["location"] != "Bear Valley Visitor Center"]

    data.to_pickle(os.path.join("pkls", pkl_name))
    return data