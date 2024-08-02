import streamlit.components.v1 as components

from google.oauth2 import id_token
from google.auth.transport import requests

_component_func = components.declare_component(
    "st-google-signin", path="./streamlit_google_signin"
)


def st_google_signin(client_id):
    encoded_token = _component_func(
        client_id=client_id, 
        default=None, 
        key=client_id,
    )

    if encoded_token is None:
        return None

    # if ValueError on verification, let Streamlit bubble the error up
    decoded_token = id_token.verify_oauth2_token(
        encoded_token,
        requests.Request(),
        client_id,
    )

    # I"m supposed to do exp and hd claim check too...
    # Use sub as identifier

    return decoded_token
