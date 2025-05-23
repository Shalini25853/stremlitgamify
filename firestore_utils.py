# firestore_utils.py

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
    return [doc.to_dict() for doc in docs]

def calculate_user_stats(logs):
    stats = {}
    for log in logs:
        user = log["user"]
        if user not in stats:
            stats[user] = {
                "points": 0,
                "badges": [],
                "actions": {},
                "devices": {},
                "location": log.get("location", "Unknown")
            }
        stats[user]["points"] += log["points"]
        action = log["action"]
        stats[user]["actions"][action] = stats[user]["actions"].get(action, 0) + 1
        device = log["device"]
        stats[user]["devices"][device] = stats[user]["devices"].get(device, 0) + 1
        badge = log.get("badge")
        if badge and badge not in stats[user]["badges"]:
            stats[user]["badges"].append(badge)
    return stats
