let initialized = false;

function onDataFromPython(event) {
  const data = event.detail;

  const client_id = data.args.client_id;

  // should be initialized only once
  if (initialized === false) {
    google.accounts.id.initialize({
      client_id: client_id,
      callback: handleCredentialResponse,
    });
    google.accounts.id.renderButton(document.getElementById("buttonDiv"), {
      theme: "outline",
      size: "large",
    });
    initialized = true;
    console.log("Initialized Google Sign In Button");
  }

  Streamlit.setFrameHeight(document.documentElement.clientHeight);
}

function handleCredentialResponse(response) {
  Streamlit.setComponentValue(response.credential);
  console.log("Handled Sign In Callback");
  Streamlit.setFrameHeight(0);
}

Streamlit.events.addEventListener(Streamlit.RENDER_EVENT, onDataFromPython);
Streamlit.setComponentReady();
