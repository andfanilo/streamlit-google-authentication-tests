from datetime import datetime

import streamlit as st
from google.auth.transport import requests
from google.oauth2 import id_token
from google_auth_oauthlib import get_user_credentials
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError


if "user" not in st.session_state:
    st.session_state.user = None
if "credentials" not in st.session_state:
    st.session_state.credentials = None


def login_callback():
    credentials = get_user_credentials(
        scopes=[
            "openid",
            "https://www.googleapis.com/auth/userinfo.email",
            "https://www.googleapis.com/auth/userinfo.profile",
            "https://www.googleapis.com/auth/calendar.events.readonly",
        ],
        client_id=st.secrets.client_id,
        client_secret=st.secrets.client_secret,
        # limit redirect URI server to http://localhost:9000
        minimum_port=9000,
        maximum_port=9001,
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

st.divider()

with st.expander("Upcoming Events in Google Calendar"):
    try:
        service = build("calendar", "v3", credentials=st.session_state.credentials)

        # Call the Calendar API for the next 10 events
        now = datetime.now().isoformat() + "Z"
        events_result = (
            service.events()
            .list(
                calendarId="primary",
                timeMin=now,
                maxResults=10,
                singleEvents=True,
                orderBy="startTime",
            )
            .execute()
        )
        events = events_result.get("items", [])

        if not events:
            st.info("No upcoming events found", icon="ℹ️")
            st.stop()

        for event in events:
            start = event["start"].get("dateTime", event["start"].get("date"))
            st.markdown(f":blue[{start}] - **{event['summary']}**")

    except HttpError as error:
        st.error(f"An error occurred: {error}")
