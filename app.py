import streamlit as st
import firebase_admin
from firebase_admin import credentials, firestore
import datetime

# --- FIRESTORE CONNECTION ---
def connect_to_firestore():
    if not firebase_admin._apps:
        firebase_secret = dict(st.secrets["firebase"])
        cred = credentials.Certificate(firebase_secret)
        firebase_admin.initialize_app(cred)
    return firestore.client()

# --- NORMALIZATION ---
def normalize_entry(entry):
    return {
        "user_name": entry.get("user_name", "Unknown"),
        "user_id": entry.get("user_id", "unknown"),
        "action": entry.get("action", "unknown"),
        "points_awarded": entry.get("points_awarded", 0),
        "device": entry.get("device") or entry.get("devices", "unknown"),
        "location": entry.get("location") or entry.get("locations", "unknown"),
        "timestamp": entry.get("timestamp", str(datetime.datetime.now()))
    }

# --- FETCH DATA ---
def fetch_activity_logs(db):
    docs = db.collection("activity_logs").stream()
    logs = [normalize_entry(doc.to_dict()) for doc in docs]
    logs = [log for log in logs if "user_name" in log and "points_awarded" in log]
    return logs

# --- CALCULATE STATS ---
def calculate_user_stats(logs):
    result = {}
    for entry in logs:
        user = entry["user_name"]
        device = entry["device"].lower()
        location = entry["location"].lower()
        action = entry["action"]
        points = entry["points_awarded"]

        if user not in result:
            result[user] = {
                "device": device,
                "location": location,
                "actions": {},
                "total_points": 0
            }

        result[user]["actions"][action] = result[user]["actions"].get(action, 0) + 1
        result[user]["total_points"] += points

    return result

# --- BUILD LEADERBOARD ---
def build_leaderboard(stats):
    leaderboard = sorted(
        [{"name": k, **v} for k, v in stats.items()],
        key=lambda x: x["total_points"],
        reverse=True
    )
    return leaderboard

# --- MAIN DASHBOARD ---
db = connect_to_firestore()
logs = fetch_activity_logs(db)
user_stats = calculate_user_stats(logs)

# --- UI ---
st.set_page_config(page_title="GamifyConnect Dashboard", layout="wide")
st.title("🎮 Gamification Dashboard")
st.write("Analyze gamified engagement patterns using actions like shares, posts, likes, and login streaks. Use filters below to explore user behavior, device types, and engagement stats.")

# --- SIDEBAR FILTERS ---
st.sidebar.header("🔍 Filter")
all_devices = list(set([v["device"] for v in user_stats.values()]))
all_locations = list(set([v["location"] for v in user_stats.values()]))

device_filter = st.sidebar.selectbox("Device", ["All"] + sorted(all_devices))
location_filter = st.sidebar.selectbox("Location", ["All"] + sorted(all_locations))

# --- FILTER LOGIC ---
filtered_users = {
    k: v for k, v in user_stats.items()
    if (device_filter == "All" or v["device"] == device_filter.lower()) and
       (location_filter == "All" or v["location"] == location_filter.lower())
}

# --- LEADERBOARD ---
st.subheader("🏆 Leaderboard")
leaderboard = build_leaderboard(filtered_users)

if leaderboard:
    for i, entry in enumerate(leaderboard):
        st.write(f"{entry['name']}: {entry['total_points']} pts")
else:
    st.warning("No leaderboard data available.")

# --- USER METRICS ---
st.subheader("📊 Key Engagement Metrics")
if filtered_users:
    for user, stats in filtered_users.items():
        st.markdown(f"**{user}** - {stats['total_points']} pts")
        st.json(stats['actions'])
else:
    st.info("No users match the selected filters.")
