const video = document.getElementById("video");
const canvas = document.getElementById("canvas");
const photoPreview = document.getElementById("photoPreview");

let stream = null;
let capturedBlob = null;

/* Start Camera */
function startCamera() {
  navigator.mediaDevices.getUserMedia({ video: true })
    .then(s => {
      stream = s;
      video.srcObject = s;

      // SHOW capture button
      document.getElementById("captureBtn").hidden = false;
    })
    .catch(err => alert("Camera access denied"));
}


/* Capture Photo */
function capture() {
  const ctx = canvas.getContext("2d");
  ctx.drawImage(video, 0, 0, canvas.width, canvas.height);

  canvas.toBlob(blob => {
    capturedBlob = blob;
    photoPreview.src = URL.createObjectURL(blob);
  });

  // Stop camera
  stream.getTracks().forEach(track => track.stop());
  video.srcObject = null;

  // Hide capture button again
  document.getElementById("captureBtn").hidden = true;

  alert("Photo captured successfully");
}




/* Questionnaire Data */
const sections = [
{
title:"Section A: Body Build & Weight",
qs:[
["Q1. How would you describe your body frame?",["Thin / Lean","Medium","Heavy / Broad"]],
["Q2. How does your body weight change over time?",["Difficult to gain weight","Remains stable","Gains weight easily"]]
]
},
{
title:"Section B: Appetite & Digestion",
qs:[
["Q3. How is your appetite usually?",["Irregular or low","Strong and intense","Mild but steady"]],
["Q4. How is your digestion after meals?",["Irregular or bloating","Fast digestion","Slow digestion"]],
["Q5. How do you generally feel after eating?",["Bloated","Energetic","Sleepy"]],
["Q6. Bowel movements?",["Dry or irregular","Loose or frequent","Heavy"]]
]
}
];

/* Render Questions */
let qid = 1;
sections.forEach(section => {
  let block = `<div class="section"><h3>${section.title}</h3>`;
  section.qs.forEach(q => {
    block += `<div class="question"><b>${q[0]}</b><br>`;
    q[1].forEach(opt => {
      block += `<input type="checkbox" data-q="${qid}" value="${opt}"> ${opt}<br>`;
    });
    block += "</div>";
    qid++;
  });
  block += "</div>";
  questionsDiv.innerHTML += block;
});

/* Submit */
function submitForm() {

  if (!capturedBlob) {
    alert("Please capture photo first");
    return;
  }

  let answers = {};
  document.querySelectorAll("input[type=checkbox]:checked")
    .forEach(cb => {
      const q = cb.dataset.q;
      if (!answers[q]) answers[q] = [];
      answers[q].push(cb.value);
    });

  const formData = new FormData();
  formData.append("image", capturedBlob, "photo.png");
  formData.append("answers", JSON.stringify(answers));
  formData.append("name", document.getElementById("name").value);
  formData.append("age", document.getElementById("age").value);

  fetch("https://prakriti-website.onrender.com/predict", {
    method: "POST",
    body: formData
  })
  .then(res => res.json())
  .then(data => {
  document.getElementById("result").innerHTML =
    `Prakriti: <b>${data.prakriti}</b><br>
     Confidence: ${data.confidence}`;

  const link = document.getElementById("downloadLink");
  link.href = `https://YOUR-RENDER-URL.onrender.com/download/${data.record_id}`;
  link.innerHTML = "⬇ Download PDF Report";
});

}
