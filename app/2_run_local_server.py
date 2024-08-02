import streamlit as st
from google.auth.transport import requests
from google.oauth2 import id_token
from google_auth_oauthlib.flow import InstalledAppFlow

if "user" not in st.session_state:
    st.session_state.user = None
if "credentials" not in st.session_state:
    st.session_state.credentials = None

flow = InstalledAppFlow.from_client_secrets_file(
    "./client_secret.json",
    scopes=[
        "openid",
        "https://www.googleapis.com/auth/userinfo.email",
        "https://www.googleapis.com/auth/userinfo.profile",
    ],
    redirect_uri="http://localhost:9000/",
)


def login_callback():
    credentials = flow.run_local_server(
        # bind_addr="0.0.0.0", # so it works in Docker container
        port=9000,
        open_browser=True,  # pass to False in container
        success_message="Authentication Complete. You can go back to the app if this window is not automatically closed.",
    )
    id_info = id_token.verify_token(
        credentials.id_token,
        requests.Request(),
    )
    st.session_state.credentials = credentials
    st.session_state.user = id_info


if not st.session_state.user:
    st.button(
        "🔑 Login with Google",
        type="primary",
        on_click=login_callback,
    )
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
