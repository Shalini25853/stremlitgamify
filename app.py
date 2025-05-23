import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
from firestore_utils import connect_to_firestore, fetch_activity_logs, calculate_user_stats, build_leaderboard

# Page configuration
st.set_page_config(page_title="GamifyConnect Dashboard", layout="wide")

# Custom style
st.markdown("""
    <style>
        .main {
            background-color: #0E1117;
            color: #FFFFFF;
            font-family: 'Segoe UI', sans-serif;
        }
        h1, h2, h3 {
            color: #F39C12;
        }
        .stSelectbox > div > div {
            background-color: #1E1E1E;
            color: white;
        }
        .metric-box {
            padding: 1rem;
            background: #1E1E1E;
            border-radius: 10px;
            margin-bottom: 1rem;
        }
    </style>
""", unsafe_allow_html=True)

# Header
st.title("🎮 GamifyConnect Dashboard")
st.markdown("""
Analyze gamified engagement patterns from social media-like activity such as posts, shares, likes, and login streaks. 
Use the filters to dive deep into user behavior by device or location.
""")

# Connect to Firestore
db = connect_to_firestore()
logs = fetch_activity_logs(db)
user_stats = calculate_user_stats(logs)
leaderboard = build_leaderboard(user_stats)

# Sidebar Filters
st.sidebar.header("🔍 Filter Users")
unique_devices = sorted(set([v.get("device", "unknown") for v in user_stats.values()]))
unique_locations = sorted(set([v.get("location", "unknown") for v in user_stats.values()]))

device_filter = st.sidebar.selectbox("Device", ["All"] + unique_devices)
location_filter = st.sidebar.selectbox("Location", ["All"] + unique_locations)

# Apply filters
filtered_users = {
    user: stats for user, stats in user_stats.items()
    if (device_filter == "All" or stats.get("device") == device_filter)
    and (location_filter == "All" or stats.get("location") == location_filter)
}

# Leaderboard
st.markdown("## 🏆 Leaderboard")
if filtered_users:
    sorted_leaderboard = build_leaderboard(filtered_users)
    col1, col2, col3 = st.columns(3)
    for i, (user, stats) in enumerate(sorted_leaderboard):
        with [col1, col2, col3][i % 3]:
            st.metric(label=f"{user}", value=f"{stats['total_points']} pts")
else:
    st.warning("No leaderboard data matches the filters.")

# Engagement Metrics Grid
st.markdown("## 📊 Key Engagement Metrics")
if filtered_users:
    grid_cols = st.columns(3)
    for i, (user, stats) in enumerate(filtered_users.items()):
        with grid_cols[i % 3]:
            st.markdown(f"### 👤 {user}")
            st.markdown(f"<div class='metric-box'><strong>Total Points:</strong> {stats['total_points']}<br><strong>Badges:</strong> {' | '.join(stats.get('badges', [])) or 'None'}</div>", unsafe_allow_html=True)
            st.markdown("**Actions:**")
            st.json(stats.get("actions", {}))
            st.markdown("**Device Usage:**")
            st.json(stats.get("device_counts", {}))
            st.markdown("**Location Usage:**")
            st.json(stats.get("location_counts", {}))
else:
    st.info("No engagement data matches the filters.")

# Engagement Trends
st.markdown("## 📈 Engagement Trends Over Time")
if logs:
    df = pd.DataFrame(logs)
    df["timestamp"] = pd.to_datetime(df["timestamp"], errors='coerce')
    df.dropna(subset=["timestamp"], inplace=True)
    df["date"] = df["timestamp"].dt.date
    df_summary = df.groupby(["date", "action"]).size().unstack(fill_value=0)

    fig, ax = plt.subplots(figsize=(10, 5))
    df_summary.plot(ax=ax, kind="line", marker="o")
    ax.set_title("Engagement Over Time", fontsize=14)
    ax.set_xlabel("Date")
    ax.set_ylabel("Interaction Count")
    ax.grid(True, linestyle="--", alpha=0.6)
    st.pyplot(fig)
else:
    st.info("No timestamp data available to plot trends.")
