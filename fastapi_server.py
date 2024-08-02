from contextlib import asynccontextmanager
from datetime import datetime
from datetime import timedelta
from datetime import timezone

from fastapi import FastAPI
from fastapi import status
from fastapi.exceptions import HTTPException
from fastapi.responses import HTMLResponse
from fastapi.responses import RedirectResponse
from fastapi.responses import Response
from google.auth.transport import requests
from google.oauth2 import id_token
from google_auth_oauthlib.flow import Flow


@asynccontextmanager
async def lifespan(app: FastAPI):
    # This should be a remote Redis or Firestore...
    # for expiry and horizontal scalability
    app.state.fake_sessions = {}
    yield


app = FastAPI(title="My Google OAuth middleware", lifespan=lifespan)


@app.get("/")
def hello_world():
    return {"Hello": "World"}


@app.get(
    "/auth/code",
    summary="Parses the redirect URI for authorization code",
    description="Passed as redirect URI from Google. Uses state for session validation",
    tags=["oauth2"],
)
def callback_parse_redirect(state: str, code: str):
    return HTMLResponse(f"""
    <html>
        <head>
            <title>FastAPI Server</title>
        </head>
        <body>
            <div>
                <h2>State to check against Streamlit</h2>
                {state}
            </div>
            <div>
                <h2>Authorization Code to copy back to Streamlit</h2>
                {code}
            </div>
        </body>
    </html>
    """)


@app.get(
    "/auth/token",
    summary="Updates session with tokens from parsed authorization code",
    description="Passed as redirect URI from Google. Uses state for session validation. Updates session with OAuth tokens",
    tags=["oauth2"],
)
def callback_google_oauth2(state: str, code: str):
    # Check state from auth server actually exists
    if state not in app.state.fake_sessions:
        return HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid state parameter",
        )

    flow = Flow.from_client_secrets_file(
        "./client_secret.json",
        scopes=[
            "openid",
            "https://www.googleapis.com/auth/userinfo.email",
            "https://www.googleapis.com/auth/userinfo.profile",
        ],
    )
    flow.redirect_uri = "http://localhost:8000/auth/token"
    flow.fetch_token(code=code)

    credentials = flow.credentials
    access_token = credentials.token
    refresh_token = credentials.refresh_token
    token = credentials.id_token

    id_info = id_token.verify_token(
        credentials.id_token,
        requests.Request(),
    )

    app.state.fake_sessions[state]["access_token"] = access_token
    app.state.fake_sessions[state]["refresh_token"] = refresh_token
    app.state.fake_sessions[state]["id_token"] = token
    app.state.fake_sessions[state]["id_info"] = id_info

    response = RedirectResponse("https://localhost:8501/fastapi_session_cookies")
    response.set_cookie(
        "__streamlit_session",
        state,
        expires=app.state.fake_sessions[state]["expires_at"],
        secure=True,
        httponly=True,
        samesite="strict",
    )
    return response


@app.get("/sessions", tags=["local"])
def get_all_sessions():
    return app.state.fake_sessions


@app.post("/sessions", tags=["local"])
def create_session():
    flow = Flow.from_client_secrets_file(
        "./client_secret.json",
        scopes=[
            "openid",
            "https://www.googleapis.com/auth/userinfo.email",
            "https://www.googleapis.com/auth/userinfo.profile",
        ],
    )
    flow.redirect_uri = "http://localhost:8000/auth/token"
    auth_url, state = flow.authorization_url(
        access_type="offline",
        prompt="select_account",
    )
    now = datetime.now(timezone.utc)
    expire = now + timedelta(minutes=15)
    body = {
        "auth_url": auth_url,
        "state": state,
        "created_at": now,
        "expires_at": expire,
    }
    app.state.fake_sessions[state] = body
    return body


@app.get("/sessions/{state}", tags=["local"])
def get_session_info_user(state: str):
    if state not in app.state.fake_sessions:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="This session wasn't found",
        )

    # shouldn't happen if cookie disappeared
    # but maybe someone stole this so let's revoke
    if datetime.now(timezone.utc) > app.state.fake_sessions[state]["expires_at"]:
        del app.state.fake_sessions[state]
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="This session expired",
        )

    id_info = app.state.fake_sessions[state]["id_info"]
    return {
        "given_name": id_info["given_name"],
        "email": id_info["email"],
        "picture": id_info["picture"],
    }


@app.delete("/sessions/{state}", tags=["local"])
def revoke_session(state: str):
    if state in app.state.fake_sessions:
        del app.state.fake_sessions[state]
        response = Response(status_code=status.HTTP_200_OK)
        return response
    else:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)


@app.get("/delete-cookie", tags=["local"])
def remove_cookie():
    response = RedirectResponse("https://localhost:8501/fastapi_session_cookies")
    response.delete_cookie("__streamlit_session")
    return response
