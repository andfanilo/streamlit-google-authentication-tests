import json
import streamlit as st

from streamlit_firebase_signin import st_firebase_signin

if "user" not in st.session_state:
    st.session_state.user = None

with open("firebase_client.json", "r") as f:
    firebase_config = json.load(f)

if not st.session_state.user:
    token = st_firebase_signin(firebase_config)
    if token is None:
        st.stop()
    st.session_state.user = token

if not st.session_state.user:
    st.stop()

if st.sidebar.button("Logout", type="primary"):
    st.session_state["user"] = None
    st.session_state["credentials"] = None
    st.rerun()

st.header(f"Hello {st.session_state.user['name']}")
st.image(st.session_state.user["picture"])

with st.sidebar:
    st.subheader("User info")
    st.json(st.session_state.user)
