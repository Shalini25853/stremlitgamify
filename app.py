import streamlit as st
import matplotlib.pyplot as plt
import pandas as pd
from firestore_utils import connect_to_firestore, fetch_activity_logs, calculate_user_stats, build_leaderboard

st.set_page_config(page_title="Gamification Dashboard", layout="wide")
st.title("🎮 Gamification Dashboard")
st.markdown("""
Analyze gamified engagement patterns using actions like shares, posts, likes, and login streaks. Use filters below to explore user behavior, device types, and engagement stats.
""")

# Connect to Firestore
db = connect_to_firestore()
logs = fetch_activity_logs(db)
user_stats = calculate_user_stats(logs)
leaderboard = build_leaderboard(user_stats)

# Sidebar Filters
st.sidebar.title("🔍 Filter")
unique_devices = sorted(set([v.get("device", "unknown") for v in user_stats.values()]))
unique_locations = sorted(set([v.get("location", "unknown") for v in user_stats.values()]))

device_filter = st.sidebar.selectbox("Device", ["All"] + unique_devices)
location_filter = st.sidebar.selectbox("Location", ["All"] + unique_locations)

# Filtered Users
filtered_users = {
    user: stats for user, stats in user_stats.items()
    if (device_filter == "All" or stats.get("device") == device_filter)
    and (location_filter == "All" or stats.get("location") == location_filter)
}

# Leaderboard Section
st.subheader("🏆 Leaderboard")
if filtered_users:
    sorted_leaderboard = build_leaderboard(filtered_users)
    for entry in sorted_leaderboard:
        st.write(f"**{entry['name']}**: {entry['total_points']} pts")
else:
    st.info("No leaderboard data available.")

# Engagement Metrics Section
st.subheader("📊 Key Engagement Metrics")
if filtered_users:
    for user, stats in filtered_users.items():
        st.markdown(f"**{user}** - {stats['total_points']} pts")
        st.json(stats.get("actions", {}))
else:
    st.info("No users match the selected filters.")

# 📈 Engagement Trend Chart
st.subheader("📈 Engagement Trends")
if logs:
    df = pd.DataFrame(logs)
    df["timestamp"] = pd.to_datetime(df["timestamp"], errors='coerce')
    df.dropna(subset=["timestamp"], inplace=True)
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
