# GamifyConnect – Social Media Gamification Dashboard

GamifyConnect is a real-time engagement analytics dashboard designed to simulate user behavior on a social media platform. Built using Python, Streamlit, and Google Cloud Firestore, it tracks activities like posts, comments, likes, and shares, then awards points and badges to users using gamification logic.

While this model currently simulates 5 users for clarity, it is fully scalable. The Firestore database and analytics logic are designed to handle larger datasets and could easily support real-time analytics for hundreds of users with minimal changes.

## Features

- Real-time data from GCP Firestore
- Simulated social media user behavior for 5+ users
- Point system and badge-based engagement scoring
- Leaderboard and user engagement breakdowns
- Daily activity trend chart (time-series visualization)
- Interactive filters by device type and location
- CSV export of leaderboard
- Fully deployed on Streamlit Cloud

## Tech Stack

- Python
- Streamlit
- Google Cloud Platform (Firestore)
- Matplotlib & Pandas
- Firebase Admin SDK

## How to Run Locally

```bash
git clone https://github.com/yourusername/gamifyconnect.git
cd gamifyconnect
pip install -r requirements.txt
streamlit run app.py
```

Screenshots

![image](https://github.com/user-attachments/assets/528401d8-b529-4d75-aa82-943f077df341)
![image](https://github.com/user-attachments/assets/07f185a4-941a-4853-b1e8-31fd80c52e60)

Live Demo
Visit: https://stremlitgamify-cwjiidztgqomuftcvt4mdw.streamlit.app/ 

Author
Shalini James Paulraj

