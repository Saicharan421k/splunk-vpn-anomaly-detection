# splunk-vpn-anomaly-detection
A Splunk MLTK prototype for detecting anomalous VPN logins.
# Machine Learning-Based VPN Anomaly Detection in Splunk

This project is a prototype submitted for the HackerEarth Splunk Build-a-thon (Track 4: AI/ML). It uses Splunk's Machine Learning Toolkit (MLTK) to detect anomalous VPN logins based on geography and time.

## Problem Statement

As described in the "VPN Login from an Unusual Location per User Model" use case, traditional security tools struggle to detect credential theft when valid credentials are used. This model establishes a baseline of normal login behavior for each user (typical locations and hours) and flags any significant deviations as potential security threats.

## How It Works

1.  **Data Ingestion**: The system uses a sample `vpn_logins.csv` which contains `timestamp`, `user`, and `src_ip`.
2.  **Feature Engineering**: A Splunk SPL query enriches the data by:
    *   Using the `iplocation` command to get the `latitude` and `longitude` from the `src_ip`.
    *   Extracting the `login_hour` from the timestamp and converting it to a number.
3.  **ML Model**: The `KMeans` algorithm from MLTK is used to cluster user behavior.
    *   The model is trained on the `lat`, `lon`, and `login_hour` features.
    *   Critically, the `by user` clause creates a unique behavioral baseline (a cluster center) for every single user.
    *   The trained model is saved as **`vpn_model_final`**.
4.  **Detection**: The `apply` command runs new login events against the model. It calculates the **`cluster_distance`** for each event, which is a numerical score of how far that login is from the user's normal behavior. A high score indicates a likely anomaly.
5.  **Visualization & Alerting**: A dashboard provides a real-time view of anomalies on a world map and in a table, sorted by the highest anomaly score. A scheduled alert can notify security teams of new threats.

## Core SPL Queries

**Model Training:**
```spl
| inputlookup vpn_logins.csv | eval _time = strptime(timestamp, "%Y-%m-%dT%H:%M:%SZ") | iplocation src_ip | eval login_hour = tonumber(strftime(_time, "%H")) | where isnotnull(lat) AND isnotnull(lon) AND isnotnull(login_hour) | fit KMeans k=1 from "lat", "lon", "login_hour" by "user" into vpn_model_final
```

**Detection & Visualization (for the anomaly table):**
```spl
| inputlookup vpn_logins.csv | eval _time = strptime(timestamp, "%Y-%m-%dT%H:%M:%SZ") | iplocation src_ip | eval login_hour = tonumber(strftime(_time, "%H")) | where isnotnull(lat) AND isnotnull(lon) AND isnotnull(login_hour) | apply vpn_model_final | sort - cluster_distance | table _time, user, City, Country, cluster_distance
```

## How to Deploy and Test

**Prerequisites:** A Splunk Enterprise instance with the **Splunk Machine Learning Toolkit (MLTK)** and the **Python for Scientific Computing Add-on** installed.

1.  **Upload Data:** Upload the `vpn_logins.csv` from this repository as a lookup file in Splunk (`Settings > Lookups > Lookup table files`). Make it globally shared.
2.  **Train Model:** Run the "Model Training" query above in the Splunk search bar.
3.  **View Dashboard:**
    *   Create a new dashboard in Dashboard Studio.
    *   The dashboard in this repository is saved as `vpn_anomaly_detection.xml`. You can view its source and use it as a template to rebuild the panels using the queries above.
    *   *Note: Due to a bug in our Splunk version, the table panel was created from a Saved Report. The search query for that report is the "Detection & Visualization" query listed above.*
