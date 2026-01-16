// -------------------------
// DOM ELEMENTS
// -------------------------
const video = document.getElementById("video");
const canvas = document.getElementById("canvas");
const photoPreview = document.getElementById("photoPreview");
const captureBtn = document.getElementById("captureBtn");
const questionsDiv = document.getElementById("questions");
const downloadLink = document.getElementById("downloadLink");

let stream = null;
let capturedBlob = null;

// -------------------------
// CAMERA FUNCTIONS
// -------------------------

/* Start Camera */
function startCamera() {
  navigator.mediaDevices.getUserMedia({ video: true })
    .then(s => {
      stream = s;
      video.srcObject = s;
      video.style.display = "block";
      video.play();

      captureBtn.hidden = false;     // Show capture button
      photoPreview.src = "";         // Clear old photo
    })
    .catch(err => {
      console.error(err);
      alert("Camera access denied or unavailable");
    });
}

/* Capture Photo */
function capture() {
  const ctx = canvas.getContext("2d");
  canvas.width = video.videoWidth;
  canvas.height = video.videoHeight;

  ctx.drawImage(video, 0, 0, canvas.width, canvas.height);

  canvas.toBlob(blob => {
    capturedBlob = blob;
    photoPreview.src = URL.createObjectURL(blob);
    photoPreview.style.display = "block";
  });

  // Stop camera
  if (stream) {
    stream.getTracks().forEach(track => track.stop());
  }

  video.srcObject = null;
  video.style.display = "none";
  captureBtn.hidden = true;

  alert("Photo captured successfully");
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
    block += `<div class="question"><b>${q[0]}</b><br>`;

    q[1].forEach(opt => {
      block += `
        <label>
          <input type="checkbox" data-q="${qid}" value="${opt}">
          ${opt}
        </label><br>`;
    });

    block += "</div>";
    qid++;
  });

  block += "</div>";
  questionsDiv.innerHTML += block;
});

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

  let answers = {};
  document.querySelectorAll("input[type=checkbox]:checked")
    .forEach(cb => {
      const q = cb.dataset.q;
      if (!answers[q]) answers[q] = [];
      answers[q].push(cb.value);
    });

  if (Object.keys(answers).length === 0) {
    alert("Please answer at least one question");
    return;
  }

  const formData = new FormData();
  formData.append("image", capturedBlob, "photo.png");
  formData.append("answers", JSON.stringify(answers));
  formData.append("name", name);
  formData.append("age", age);

  document.getElementById("result").innerHTML = "⏳ Processing...";
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

    document.getElementById("result").innerHTML =
      `✅ Prakriti: <b>${data.prakriti}</b><br>
       Confidence: ${data.confidence}`;

    // Enable PDF download
    if (data.pdf_id) {
      downloadLink.href = `https://prakriti-website.onrender.com/download/${data.pdf_id}`;
      downloadLink.innerHTML = "⬇ Download PDF Report";
      downloadLink.style.display = "inline-block";
    }
  })
  .catch(err => {
    console.error(err);
    alert("Submission failed. Please try again.");
    document.getElementById("result").innerHTML = "";
  });
}
