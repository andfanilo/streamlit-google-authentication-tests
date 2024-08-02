import streamlit as st

from streamlit_google_signin import st_google_signin

if "user" not in st.session_state:
    st.session_state.user = None

if not st.session_state.user:
    token = st_google_signin(st.secrets.client_id)
    if token is None:
        st.stop()
    st.session_state.user = token

if not st.session_state.user:
    st.stop()

if st.sidebar.button("Logout", type="primary"):
    st.session_state["user"] = None
    st.session_state["credentials"] = None
    st.rerun()

st.header(f"Hello {st.session_state.user['given_name']}")
st.image(st.session_state.user["picture"])

with st.sidebar:
    st.subheader("User info")
    st.json(st.session_state.user)
