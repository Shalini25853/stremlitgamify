import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from firestore_utils import connect_to_firestore, fetch_activity_logs, calculate_user_stats, build_leaderboard

# Set dashboard page config
st.set_page_config(
    page_title="GamifyConnect Dashboard",
    layout="wide",
    page_icon="🎮"
)

# Title and description
st.title("🎮 GamifyConnect – Social Media Gamification Dashboard")
st.markdown(
    "Analyze gamified engagement patterns using actions like shares, posts, likes, and login streaks. "
    "Use filters below to explore user behavior, device types, and engagement stats."
)

# Load and process data
db = connect_to_firestore()
logs = fetch_activity_logs(db)
user_stats = calculate_user_stats(logs)
leaderboard = build_leaderboard(user_stats)

# Sidebar Filters
st.sidebar.header("🔍 Filter")
devices = sorted(set(v.get("device", "Unknown") for v in user_stats.values()))
locations = sorted(set(v.get("location", "Unknown") for v in user_stats.values()))

selected_device = st.sidebar.selectbox("Device", ["All"] + devices)
selected_location = st.sidebar.selectbox("Location", ["All"] + locations)

# Filtered users
if filtered_users:
    cols = st.columns(min(4, len(filtered_users)))
    for col, user in zip(cols, filtered_users):
        stats = user_stats[user]
        with col:
            st.metric(label=f"{user}", value=f'{stats["total_points"]} pts')
else:
    st.info("No users match the selected filters.")


# Leaderboard Section
st.markdown("### 🏆 Leaderboard")
if leaderboard:
    df_leaderboard = pd.DataFrame(leaderboard)
    fig, ax = plt.subplots(figsize=(8, 4))
    sns.barplot(data=df_leaderboard, x="total_points", y="name", palette="coolwarm", edgecolor="black", ax=ax)
    ax.set_xlabel("Total Points")
    ax.set_ylabel("User")
    st.pyplot(fig)
else:
    st.warning("No leaderboard data available.")

# KPI Metrics Grid
st.markdown("### 📊 Key Engagement Metrics")
cols = st.columns(min(4, len(filtered_users)))
for i, (user, stats) in enumerate(filtered_users.items()):
    with cols[i % len(cols)]:
        st.metric(
            label=f"{user} (pts)",
            value=stats.get("total_points", 0),
            delta=f"{len(stats.get('badges', []))} badges"
        )

# Detailed User Summary
st.markdown("### 👤 User Activity Breakdown")
for user, stats in filtered_users.items():
    with st.expander(f"📋 {user}"):
        st.write(f"**Total Points:** {stats.get('total_points', 0)}")
        st.write(f"**Badges:** {', '.join(stats.get('badges', [])) or 'None'}")
        st.write("**Actions:**")
        st.json(stats.get("actions", {}))
        st.write("**Devices Used:**")
        st.json(stats.get("devices", {}))
