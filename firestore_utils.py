import streamlit as st
import firebase_admin
from firebase_admin import credentials, firestore
import json

def connect_to_firestore():
    """
    Initializes Firestore using Streamlit secrets and returns the client.
    """
    if not firebase_admin._apps:
        # Parse the TOML dictionary into a Firebase credential dict
        firebase_secret = dict(st.secrets["firebase"])
        cred = credentials.Certificate(firebase_secret)
        firebase_admin.initialize_app(cred)
    return firestore.client()
