import pandas as pd
import numpy as np
from sklearn.cluster import KMeans

# Adjust the date format to match your CSV data:
# For example, if dates are like "7/3/24 18:54", use "%m/%d/%y %H:%M"
DATE_FORMAT = "%m/%d/%y %H:%M"

# Load the dataset
df = pd.read_csv("email_data.csv")

# Convert datetime columns with a fixed format
df["email_sent_date_time"] = pd.to_datetime(df["email_sent_date_time"], format=DATE_FORMAT, errors="coerce")
df["email_view_date_time"] = pd.to_datetime(df["email_view_date_time"], format=DATE_FORMAT, errors="coerce")
df["cta_id1_click_datetime"] = pd.to_datetime(df["cta_id1_click_datetime"], format=DATE_FORMAT, errors="coerce")
df["cta_id2_click_datetime"] = pd.to_datetime(df["cta_id2_click_datetime"], format=DATE_FORMAT, errors="coerce")

# Extract engagement hours (as decimal values, e.g., 20.33 for 20:20)
def extract_hours(row):
    times = [
        row["email_view_date_time"],
        row["cta_id1_click_datetime"],
        row["cta_id2_click_datetime"]
    ]
    return [t.hour + t.minute/60 for t in times if pd.notna(t)]

df["engagement_hours"] = df.apply(extract_hours, axis=1)

# Determine optimal best times:
def find_optimal_times(hours):
    """
    - If no times: return []
    - If one time: return that time
    - If multiple times:
         * Compute the mean.
         * Use K-Means with 2 clusters.
         * If the cluster centers differ by more than 3 hours, return both centers.
         * Otherwise, return the mean.
    """
    if len(hours) == 0:
        return []
    if len(hours) == 1:
        return [float(round(hours[0], 2))]
    
    X = np.array(hours).reshape(-1, 1)
    mean_time = float(round(np.mean(hours), 2))
    
    # Only attempt clustering if there are distinct values
    if len(set(hours)) > 1:
        kmeans = KMeans(n_clusters=2, random_state=42, n_init=10)
        kmeans.fit(X)
        centers = sorted(kmeans.cluster_centers_.flatten())
        separation = abs(centers[1] - centers[0])
        if separation > 3:
            return [float(round(c, 2)) for c in centers]
    
    return [mean_time]

df["best_send_hours"] = df["engagement_hours"].apply(find_optimal_times)

# Force best_send_hours to be stored as a plain list string (without numpy type formatting)
df["best_send_hours"] = df["best_send_hours"].apply(lambda x: str(x))

# Ensure customer_id exists; if not, assign sequential IDs.
if "customer_id" not in df.columns:
    df.insert(0, "customer_id", range(1, len(df) + 1))

# Save the updated CSV
df.to_csv("updated_email_data.csv", index=False)
print("✅ Optimal send times calculated and saved to 'updated_email_data.csv'.")
