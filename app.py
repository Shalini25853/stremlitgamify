import streamlit as st
import matplotlib.pyplot as plt
import pandas as pd
from collections import defaultdict
from firestore_utils import connect_to_firestore, fetch_activity_logs, calculate_user_stats, build_leaderboard

# --- Page Config ---
st.set_page_config(page_title="GamifyConnect Dashboard", layout="wide")
st.title("🎮 GamifyConnect Dashboard")
st.markdown("""
Analyze gamified engagement patterns from social media-like activity such as posts, shares, likes, and login streaks. Use the filters to dive deep into user behavior by device or location.
""")

# --- Connect & Fetch ---
db = connect_to_firestore()
logs = fetch_activity_logs(db)
user_stats = calculate_user_stats(logs)
leaderboard = build_leaderboard(user_stats)

# --- Sidebar Filters ---
st.sidebar.header("🔍 Filter Users")
all_devices = sorted(list(set([d for _, v in user_stats.items() for d in v["device_counts"]])))
all_locations = sorted(list(set([l for _, v in user_stats.items() for l in v["location_counts"]])))

selected_device = st.sidebar.selectbox("Device", options=["All"] + all_devices)
selected_location = st.sidebar.selectbox("Location", options=["All"] + all_locations)

# --- Filtered Leaderboard ---
filtered_leaderboard = [
    (uid, stats) for uid, stats in leaderboard
    if (selected_device == "All" or stats["device_counts"].get(selected_device, 0) > 0)
    and (selected_location == "All" or stats["location_counts"].get(selected_location, 0) > 0)
]

# --- Leaderboard Section ---
st.subheader("🏆 Leaderboard")
if filtered_leaderboard:
    for i, (user, stats) in enumerate(filtered_leaderboard):
        st.markdown(f"**{stats['name']}**: {stats['total_points']} pts")
else:
    st.info("No users match the selected filters.")

# --- Key Engagement Metrics ---
st.subheader("📊 Key Engagement Metrics")
if filtered_leaderboard:
    for uid, stats in filtered_leaderboard:
        with st.expander(f"{stats['name']} – {stats['total_points']} pts"):
            st.write(f"**Badges:** {', '.join(stats['badges']) if stats['badges'] else 'None'}")
            st.write("**Actions:**")
            st.json(dict(stats["actions"]))
            st.write("**Devices Used:**")
            st.json(dict(stats["device_counts"]))
            st.write("**Locations:**")
            st.json(dict(stats["location_counts"]))
else:
    st.info("No user data available for selected filters.")

# --- Engagement Trends Chart ---
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
    st.info("No engagement data available for visualization.")
