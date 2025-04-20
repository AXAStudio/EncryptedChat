import streamlit as st
from firebase_admin import credentials, firestore, initialize_app
from datetime import datetime, timezone
from streamlit_autorefresh import st_autorefresh
import firebase_admin
from firebase_admin import credentials, firestore

if not firebase_admin._apps:
    cred = credentials.Certificate("encryptedchat-18a72-firebase-adminsdk-fbsvc-353e881291.json")
    firebase_admin.initialize_app(cred)

db = firestore.client()

if "username" not in st.session_state or not st.session_state.username:
    username = st.text_input("Enter your name to start chatting:")
    if username:
        st.session_state.username = username
        st.rerun()
else:
    st_autorefresh(interval=2000, key="autoRefresh")

    if "room_code_visible" not in st.session_state:
        st.session_state.room_code_visible = True

    shownText = "Hide Room Code" if st.session_state.room_code_visible else "Show Room Code"
    st.markdown(f"You're logged in as: **{st.session_state.username}**")
    toggle_button = st.button(shownText, key="toggle_button")
    if toggle_button:
        st.session_state.room_code_visible = not st.session_state.room_code_visible
        

    if st.session_state.room_code_visible:
        room = st.text_input("Room Code", value="general").lower().strip()
        st.session_state.room_code = room 
        st.markdown(f"You're in room: `{room}`")
    else:
        room = st.session_state.get("room_code", "general")

    chat_ref = db.collection("chatrooms").document(room).collection("messages")

    with st.form("send_form", clear_on_submit=True):
        msg = st.text_input("Type a message")
        submitted = st.form_submit_button("Send")
        if submitted and msg:
            chat_ref.add({
                "user": st.session_state.username,
                "message": msg,
                "timestamp": datetime.now(timezone.utc)
            })

    messages = chat_ref.order_by("timestamp", direction=firestore.Query.ASCENDING).stream()
    st.write("Messages:")
    for m in messages:
        data = m.to_dict()
        time = data["timestamp"].strftime("%H:%M:%S")
        st.markdown(f"**[{time}] {data['user']}**: {data['message']}")

