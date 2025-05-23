import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
from collections import defaultdict
from firestore_utils import connect_to_firestore, fetch_activity_logs, calculate_user_stats, build_leaderboard

st.set_page_config(page_title="GamifyConnect Dashboard", layout="wide")
st.title("🎮 GamifyConnect Dashboard")
st.markdown("""
Analyze gamified engagement patterns from social media-like activity such as posts, shares, likes, and login streaks. Use the filters to dive deep into user behavior by device or location.
""")

# Connect to Firestore
db = connect_to_firestore()
logs = fetch_activity_logs(db)
user_stats = calculate_user_stats(logs)
leaderboard = build_leaderboard(user_stats)

# Sidebar Filters
st.sidebar.header("🔍 Filter Users")
all_devices = sorted({d for _, stats in user_stats.items() for d in stats["device_counts"]})
all_locations = sorted({l for _, stats in user_stats.items() for l in stats["location_counts"]})

selected_device = st.sidebar.selectbox("Device", options=["All"] + all_devices)
selected_location = st.sidebar.selectbox("Location", options=["All"] + all_locations)

# Filtered Leaderboard
filtered_leaderboard = [
    (uid, stats) for uid, stats in leaderboard
    if (selected_device == "All" or stats["device_counts"].get(selected_device, 0) > 0)
    and (selected_location == "All" or stats["location_counts"].get(selected_location, 0) > 0)
]

# Leaderboard Section
st.subheader("🏆 Leaderboard")
if filtered_leaderboard:
    cols = st.columns(min(3, len(filtered_leaderboard)))
    for i, (user, stats) in enumerate(filtered_leaderboard):
        with cols[i % len(cols)]:
            st.metric(label=stats["name"], value=f"{stats['total_points']} pts")
else:
    st.warning("No users match the selected filters.")

# Key Engagement Metrics
st.subheader("📊 Key Engagement Metrics")
for uid, stats in filtered_leaderboard:
    with st.expander(f"{stats['name']}"):
        st.write(f"**Total Points:** {stats['total_points']}")
        st.write(f"**Badges:** {', '.join(stats['badges']) or 'None'}")
        st.write("**Actions:**")
        st.json(dict(stats["actions"]))
        st.write("**Devices Used:**")
        st.json(dict(stats["device_counts"]))
        st.write("**Locations:**")
        st.json(dict(stats["location_counts"]))

# Engagement Trends
st.subheader("📈 Engagement Trends")
df = pd.DataFrame(logs)
df["timestamp"] = pd.to_datetime(df["timestamp"], errors="coerce")
df.dropna(subset=["timestamp"], inplace=True)
df["date"] = df["timestamp"].dt.date
df_summary = df.groupby(["date", "action"]).size().unstack(fill_value=0)

if not df_summary.empty:
    fig, ax = plt.subplots()
    df_summary.plot(ax=ax, marker="o")
    ax.set_title("Engagement Over Time")
    ax.set_xlabel("Date")
    ax.set_ylabel("Count")
    ax.grid(True)
    st.pyplot(fig)
else:
    st.info("No trend data to display.")
