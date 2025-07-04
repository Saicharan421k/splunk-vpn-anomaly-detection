# --- CORRECTED SCRIPT ---
import csv
import random
from datetime import datetime, timedelta
from faker import Faker

fake = Faker()

# --- Configuration ---
NUM_LOGS = 5000
NUM_USERS = 50
FILENAME = "vpn_logins.csv"

# --- Define User Profiles (Normal Behavior) ---
# Let's create some users with typical login locations
user_profiles = {}
for i in range(NUM_USERS):
    username = fake.user_name()
    # Assign a "home" country for each user
    if i % 3 == 0:
        home_country = "US"
        home_city_func = fake.city  # <-- CORRECTED
        home_ip_func = fake.ipv4_public
    elif i % 3 == 1:
        home_country = "IN"
        home_city_func = lambda: random.choice(["Bangalore", "Mumbai", "Delhi", "Pune"])
        home_ip_func = lambda: f"103.{random.randint(10,250)}.{random.randint(10,250)}.{random.randint(10,250)}"
    else:
        home_country = "GB"
        home_city_func = fake.city  # <-- CORRECTED
        home_ip_func = fake.ipv4_private # Mix it up

    user_profiles[username] = {
        "home_country": home_country,
        "home_city_func": home_city_func,
        "home_ip_func": home_ip_func,
    }

# --- Generate Logs ---
header = ['timestamp', 'user', 'src_ip', 'login_status']
data = []
current_time = datetime.now()

users = list(user_profiles.keys())

for _ in range(NUM_LOGS):
    # Choose a random user
    user = random.choice(users)
    profile = user_profiles[user]
    
    # Generate timestamp
    time_offset = random.randint(1, 30*24*60) # logs over the last 30 days
    timestamp = (current_time - timedelta(minutes=time_offset)).strftime('%Y-%m-%dT%H:%M:%SZ')
    
    # Decide if this is an anomaly (10% chance)
    if random.random() < 0.10:
        # ANOMALOUS LOGIN
        src_ip = fake.ipv4_public(network=False, address_class=random.choice(['a', 'b', 'c']))
        login_status = "success" # Attackers often use valid credentials
    else:
        # NORMAL LOGIN
        src_ip = profile["home_ip_func"]()
        login_status = "success" if random.random() < 0.98 else "failure"

    data.append([timestamp, user, src_ip, login_status])

# --- Write to CSV ---
with open(FILENAME, 'w', newline='') as f:
    writer = csv.writer(f)
    writer.writerow(header)
    writer.writerows(data)

print(f"Successfully generated {NUM_LOGS} logs in '{FILENAME}'")