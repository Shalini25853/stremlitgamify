import streamlit as st
import matplotlib.pyplot as plt
import pandas as pd
from collections import defaultdict
from firestore_utils import connect_to_firestore

# Set up page
st.set_page_config(page_title="Gamification Dashboard", layout="wide")
st.title("🎮 Gamification Dashboard")
st.markdown("""
Analyze gamified engagement patterns using actions like shares, posts, likes, and login streaks. Use filters below to explore user behavior, device types, and engagement stats.
""")

# Firestore connection and log fetching
db = connect_to_firestore()
logs = db.collection("activity_logs").stream()

data = []
for doc in logs:
    record = doc.to_dict()
    record["timestamp"] = pd.to_datetime(record.get("timestamp"), errors="coerce")
    if record["timestamp"] is not pd.NaT:
        data.append(record)

df = pd.DataFrame(data)

# Normalize and summarize user stats
user_stats = defaultdict(lambda: {
    "total_points": 0,
    "actions": defaultdict(int),
    "device": "unknown",
    "location": "unknown"
})

for row in data:
    user = row.get("user_name", "Unknown")
    user_stats[user]["total_points"] += row.get("points_awarded", 0)
    user_stats[user]["actions"][row.get("action", "")] += 1
    user_stats[user]["device"] = row.get("device", "unknown")
    user_stats[user]["location"] = row.get("location", "unknown")

# Leaderboard Section
st.subheader("🏆 Leaderboard")
leaderboard = sorted(user_stats.items(), key=lambda x: x[1]["total_points"], reverse=True)
if leaderboard:
    for user, stats in leaderboard:
        st.write(f"**{user}**: {stats['total_points']} pts")
else:
    st.info("No leaderboard data available.")

# Filter Sidebar
st.sidebar.title("🔍 Filter")
devices = sorted(set(stats["device"] for stats in user_stats.values()))
locations = sorted(set(stats["location"] for stats in user_stats.values()))

selected_device = st.sidebar.selectbox("Device", ["All"] + devices)
selected_location = st.sidebar.selectbox("Location", ["All"] + locations)

# Engagement Metrics Section
st.subheader("📊 Key Engagement Metrics")
filtered_users = {
    user: stats for user, stats in user_stats.items()
    if (selected_device == "All" or stats["device"] == selected_device)
    and (selected_location == "All" or stats["location"] == selected_location)
}

if filtered_users:
    for user, stats in filtered_users.items():
        st.markdown(f"**{user}** - {stats['total_points']} pts")
        st.json(dict(stats.get("actions", {})))
else:
    st.info("No users match the selected filters.")

# Engagement Trend Chart
st.subheader("📈 Engagement Trends")
if not df.empty:
    df = df.dropna(subset=["timestamp"])
    df["date"] = df["timestamp"].dt.date
    df_summary = df.groupby(["date", "action"]).size().unstack(fill_value=0)

    fig, ax = plt.subplots()
    df_summary.plot(ax=ax, kind="line", marker="o")
    ax.set_title("Engagement Over Time")
    ax.set_ylabel("Count")
    ax.set_xlabel("Date")
    ax.grid(True)
    st.pyplot(fig)
else:
    st.info("No log data available for trend chart.")
