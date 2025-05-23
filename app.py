import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
from firestore_utils import connect_to_firestore
from gamification_engine import fetch_activity_logs, calculate_user_stats, build_leaderboard

# ---- CONFIG ----
st.set_page_config(page_title="GamifyConnect", layout="wide")

st.title("🎮 GamifyConnect – Social Media Gamification Dashboard")
st.markdown("Analyze gamified engagement patterns using actions like shares, posts, likes, and streaks.")

# ---- FIRESTORE CONNECTION ----
db = connect_to_firestore()
logs = fetch_activity_logs(db)
user_stats = calculate_user_stats(logs)
leaderboard = build_leaderboard(user_stats)

# ---- LEADERBOARD SECTION ----
st.markdown("## 🏆 Leaderboard")

names = [v["name"] for _, v in leaderboard]
points = [v["total_points"] for _, v in leaderboard]

fig, ax = plt.subplots()
ax.bar(names, points, color="skyblue", edgecolor="gold", linewidth=3)
ax.set_ylabel("Total Points")
ax.set_title("Total Engagement by User")
st.pyplot(fig)

# ---- USER FILTERS ----
st.markdown("## 🔎 Filter Users")
device_filter = st.selectbox("Device", ["All"] + sorted({v.get("device", "unknown") for v in user_stats.values()}))
location_filter = st.selectbox("Location", ["All"] + sorted({v.get("location", "unknown") for v in user_stats.values()}))

# ---- USER INSIGHTS ----
# ---- USER INSIGHTS ----
st.markdown("## 📋 User Details")
for user_id, stats in user_stats.items():
    if (device_filter == "All" or stats.get("device") == device_filter) and \
       (location_filter == "All" or stats.get("location") == location_filter):
        with st.expander(f"{stats['name']}"):
            st.markdown(f"**Total Points:** {stats.get('total_points', 0)}")
            st.markdown(f"**Badges:** {' • '.join(stats.get('badges', []))}")
            st.markdown("**Actions:**")
            st.json(stats.get("actions", {}))
            st.markdown("**Devices Used:**")
            st.json(stats.get("devices", {}))

