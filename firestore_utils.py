import streamlit as st
import firebase_admin
from firebase_admin import credentials, firestore

def connect_to_firestore():
    if not firebase_admin._apps:
        firebase_secret = dict(st.secrets["firebase"])
        cred = credentials.Certificate(firebase_secret)
        firebase_admin.initialize_app(cred)
    return firestore.client()

def fetch_activity_logs(db):
    logs_ref = db.collection("activity_logs")
    docs = logs_ref.stream()

    user_logs = {}

    for doc in docs:
        data = doc.to_dict()
        user = data.get("user_name", "Unknown")
        action = data.get("action")
        points = data.get("points_awarded", 0)
        device = data.get("device", "unknown")
        location = data.get("location", "unknown")

        if user not in user_logs:
            user_logs[user] = {
                "user": user,
                "device": device,
                "location": location,
                "actions": {},
                "total_points": 0
            }

        # Increment action count
        if action in user_logs[user]["actions"]:
            user_logs[user]["actions"][action] += 1
        else:
            user_logs[user]["actions"][action] = 1

        # Add points
        user_logs[user]["total_points"] += points

    return list(user_logs.values())


def calculate_user_stats(logs):
    result = {}

    for entry in logs:
        user = entry["user"]
        device = entry.get("device", "unknown")
        location = entry.get("location", "unknown")
        actions = entry.get("actions", {})
        points = entry.get("total_points", 0)

        result[user] = {
            "device": device,
            "location": location,
            "actions": actions,
            "total_points": points
        }

    return result


def build_leaderboard(stats):
    leaderboard = sorted(
        [{"name": k, **v} for k, v in stats.items()],
        key=lambda x: x["total_points"],
        reverse=True
    )
    return leaderboard
