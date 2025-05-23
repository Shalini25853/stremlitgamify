import streamlit as st
import firebase_admin
from firebase_admin import credentials, firestore

# --- Firebase Connection ---
def connect_to_firestore():
    if not firebase_admin._apps:
        firebase_secret = dict(st.secrets["firebase"])
        cred = credentials.Certificate(firebase_secret)
        firebase_admin.initialize_app(cred)
    return firestore.client()

# --- Normalize Each Entry ---
def normalize_entry(entry):
    return {
        "user_name": entry.get("user_name", "Unknown"),
        "user_id": entry.get("user_id", "unknown"),
        "action": entry.get("action", "unknown"),
        "points_awarded": entry.get("points_awarded", 0),
        "device": entry.get("device") or entry.get("devices", "unknown"),
        "location": entry.get("location") or entry.get("locations", "unknown"),
        "timestamp": entry.get("timestamp", "")
    }

# --- Fetch and Normalize Activity Logs ---
def fetch_activity_logs(db):
    docs = db.collection("activity_logs").stream()
    return [normalize_entry(doc.to_dict()) for doc in docs]

# --- Compute Stats Per User ---
def calculate_user_stats(logs):
    user_logs = {}
    for entry in logs:
        user = entry["user_name"]
        if user not in user_logs:
            user_logs[user] = {
                "device": entry.get("device", "unknown"),
                "location": entry.get("location", "unknown"),
                "actions": {},
                "total_points": 0
            }

        action = entry.get("action")
        user_logs[user]["actions"][action] = user_logs[user]["actions"].get(action, 0) + 1
        user_logs[user]["total_points"] += entry.get("points_awarded", 0)

    return user_logs

# --- Build Leaderboard ---
def build_leaderboard(stats):
    return sorted(
        [{"name": k, **v} for k, v in stats.items()],
        key=lambda x: x["total_points"],
        reverse=True
    )

# --- Streamlit UI ---
db = connect_to_firestore()
logs = fetch_activity_logs(db)
user_stats = calculate_user_stats(logs)

# Sidebar Filters
devices = sorted(set(entry.get("device", "unknown") for entry in logs))
locations = sorted(set(entry.get("location", "unknown") for entry in logs))

st.sidebar.header("🔍 Filter")
device_filter = st.sidebar.selectbox("Device", ["All"] + devices)
location_filter = st.sidebar.selectbox("Location", ["All"] + locations)

# Apply filters
filtered_users = {
    user: stats for user, stats in user_stats.items()
    if (device_filter == "All" or stats["device"] == device_filter)
    and (location_filter == "All" or stats["location"] == location_filter)
}

# --- Main Dashboard ---
st.title("🎮 GamifyConnect – Social Media Gamification Dashboard")
st.markdown("""
Analyze gamified engagement patterns using actions like shares, posts, likes, and login streaks. 
Use filters below to explore user behavior, device types, and engagement stats.
""")

# Leaderboard
st.subheader("🏆 Leaderboard")
leaderboard = build_leaderboard(filtered_users)
if leaderboard:
    for user in leaderboard:
        st.write(f"**{user['name']}**: {user['total_points']} pts")
else:
    st.info("No leaderboard data available.")

# Key Engagement Metrics
st.subheader("📊 Key Engagement Metrics")
if filtered_users:
    for user, stats in filtered_users.items():
        st.markdown(f"**{user}** - {stats['total_points']} pts")
        st.json(stats["actions"])
else:
    st.warning("No users match the selected filters.")
