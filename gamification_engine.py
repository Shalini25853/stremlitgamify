from collections import defaultdict

# Badge thresholds
BADGE_RULES = {
    "post": {"threshold": 5, "badge": "🏅 Content Creator"},
    "comment": {"threshold": 10, "badge": "🗣️ Engager"},
    "like": {"threshold": 20, "badge": "👍 Supporter"},
    "share": {"threshold": 3, "badge": "📣 Influencer"},
    "login_streak": {"threshold": 7, "badge": "🔥 Loyal User"}
}

def fetch_activity_logs(db):
    logs = db.collection("activity_logs").stream()
    return [log.to_dict() for log in logs]

def calculate_user_stats(logs):
    user_stats = defaultdict(lambda: {
        "name": "",
        "total_points": 0,
        "actions": defaultdict(int),
        "badges": [],
        "device_counts": defaultdict(int),
        "location_counts": defaultdict(int)
    })

    for entry in logs:
        uid = entry["user_id"]
        uname = entry["user_name"]
        action = entry["action"]
        points = entry["points_awarded"]
        device = entry.get("device", "unknown")
        location = entry.get("location", "unknown")

        user_stats[uid]["name"] = uname
        user_stats[uid]["total_points"] += points
        user_stats[uid]["actions"][action] += 1
        user_stats[uid]["device_counts"][device] += 1
        user_stats[uid]["location_counts"][location] += 1

    for uid, stats in user_stats.items():
        for action, rule in BADGE_RULES.items():
            if stats["actions"][action] >= rule["threshold"]:
                stats["badges"].append(rule["badge"])

    return dict(user_stats)

def build_leaderboard(user_stats):
    return sorted(user_stats.items(), key=lambda x: x[1]["total_points"], reverse=True)
