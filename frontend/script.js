// -------------------------
// DOM ELEMENTS
// -------------------------
const video = document.getElementById("video");
const canvas = document.getElementById("canvas");
const photoPreview = document.getElementById("photoPreview");
const captureBtn = document.getElementById("captureBtn");
const questionsDiv = document.getElementById("questions");
const downloadLink = document.getElementById("downloadLink");
const resultCard = document.getElementById("resultCard");
const resultDiv = document.getElementById("result");

let stream = null;
let capturedBlob = null;
let answers = {};
let useFrontCamera = true;

// -------------------------
// CAMERA FUNCTIONS
// -------------------------

function stopCamera() {
  if (stream) {
    stream.getTracks().forEach(track => track.stop());
    stream = null;
  }
}

/* Start Camera */
function startCamera() {
  stopCamera();

  const constraints = {
    video: {
      facingMode: useFrontCamera ? "user" : "environment"
    }
  };

  navigator.mediaDevices.getUserMedia(constraints)
    .then(s => {
      stream = s;
      video.srcObject = s;
      video.style.display = "block";
      video.play();

      captureBtn.hidden = false;
      photoPreview.src = "";
      photoPreview.style.display = "none";
    })
    .catch(err => {
      console.error(err);
      alert("Camera access denied or unavailable");
    });
}

/* Switch Camera */
function switchCamera() {
  useFrontCamera = !useFrontCamera;
  startCamera();
}

/* Capture Photo */
function capture() {
  if (!stream) {
    alert("Start camera first");
    return;
  }

  const ctx = canvas.getContext("2d");
  canvas.width = video.videoWidth;
  canvas.height = video.videoHeight;
  ctx.drawImage(video, 0, 0);

  canvas.toBlob(blob => {
    capturedBlob = blob;
    photoPreview.src = URL.createObjectURL(blob);
    photoPreview.style.display = "block";
  });

  stopCamera();
  video.srcObject = null;
  video.style.display = "none";
  captureBtn.hidden = true;

  alert("✅ Photo captured successfully");
}

// -------------------------
// QUESTIONNAIRE DATA
// -------------------------
const sections = [
  {
    title: "Section A: Body Build & Weight",
    qs: [
      ["Q1. How would you describe your body frame?", ["Thin / Lean", "Medium", "Heavy / Broad"]],
      ["Q2. How does your body weight change over time?", ["Difficult to gain weight", "Remains stable", "Gains weight easily"]]
    ]
  },
  {
    title: "Section B: Appetite & Digestion",
    qs: [
      ["Q3. How is your appetite usually?", ["Irregular or low", "Strong and intense", "Mild but steady"]],
      ["Q4. How is your digestion after meals?", ["Irregular or bloating", "Fast digestion", "Slow digestion"]],
      ["Q5. How do you generally feel after eating?", ["Bloated", "Energetic", "Sleepy"]],
      ["Q6. Bowel movements?", ["Dry or irregular", "Loose or frequent", "Heavy"]]
    ]
  }
];

// -------------------------
// RENDER QUESTIONS
// -------------------------
let qid = 1;

sections.forEach(section => {
  let block = `<div class="section"><h3>${section.title}</h3>`;

  section.qs.forEach(q => {
    block += `<div class="question"><b>${q[0]}</b>`;
    block += `<div class="option-grid">`;

    q[1].forEach(opt => {
      block += `
        <div class="option-box"
             onclick="toggleOption(this, '${qid}', '${opt}')">
          ${opt}
        </div>
      `;
    });

    block += `</div></div>`;
    qid++;
  });

  block += `</div>`;
  questionsDiv.innerHTML += block;
});

// -------------------------
// OPTION TOGGLE HANDLER
// -------------------------
function toggleOption(box, qid, value) {
  box.classList.toggle("selected");

  if (!answers[qid]) {
    answers[qid] = [];
  }

  if (answers[qid].includes(value)) {
    answers[qid] = answers[qid].filter(v => v !== value);
  } else {
    answers[qid].push(value);
  }
}

// -------------------------
// SUBMIT FORM
// -------------------------
function submitForm() {

  if (!capturedBlob) {
    alert("Please capture photo first");
    return;
  }

  const name = document.getElementById("name").value.trim();
  const age = document.getElementById("age").value.trim();

  if (!name || !age) {
    alert("Please enter name and age");
    return;
  }

  if (Object.keys(answers).length === 0) {
    alert("Please select at least one option");
    return;
  }

  const formData = new FormData();
  formData.append("image", capturedBlob, "photo.png");
  formData.append("answers", JSON.stringify(answers));
  formData.append("name", name);
  formData.append("age", age);

  resultDiv.innerHTML = "⏳ Processing...";
  resultCard.style.display = "block";
  downloadLink.style.display = "none";

  fetch("https://prakriti-website.onrender.com/predict", {
    method: "POST",
    body: formData
  })
  .then(res => {
    if (!res.ok) throw new Error("Server error");
    return res.json();
  })
  .then(data => {

    resultDiv.innerHTML =
      `✅ <b>Prakriti:</b> ${data.prakriti}<br>
       🎯 <b>Confidence:</b> ${data.confidence}`;

    if (data.pdf_id) {
      downloadLink.href =
        `https://prakriti-website.onrender.com/download/${data.pdf_id}`;
      downloadLink.innerHTML = "⬇ Download PDF Report";
      downloadLink.style.display = "inline-block";
    }

    resultCard.scrollIntoView({ behavior: "smooth" });
  })
  .catch(err => {
    console.error(err);
    alert("Submission failed. Please try again.");
    resultDiv.innerHTML = "";
    resultCard.style.display = "none";
  });
}
