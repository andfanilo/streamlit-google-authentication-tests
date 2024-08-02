let initialized = false;

function onDataFromPython(event) {
  const data = event.detail;

  const firebaseConfig = data.args.firebaseConfig;

  // should be initialized only once
  if (initialized === false) {
    const firebaseApp = firebase.initializeApp(firebaseConfig);
    console.log("Initialized Firebase");

    // Auth test
    const auth = firebaseApp.auth(firebaseApp);
    const ui = new firebaseui.auth.AuthUI(auth);

    const uiConfig = {
      callbacks: {
        signInSuccessWithAuthResult: function (authResult) {
          authResult.user.getIdToken().then(function (idToken) {
            Streamlit.setComponentValue(idToken);
            Streamlit.setFrameHeight(0);
            console.log("Handled Sign In Callback");
          }).catch(function(error) {
            console.log(error);
          });  
        },
      },
      signInFlow: "popup",
      signInOptions: [firebase.auth.GoogleAuthProvider.PROVIDER_ID],
    };

    ui.start("#firebaseui-auth-container", uiConfig);
    console.log("Initialized Firebase UI");
    initialized = true;
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
