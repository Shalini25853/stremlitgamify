import streamlit as st
import matplotlib.pyplot as plt
from firestore_utils import connect_to_firestore, fetch_activity_logs, calculate_user_stats, build_leaderboard

st.set_page_config(page_title="GamifyConnect Dashboard", layout="wide")
st.title("🎮 GamifyConnect – Social Media Gamification Dashboard")
st.markdown("""
Analyze gamified engagement patterns using actions like shares, posts, likes, and login streaks. 
Use filters below to explore user behavior, device types, and engagement stats.
""")

# Connect to Firestore
db = connect_to_firestore()
logs = fetch_activity_logs(db)
user_stats = calculate_user_stats(logs)
leaderboard = build_leaderboard(user_stats)

# Sidebar Filters
st.sidebar.header("🔍 Filter")
device_filter = st.sidebar.selectbox("Device", ["All"] + sorted(set(v.get("device", "") for v in user_stats.values())))
location_filter = st.sidebar.selectbox("Location", ["All"] + sorted(set(v.get("location", "") for v in user_stats.values())))

# Apply Filters
filtered_users = [
    user for user, stats in user_stats.items()
    if (device_filter == "All" or stats.get("device") == device_filter)
    and (location_filter == "All" or stats.get("location") == location_filter)
]

# Leaderboard
st.subheader("🏆 Leaderboard")
if leaderboard:
    names = [v["name"] for v in leaderboard]
    points = [v["total_points"] for v in leaderboard]
    fig, ax = plt.subplots()
    ax.bar(names, points, color="skyblue", edgecolor="gold", linewidth=2)
    ax.set_ylabel("Total Points")
    ax.set_title("Top Gamified Users")
    st.pyplot(fig)
else:
    st.warning("No leaderboard data available.")

# Key Metrics Section
st.subheader("📊 Key Engagement Metrics")
if filtered_users:
    cols = st.columns(min(4, len(filtered_users)))
    for col, user in zip(cols, filtered_users):
        stats = user_stats[user]
        with col:
            st.metric(label=f"{user}", value=f'{stats["total_points"]} pts')
else:
    st.info("No users match the selected filters.")
