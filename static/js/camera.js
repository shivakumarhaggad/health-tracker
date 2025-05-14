marked.setOptions({
  breaks: true,
  gfm: true,
});

const video = document.getElementById("video");
const canvas = document.getElementById("canvas");
const startBtn = document.getElementById("startBtn");
const stopBtn = document.getElementById("stopBtn");
const captureBtn = document.getElementById("captureBtn");
const capturedImage = document.getElementById("capturedImage");
let mediaStream;

startBtn.addEventListener("click", () => {
  navigator.mediaDevices
    .getUserMedia({ video: true })
    .then((stream) => {
      mediaStream = stream;
      video.srcObject = stream;
      startBtn.disabled = true;
      stopBtn.disabled = false;
      captureBtn.disabled = false;
    })
    .catch((error) => {
      console.error("Error accessing camera: ", error);
    });
});

stopBtn.addEventListener("click", () => {
  if (mediaStream) {
    const tracks = mediaStream.getTracks();
    tracks.forEach((track) => track.stop());
    video.srcObject = null;
    startBtn.disabled = false;
    stopBtn.disabled = true;
    captureBtn.disabled = true;
  }
});

captureBtn.addEventListener("click", () => {
  const ctx = canvas.getContext("2d");
  ctx.drawImage(video, 0, 0, canvas.width, canvas.height);

  const dataUrl = canvas.toDataURL("image/png");
  capturedImage.src = dataUrl;

  sendImageToBackend(dataUrl);
});

function sendImageToBackend(imageDataUrl) {
  const formData = new FormData();
  formData.append("file", dataURLtoBlob(imageDataUrl));

  fetch("/process", {
    method: "POST",
    body: formData,
  })
    .then((response) => response.json())
    .then((data) => {
      if (data.response) {
        document.getElementById("result").innerHTML = marked.parse(
          data.response
        );
        document.getElementById("capturedImage").src = data.image_url;
      } else {
        document.getElementById("result").innerText = `Error: ${data.error}`;
      }
    })
    .catch((error) => {
      document.getElementById("result").innerText = `Error: ${error.message}`;
    });
}

function dataURLtoBlob(dataURL) {
  const byteString = atob(dataURL.split(",")[1]);
  const arrayBuffer = new ArrayBuffer(byteString.length);
  const uintArray = new Uint8Array(arrayBuffer);
  for (let i = 0; i < byteString.length; i++) {
    uintArray[i] = byteString.charCodeAt(i);
  }
  return new Blob([uintArray], { type: "image/png" });
}

const form = document.getElementById("uploadForm");
form.addEventListener("submit", async (event) => {
  event.preventDefault();

  const fileInput = document.getElementById("imageFile");
  const urlInput = document.getElementById("imageUrl");
  const formData = new FormData();

  if (fileInput.files.length > 0) {
    formData.append("file", fileInput.files[0]);
  } else if (urlInput.value.trim()) {
    formData.append("image_url", urlInput.value.trim());
  } else {
    document.getElementById("result").innerText =
      "Please upload an image or provide a URL.";
    return;
  }

  try {
    const response = await fetch("/process", {
      method: "POST",
      body: formData,
    });

    if (!response.ok) {
      throw new Error(`HTTP error! Status: ${response.status}`);
    }

    const data = await response.json();
    if (data.response) {
      document.getElementById("result").innerHTML = marked.parse(data.response);
      document.getElementById("capturedImage").src = data.image_url;
    } else {
      document.getElementById("result").innerText = `Error: ${data.error}`;
    }
  } catch (error) {
    document.getElementById("result").innerText = `Error: ${error.message}`;
  }
});

const clearBtn = document.getElementById("clearBtn");

clearBtn.addEventListener("click", () => {
  document.getElementById("imageFile").value = "";
  document.getElementById("imageUrl").value = "";
  document.getElementById("capturedImage").src = "";
  document.getElementById("result").innerHTML = "";
});
