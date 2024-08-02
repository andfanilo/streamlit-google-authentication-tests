import streamlit.components.v1 as components
import firebase_admin
from firebase_admin import auth
from firebase_admin import credentials

try:
    firebase_admin.get_app()
except ValueError:
    cred = credentials.Certificate("./firebase_secret.json")
    firebase_admin.initialize_app(cred)

_component_func = components.declare_component(
    "st-firebase-signin", path="./streamlit_firebase_signin"
)

def st_firebase_signin(firebase_config):
    encoded_token = _component_func(
        firebaseConfig=firebase_config,
        default=None, 
        key="test",
    )

    if encoded_token is None:
        return None

    # if ValueError, let Streamlit bubble the error up
    decoded_token = auth.verify_id_token(encoded_token)
    return decoded_token
