import html

import requests
import streamlit as st
from requests.exceptions import HTTPError

if "user" not in st.session_state:
    st.session_state.user = None


def st_redirect(url):
    source = f"location.href = '{url}'"
    wrapped_source = f"(async () => {{{source}}})()"
    st.markdown(
        f"""
        <div style="display:none" id="stredirect">
            <iframe src="javascript: \
                var script = document.createElement('script'); \
                script.type = 'text/javascript'; \
                script.text = {html.escape(repr(wrapped_source))}; \
                var thisDiv = window.parent.document.getElementById('stredirect'); \
                var rootDiv = window.parent.parent.parent.parent.document.getElementById('root'); \
                rootDiv.appendChild(script); \
                thisDiv.parentElement.parentElement.parentElement.style.display = 'none'; \
            "/>
        </div>
        """,
        unsafe_allow_html=True,
    )


# First, look for session cookie
if "__streamlit_session" not in st.context.cookies:
    if st.button("🔑 Login with Google", type="primary"):
        with st.spinner("Creating new session"):
            r = requests.post("http://localhost:8000/sessions")
            r.raise_for_status()
            resp = r.json()
        st_redirect(resp["auth_url"])
    st.stop()

# state from cookie after FastAPI redirect, try to get user
if "__streamlit_session" in st.context.cookies and not st.session_state.user:
    try:
        r = requests.get(
            f"http://localhost:8000/sessions/{st.context.cookies['__streamlit_session']}"
        )
        r.raise_for_status()
        resp = r.json()
        st.session_state.user = resp
    except HTTPError as exc:
        # I assume session got revoked so just destroy the cookie 😅
        st_redirect(f"http://localhost:8000/delete-cookie")


if not st.session_state.user:
    st.stop()

st.header(f"Hello {st.session_state.user['given_name']}")
st.image(st.session_state.user["picture"])

if st.sidebar.button("Logout", type="primary"):
    st.session_state.user = None
    r = requests.delete(
        f"http://localhost:8000/sessions/{st.context.cookies['__streamlit_session']}"
    )
    st_redirect(f"http://localhost:8000/delete-cookie")

with st.sidebar:
    st.subheader("User info")
    st.json(st.session_state.user)
