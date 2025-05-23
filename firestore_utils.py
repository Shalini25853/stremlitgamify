import streamlit as st
from firebase_admin import credentials, firestore
import firebase_admin

def connect_to_firestore():
    if not firebase_admin._apps:
        firebase_secret = dict(st.secrets["firebase"])
        cred = credentials.Certificate(firebase_secret)
        firebase_admin.initialize_app(cred)
    return firestore.client()
