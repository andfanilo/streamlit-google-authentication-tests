from datetime import datetime

import streamlit as st
from google.auth.transport import requests
from google.oauth2 import id_token
from google_auth_oauthlib.flow import Flow

if "user" not in st.session_state:
    st.session_state.user = None
if "credentials" not in st.session_state:
    st.session_state.credentials = None

scopes = [
    "openid",
    "https://www.googleapis.com/auth/userinfo.email",
    "https://www.googleapis.com/auth/userinfo.profile",
]


@st.cache_resource
def get_flow():
    flow = Flow.from_client_secrets_file(
        "./client_secret.json",
        scopes=scopes,
        redirect_uri="http://localhost:8000/auth/code",
    )
    return flow


@st.cache_data
def get_auth_url(_flow: Flow):
    auth_url, state = _flow.authorization_url(prompt="consent")
    return (auth_url, state)


flow = get_flow()
auth_url, state = get_auth_url(flow)

if "auth_url" not in st.session_state:
    st.session_state.auth_url = auth_url
if "state" not in st.session_state:
    st.session_state.state = state

if not st.session_state.user:
    st.link_button(
        "🔑 Login with Google",
        url=st.session_state.auth_url,
        type="primary",
    )

# The user will get an authorization code.
# This code is used to get the access token.
with st.form("token_fetch"):
    c1, c2 = st.columns((4, 1), vertical_alignment="bottom")
    code_input = c1.text_input("Enter the authorization code: ")
    code_submit = c2.form_submit_button("Submit code")

if code_submit:
    flow.fetch_token(code=code_input.rstrip())
    credentials = flow.credentials
    id_info = id_token.verify_token(
        credentials.id_token,
        requests.Request(),
    )
    st.session_state.credentials = credentials
    st.session_state.user = id_info


if st.sidebar.button("Logout", type="primary", disabled=not st.session_state.user):
    st.session_state["user"] = None
    st.session_state["credentials"] = None
    st.session_state["auth_flow"] = None
    st.session_state["state"] = None
    st.rerun()

if not st.session_state.user:
    st.stop()

st.header(f"Hello {st.session_state.user['given_name']}")
st.image(st.session_state.user["picture"])

with st.sidebar:
    st.subheader("User info")
    st.json(st.session_state.user)

st.subheader(
    f"ID Token expires on: {datetime.fromtimestamp(st.session_state.user['exp'])}"
)

# You can use flow.credentials, or you can get a requests session
# using flow.authorized_session.
authorized_session = flow.authorized_session()
with st.expander("Get Info using authorized requests session"):
    st.json(
        authorized_session.get("https://www.googleapis.com/userinfo/v2/me").json(),
    )
