import random
from datetime import datetime, timedelta
from firebase_admin import firestore

# Define actions and their point values
ACTION_POINTS = {
    "post": 10,
    "comment": 5,
    "like": 2,
    "share": 7,
    "login_streak": 5
}

DEVICES = ["mobile", "desktop"]
LOCATIONS = ["Boston", "New York", "San Francisco", "Chicago", "Austin"]

USERS = {
    "u001": "David",
    "u002": "Porter",
    "u003": "Kevin",
    "u004": "Peter",
    "u005": "John"
}

def simulate_user_activity(db, num_logs_per_user=10):
    for user_id, name in USERS.items():
        for _ in range(random.randint(num_logs_per_user - 3, num_logs_per_user + 3)):
            action = random.choice(list(ACTION_POINTS.keys()))
            timestamp = datetime.now() - timedelta(
                days=random.randint(0, 6),
                hours=random.randint(0, 23),
                minutes=random.randint(0, 59)
            )

            log = {
                "user_id": user_id,
                "user_name": name,
                "action": action,
                "points_awarded": ACTION_POINTS[action],
                "device": random.choice(DEVICES),
                "location": random.choice(LOCATIONS),
                "timestamp": timestamp.isoformat()
            }

            db.collection("activity_logs").add(log)

    print("✅ Simulated activity logs uploaded.")
