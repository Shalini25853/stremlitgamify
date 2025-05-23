import streamlit as st
import firebase_admin
from firebase_admin import credentials, firestore

# Initialize Firestore
def connect_to_firestore():
    if not firebase_admin._apps:
        firebase_secret = dict(st.secrets["firebase"])
        cred = credentials.Certificate(firebase_secret)
        firebase_admin.initialize_app(cred)
    return firestore.client()

# Normalize each log entry from Firestore
def normalize_entry(entry):
    return {
        "user_name": entry.get("user_name", "Unknown"),
        "user_id": entry.get("user_id", "unknown"),
        "action": entry.get("action", "unknown"),
        "points_awarded": entry.get("points_awarded", 0),
        "device": entry.get("device") or entry.get("devices", "unknown"),
        "location": entry.get("location") or entry.get("locations", "unknown"),
        "timestamp": entry.get("timestamp", "")
    }

# Fetch and normalize all logs
def fetch_activity_logs(db):
    docs = db.collection("activity_logs").stream()
    logs = [normalize_entry(doc.to_dict()) for doc in docs]
    return logs

# Aggregate logs into per-user stats
def calculate_user_stats(logs):
    result = {}
    for entry in logs:
        user = entry["user_name"]
        device = entry.get("device", "unknown")
        location = entry.get("location", "unknown")
        action = entry.get("action", "unknown")
        points = entry.get("points_awarded", 0)

        if user not in result:
            result[user] = {
                "device": device,
                "location": location,
                "actions": {},
                "total_points": 0
            }

        # Count actions
        if action in result[user]["actions"]:
            result[user]["actions"][action] += 1
        else:
            result[user]["actions"][action] = 1

        result[user]["total_points"] += points

    return result

# Build leaderboard from stats
def build_leaderboard(stats):
    leaderboard = sorted(
        [{"name": name, **data} for name, data in stats.items()],
        key=lambda x: x["total_points"],
        reverse=True
    )
    return leaderboard
