import firebase_admin
from firebase_admin import credentials, firestore
import streamlit as st

def connect_to_firestore():
    """
    Initializes Firestore using Streamlit secrets and returns the client.
    """
    if not firebase_admin._apps:
        cred = credentials.Certificate(st.secrets["firebase"])
        firebase_admin.initialize_app(cred)
    return firestore.client()
