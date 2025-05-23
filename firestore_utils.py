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
    logs_ref = db.collection("user_logs")
    docs = logs_ref.stream()
    logs = []
    for doc in docs:
        log = doc.to_dict()
        log["id"] = doc.id
        logs.append(log)
    return logs

def calculate_user_stats(logs):
    stats = {}
    for entry in logs:
        name = entry.get("name")
        if name not in stats:
            stats[name] = {
                "total_points": 0,
                "badges": [],
                "actions": {},
                "devices": {},
                "location": entry.get("location", "unknown")
            }
        stats[name]["total_points"] += entry.get("points", 0)

        for badge in entry.get("badges", []):
            if badge not in stats[name]["badges"]:
                stats[name]["badges"].append(badge)

        for action, count in entry.get("actions", {}).items():
            stats[name]["actions"][action] = stats[name]["actions"].get(action, 0) + count

        for device, count in entry.get("device", {}).items():
            stats[name]["devices"][device] = stats[name]["devices"].get(device, 0) + count

    return stats

def build_leaderboard(stats):
    leaderboard = sorted(
        [{"name": k, **v} for k, v in stats.items()],
        key=lambda x: x["total_points"],
        reverse=True
    )
    return leaderboard
