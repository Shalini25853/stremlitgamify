import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
from firestore_utils import connect_to_firestore
from gamification_engine import fetch_activity_logs, calculate_user_stats, build_leaderboard

st.set_page_config(page_title="GamifyConnect", layout="centered")
st.title("🎮 GamifyConnect – Social Media Gamification Dashboard")

db = connect_to_firestore()

logs = fetch_activity_logs(db)
user_stats = calculate_user_stats(logs)
leaderboard = build_leaderboard(user_stats)

st.markdown("## 🏆 Leaderboard")
names = [v["name"] for _, v in leaderboard]
points = [v["total_points"] for _, v in leaderboard]

fig, ax = plt.subplots()
bars = ax.bar(names, points, color="skyblue")
for i, (_, stats) in enumerate(leaderboard):
    if stats["badges"]:
        bars[i].set_edgecolor("gold")
        bars[i].set_linewidth(3)
ax.set_ylabel("Total Points")
st.pyplot(fig)

# --- Filters ---
st.markdown("## 🔍 Filter Users")
all_devices = sorted(set([d for _, v in user_stats.items() for d in v["device_counts"]]))
selected_device = st.selectbox("Device", ["All"] + all_devices)

all_locations = sorted(set([l for _, v in user_stats.items() for l in v["location_counts"]]))
selected_location = st.selectbox("Location", ["All"] + all_locations)

# --- User Summaries ---
st.markdown("## 📋 User Details")
for uid, stats in leaderboard:
    if (selected_device != "All" and stats["device_counts"].get(selected_device, 0) == 0) or \
       (selected_location != "All" and stats["location_counts"].get(selected_location, 0) == 0):
        continue

    with st.expander(f"{stats['name']}"):
        st.write(f"**Total Points:** {stats['total_points']}")
        st.write(f"**Badges:** {', '.join(stats['badges']) if stats['badges'] else 'None'}")
        st.write("**Actions:**")
        st.json(dict(stats["actions"]))
        st.write("**Devices Used:**")
        st.json(dict(stats["device_counts"]))
        st.write("**Locations:**")
        st.json(dict(stats["location_counts"]))
