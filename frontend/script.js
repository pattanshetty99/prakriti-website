const video = document.getElementById("video");
const canvas = document.getElementById("canvas");
const questionsDiv = document.getElementById("questions");
let capturedBlob = null;

/* Start Webcam */
navigator.mediaDevices.getUserMedia({ video: true })
  .then(stream => video.srcObject = stream);

/* Capture Image */
function capture() {
  const ctx = canvas.getContext("2d");
  ctx.drawImage(video, 0, 0, canvas.width, canvas.height);
  canvas.toBlob(blob => capturedBlob = blob);
  alert("Photo captured");
}

/* Questions */
const questions = Array.from({length: 46}, (_, i) => ({
  id: i+1,
  text: "Question " + (i+1),
  options: ["Vata", "Pitta", "Kapha"]
}));

questions.forEach(q => {
  let html = `<div class="question"><b>Q${q.id}</b> ${q.text}<br>`;
  q.options.forEach(opt => {
    html += `<input type="checkbox" value="${opt}" data-q="${q.id}"> ${opt}<br>`;
  });
  html += "</div>";
  questionsDiv.innerHTML += html;
});

/* Submit */
function submitForm() {

  if (!capturedBlob) {
    alert("Please capture photo");
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
      `Predicted Prakriti: <b>${data.prakriti}</b><br>
       Confidence: ${data.confidence}`;
  });
}
