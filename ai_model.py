import pandas as pd
import numpy as np

# Load the dataset
df = pd.read_csv("email_data.csv")

# Convert datetime columns
date_format = "%m/%d/%y %H:%M"  # Adjust if your format is different
df["email_sent_date_time"] = pd.to_datetime(df["email_sent_date_time"], format=date_format, errors="coerce")
df["email_view_date_time"] = pd.to_datetime(df["email_view_date_time"], format=date_format, errors="coerce")
df["cta_id1_click_datetime"] = pd.to_datetime(df["cta_id1_click_datetime"], format=date_format, errors="coerce")
df["cta_id2_click_datetime"] = pd.to_datetime(df["cta_id2_click_datetime"], format=date_format, errors="coerce")


# Calculate the mean engagement hour for each customer
def calculate_best_send_hour(row):
    times = [row["email_view_date_time"], row["cta_id1_click_datetime"], row["cta_id2_click_datetime"]]
    times = [t.hour for t in times if pd.notna(t)]  # Filter out NaN values
    return np.mean(times) if times else np.nan  # Calculate mean hour

df["best_send_hour"] = df.apply(calculate_best_send_hour, axis=1)

# Fill missing best send hour with the most common engagement hour
overall_best_hour = df["best_send_hour"].mode()[0] if not df["best_send_hour"].dropna().empty else 12
df["best_send_hour"].fillna(overall_best_hour, inplace=True)

# Save the dataset with calculated best send hour
df.to_csv("updated_email_data.csv", index=False)

print("Best send hour calculated and saved to 'updated_email_data.csv'.")
