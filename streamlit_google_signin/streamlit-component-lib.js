function sendMessageToStreamlitClient(type, data) {
  const outData = Object.assign(
    {
      isStreamlitMessage: true,
      type: type,
    },
    data
  );
  window.parent.postMessage(outData, "*");
}

const Streamlit = {
  setComponentReady: function () {
    sendMessageToStreamlitClient("streamlit:componentReady", { apiVersion: 1 });
  },
  setFrameHeight: function (height) {
    sendMessageToStreamlitClient("streamlit:setFrameHeight", {
      height: height,
    });
  },
  setComponentValue: function (value) {
    sendMessageToStreamlitClient("streamlit:setComponentValue", {
      value: value,
    });
  },

  RENDER_EVENT: "streamlit:render",
  events: {
    addEventListener: function (type, callback) {
      window.addEventListener("message", function (event) {
        if (event.data.type === type) {
          event.detail = event.data;
          callback(event);
        }
      });
    },
  },
};
