import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
from firestore_utils import connect_to_firestore
from gamification_engine import fetch_activity_logs, calculate_user_stats, build_leaderboard

# Page config
st.set_page_config(page_title="GamifyConnect", layout="wide")

st.title("🎮 GamifyConnect – Social Media Gamification Dashboard")

# Connect to Firestore
db = connect_to_firestore()

# Fetch logs and compute stats
logs = fetch_activity_logs(db)
user_stats = calculate_user_stats(logs)
leaderboard = build_leaderboard(user_stats)

# Display leaderboard
st.markdown("## 🏆 Leaderboard")
names = [v["name"] for _, v in leaderboard]
points = [v["total_points"] for _, v in leaderboard]

fig, ax = plt.subplots()
ax.bar(names, points, color="skyblue", edgecolor="gold", linewidth=3)
ax.set_ylabel("Total Points")
st.pyplot(fig)

st.markdown("---")

# Sidebar filters
st.sidebar.header("🔍 Filter Users")
device_filter = st.sidebar.selectbox("Device", ["All", "mobile", "desktop", "unknown"])
location_filter = st.sidebar.selectbox("Location", ["All"] + sorted(set(v["location"] for _, v in user_stats.items())))

# Horizontal buttons
user_names = [v["name"] for _, v in leaderboard]
selected_user = st.radio("👥 Choose User", user_names, horizontal=True)

# User details section
st.markdown("### 📝 User Details")
user_data = next(v for _, v in leaderboard if v["name"] == selected_user)

# Apply filters
if device_filter != "All":
    user_data["devices"] = {k: v for k, v in user_data["devices"].items() if k == device_filter}
if location_filter != "All" and user_data["location"] != location_filter:
    st.warning(f"No data for {selected_user} in {location_filter}")
else:
    col1, col2 = st.columns(2)
    with col1:
        st.metric("Total Points", user_data["total_points"])
    with col2:
        st.markdown("**Badges:** " + ", ".join(user_data["badges"]))

    st.markdown("**Actions:**")
    st.json(user_data["actions"])

    st.markdown("**Devices Used:**")
    st.json(user_data["devices"])
