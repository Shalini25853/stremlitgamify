import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
from firestore_utils import connect_to_firestore
from gamification_engine import fetch_activity_logs, calculate_user_stats, build_leaderboard

# Page setup
st.set_page_config(page_title="GamifyConnect", layout="wide")
st.title("🎮 GamifyConnect – Social Media Gamification Dashboard")

# Connect to Firestore
db = connect_to_firestore()
logs = fetch_activity_logs(db)
user_stats = calculate_user_stats(logs)
leaderboard = build_leaderboard(user_stats)

# Sidebar filters
st.sidebar.header("📊 Filters")
device_filter = st.sidebar.selectbox("Device", ["All", "desktop", "mobile", "unknown"])
all_locations = sorted({v.get("location", "Unknown") for v in user_stats.values() if "location" in v})
location_filter = st.sidebar.selectbox("Location", ["All"] + all_locations)

# Filtered leaderboard
filtered_leaderboard = [
    user for user in leaderboard
    if (device_filter == "All" or device_filter in user_stats[user["name"]]["devices"]) and
       (location_filter == "All" or user_stats[user["name"]].get("location", "Unknown") == location_filter)
]

# 🎯 Leaderboard Section
st.markdown("## 🏆 Leaderboard")
if filtered_leaderboard:
    names = [v["name"] for v in filtered_leaderboard]
    points = [v["total_points"] for v in filtered_leaderboard]

    fig, ax = plt.subplots(figsize=(8, 4))
    bars = ax.bar(names, points, color="skyblue", edgecolor="gold", linewidth=2)
    ax.set_ylabel("Total Points")
    ax.set_title("Top Performers")
    st.pyplot(fig)
else:
    st.info("No users match the selected filters.")

# 🧠 User Details Section
st.markdown("## 📝 User Details")
selected_user = st.selectbox("Select a user", list(user_stats.keys()))

if selected_user:
    stats = user_stats[selected_user]
    st.subheader(f"{selected_user}")
    st.markdown(f"**Total Points:** {stats['total_points']}")
    st.markdown(f"**Badges:** {' '.join(['🏅 ' + b for b in stats['badges']]) if stats['badges'] else 'None'}")

    st.markdown("**Actions:**")
    st.json(stats["actions"])

    st.markdown("**Devices Used:**")
    st.json(stats["devices"])
