import os

import streamlit as st

# When running locally, disable OAuthlib's HTTPs verification.
# When running in production *do not* leave this option enabled.
# Explained in https://requests-oauthlib.readthedocs.io/en/latest/examples/real_world_example.html NB
os.environ["OAUTHLIB_INSECURE_TRANSPORT"] = "1"

st.title("Google Auth")
st.logo("./images/google.png")

with st.sidebar:
    st.header("Resources")
    st.link_button(
        "Google OpenID Connect",
        "https://developers.google.com/identity/openid-connect/openid-connect",
    )
    st.link_button(
        "Google API Client Library for Python Docs",
        "https://googleapis.github.io/google-api-python-client/docs/",
    )
    st.link_button(
        "Using OAuth 2.0 for Web Server Applications",
        "https://developers.google.com/identity/protocols/oauth2/web-server",
    )
    st.link_button(
        "google-auth-oauthlib",
        "https://google-auth-oauthlib.readthedocs.io/en/latest/index.html",
    )
    st.link_button("google-auth", "https://google-auth.readthedocs.io/en/master/")
    st.link_button(
        "requests-oauthlib", "https://requests-oauthlib.readthedocs.io/en/latest/"
    )
    st.link_button(
        "GCP Console - Credentials",
        "https://console.cloud.google.com/apis/credentials/consent?project=sandbox-414119",
    )
    st.divider()

get_user_credentials = st.Page(
    "./app/1_get_user_credentials.py",
    title="1. Google OAuth's Get User Credentials",
    icon=":material/home:",
)
run_local_server = st.Page(
    "./app/2_run_local_server.py",
    title="2. Google OAuth's run local server",
    icon=":material/dns:",
)
fastapi_redirect = st.Page(
    "./app/3_fastapi_redirect.py", title="3. FastAPI catches Redirect URI", icon=":material/bolt:"
)
fastapi_session_cookies = st.Page(
    "./app/4_fastapi_session_cookies.py", title="4. Session cookies with FastAPI", icon=":material/forward:"
)
google_signin_component = st.Page(
    "./app/5_google_signin_component.py", title="5. Google Sign in component", icon=":material/login:"
)
firebase_signin_component = st.Page(
    "./app/6_firebase_signin_component.py",
    title="6. Firebase UI component",
    icon=":material/expand_circle_down:",
)

nav = st.navigation([
    get_user_credentials, 
    run_local_server, 
    fastapi_redirect, 
    fastapi_session_cookies, 
    google_signin_component, 
    firebase_signin_component,
])
nav.run()
