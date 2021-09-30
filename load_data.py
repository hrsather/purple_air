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


def get_dataframe(directory="data"):
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