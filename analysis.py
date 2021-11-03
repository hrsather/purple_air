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


index_0 = 11
index_1 = 15
print(np.unique(data["location"])[index_0])
print(np.unique(data["location"])[index_1])

selected_df_0 = data[data["location"] == np.unique(data["location"])[index_0]]
selected_df_1 = data[data["location"] == np.unique(data["location"])[index_1]]

plt.plot(selected_df_0[date_name], selected_df_0[ppm_name])
plt.plot(selected_df_1[date_name], selected_df_1[ppm_name])
plt.show()

corr = get_cor(data,
               np.unique(data["location"])[index_0],
               np.unique(data["location"])[index_1],
               date_name,
               ppm_name)

print(corr[0][1])



def get_cor(data, name_a, name_b, date_name, ppm_name):
    df_a = data[data["location"] == name_a]
    df_b = data[data["location"] == name_b]

    # Drop na and zero ppm values
    merged_df = df_a.merge(df_b, on=[date_name])
    ppm_x_name = ppm_name + "_x"
    ppm_y_name = ppm_name + "_y"
    merged_df = merged_df[merged_df[ppm_x_name] > 0]
    merged_df = merged_df[merged_df[ppm_y_name] > 0]
    merged_df.dropna(subset=[ppm_x_name, ppm_y_name])

    corr = np.corrcoef(merged_df[ppm_x_name], merged_df[ppm_y_name])
    return corr