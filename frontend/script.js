// -------------------------
// DOM ELEMENTS
// -------------------------
const video = document.getElementById("video");
const canvas = document.getElementById("canvas");
const photoPreview = document.getElementById("photoPreview");
const captureBtn = document.getElementById("captureBtn");
const questionsDiv = document.getElementById("questions");
const resultCard = document.getElementById("resultCard");
const resultDiv = document.getElementById("result");
const submitBtn = document.querySelector(".submit-btn");
 
let stream = null;
let capturedBlob = null;
let answers = {};
let useFrontCamera = true;
 
// -------------------------
// DISABLE SUBMIT IF ALREADY SUBMITTED (SESSION ONLY)
// -------------------------
if (sessionStorage.getItem("prakriti_submitted")) {
  submitBtn.disabled = true;
  submitBtn.innerText = "Already Submitted";
  submitBtn.style.opacity = "0.6";
  submitBtn.style.cursor = "not-allowed";
 
  resultCard.style.display = "block";
  resultDiv.innerHTML = "✅ You have already submitted the data. Thank you!";
}
 
// -------------------------
// FACE DETECTION (must be defined before stopCamera/startCamera)
// -------------------------
let faceDetector = null;
let detectionLoop = null;
 
async function startFaceDetection() {
  const overlay = document.querySelector(".face-overlay");

  // Simple brightness-based fallback: just check if video is active
  // and pulse green every 2s to show it's working
  if (!("FaceDetector" in window)) {
    // Fallback: turn green when face roughly detected via canvas pixel analysis
    detectionLoop = setInterval(() => {
      if (!stream) return;
      const tempCanvas = document.createElement("canvas");
      tempCanvas.width = 64;
      tempCanvas.height = 64;
      const ctx = tempCanvas.getContext("2d");
      ctx.drawImage(video, 0, 0, 64, 64);
      const data = ctx.getImageData(16, 8, 32, 48).data;

      let skinPixels = 0;
      for (let i = 0; i < data.length; i += 4) {
        const r = data[i], g = data[i+1], b = data[i+2];
        // Skin tone detection (works for all skin tones)
        if (r > 60 && g > 40 && b > 20 && r > g && r > b && (r - g) > 10) {
          skinPixels++;
        }
      }

      const ratio = skinPixels / (32 * 48);
      overlay.classList.toggle("aligned", ratio > 0.25);
    }, 400);
    return;
  }

  // Native FaceDetector path
  faceDetector = new FaceDetector({ fastMode: true });
  detectionLoop = setInterval(async () => {
    if (!stream) return;
    try {
      const faces = await faceDetector.detect(video);
      if (faces.length === 0) { overlay.classList.remove("aligned"); return; }
      const face = faces[0].boundingBox;
      const vw = video.videoWidth, vh = video.videoHeight;
      const isAligned =
        face.left >= vw * 0.10 && face.right <= vw * 0.90 &&
        face.top >= vh * 0.05 && face.bottom <= vh * 0.95;
      overlay.classList.toggle("aligned", isAligned);
    } catch (e) {}
  }, 300);
}
 
function stopFaceDetection() {
  clearInterval(detectionLoop);
  detectionLoop = null;
  document.querySelector(".face-overlay").classList.remove("aligned");
}
 
// -------------------------
// CAMERA FUNCTIONS
// -------------------------
function stopCamera() {
  if (stream) {
    stream.getTracks().forEach(track => track.stop());
    stream = null;
  }
  stopFaceDetection();
}
 
function startCamera() {
  stopCamera();
  navigator.mediaDevices.getUserMedia({
    video: { facingMode: useFrontCamera ? "user" : "environment" }
  })
  .then(s => {
    stream = s;
    video.srcObject = s;
    video.classList.add("active");
    photoPreview.classList.remove("active");
    captureBtn.hidden = false;
    startFaceDetection();
  })
  .catch(() => alert("Camera access failed"));
}
 
function switchCamera() {
  useFrontCamera = !useFrontCamera;
  startCamera();
}
 
function capture() {
  const ctx = canvas.getContext("2d");
  canvas.width = video.videoWidth;
  canvas.height = video.videoHeight;
  ctx.translate(canvas.width, 0);
  ctx.scale(-1, 1);
  ctx.drawImage(video, 0, 0);

  canvas.toBlob(blob => {
    capturedBlob = blob;
    photoPreview.src = URL.createObjectURL(blob);
    photoPreview.classList.add("active");    // shows the image
    video.classList.remove("active");        // hides the video
  });

  stopCamera();
  captureBtn.hidden = true;
}


// -------------------------
// QUESTIONS
// -------------------------
const sections = [
  {
    title: "Physical & Body Characteristics",
    qs: [
      ["Q1. How would you describe your overall body build and muscle development?", ["Thin, lean, low muscle mass", "Moderately built, proportionate muscles", "Broad, heavy, well-developed muscles"]],
      ["Q2. How would you describe your body frame or chest width?", ["Narrow / slim frame", "Medium frame", "Broad / wide frame"]],
      ["Q3. What best describes your natural skin complexion or color?", ["Black / dark", "Dark brown", "Dusky / wheatish", "Light brown / fair"]],
      ["Q4. What best describes the condition of your nails?", ["Dry, rough, brittle, easily breaking", "Sharp, flexible, pink, lustrous", "Thick, oily, smooth, polished"]],
      ["Q5. How sensitive is your skin to environment, cosmetics, or weather?", ["Very sensitive, easily irritated", "Normal sensitivity", "Less sensitive / thick skin"]]
    ]
  },
  {
    title: "Digestion, Appetite & Metabolism",
    qs: [
      ["Q6. How would you describe your appetite?", ["Irregular or low appetite", "Moderate and steady appetite", "Strong appetite, frequent hunger"]],
      ["Q7. How would you describe your digestion after meals?", ["Weak digestion, bloating or gas", "Moderate digestion", "Strong digestion, fast metabolism"]],
      ["Q8. How would you describe your metabolism and weight change?", ["Slow metabolism, difficult to gain weight", "Moderate metabolism", "Fast metabolism, weight changes easily"]],
      ["Q9. How are your bowel movements usually?", ["Constipation, dry stools", "Loose stools, frequent", "Regular and well-formed"]]
    ]
  },
  {
    title: "Food Preferences, Climate and Temperature Sensitivity",
    qs: [
      ["Q10. Which taste(s) do you naturally prefer? (Select more than one if applicable)", ["Sweet","Sour","Salty","Bitter","Pungent (spicy)","Astringent (dry / rough taste)"]],
      ["Q11. Which climate do you feel most comfortable in?", ["Cold climate", "Moderate climate", "Warm climate"]],
      ["Q12. How sensitive are you to cold temperatures?", ["Very sensitive to cold", "Moderate sensitivity", "Comfortable in cold"]],
      ["Q13. How does your body usually feel in normal weather?", ["Often feels cold", "Feels normal", "Often feels warm or hot"]]
    ]
  },
  {
    title: "Sleep, Energy & Activity",
    qs: [
      ["Q14. How would you describe your sleep pattern?", ["Light, disturbed, short sleep", "Moderate, balanced sleep", "Deep, long, heavy sleep"]],
      ["Q15. How would you describe your physical activity level?", ["Mostly sedentary", "Moderately active", "Highly active"]],
      ["Q16. How would you describe your daily energy levels?", ["Variable energy, easily fatigued", "Intense energy, driven and focused", "Slow but steady energy"]]
    ]
  },
  {
    title: "Mental & Emotional Traits",
    qs: [
      ["Q17. How would you describe your emotional nature?", ["Anxious, nervous, restless", "Irritable, aggressive, easily frustrated", "Calm, stable, patient"]],
      ["Q18. How would you describe your memory and learning ability?", ["Learns quickly but forgets easily", "Sharp, accurate, logical thinking", "Learns slowly but retains for long"]],
      ["Q19. How do you usually respond to stress or pressure?", ["Worry, anxiety, overthinking", "Anger, impatience, competitiveness", "Calmness, tolerance, withdrawal"]],
      ["Q20. How long can you maintain focus on a task?", ["Short attention span", "Moderate concentration", "Long sustained focus"]]
    ]
  },
  {
    title: "Hair Characteristics and Oral Health",
    qs: [
      ["Q21. How would you describe the thickness and density of your hair?", ["Thin, sparse, fragile", "Medium thickness", "Thick, dense, heavy"]],
      ["Q22. How would you describe the oiliness of your scalp and hair?", ["Very dry scalp", "Normal scalp", "Oily scalp"]],
      ["Q23. How would you describe your teeth strength and health?", ["Weak teeth, sensitive, cavities", "Moderate strength", "Strong, healthy teeth"]],
      ["Q24. How often do you experience dryness in mouth or lips?", ["Very frequent dryness", "Occasional dryness", "Rare dryness"]]
    ]
  },
  {
    title: "Sweat, Body Odor and Bone-Joint Characteristics",
    qs: [
      ["Q25. How much do you sweat during daily activities or mild exercise?", ["Very little sweating", "Moderate sweating", "Excessive sweating"]],
      ["Q26. How would you describe your joints and flexibility?", ["•	Cracking joints, stiffness, dryness", "Moderate flexibility", "Heavy joints, stable, less flexible"]]
    ]
  },
  {
    title: "Hunger & Thirst Tolerance",
    qs: [
      ["Q27. How well can you tolerate skipping meals?", ["Poor tolerance, feel weak quickly", "Moderate tolerance", "Cannot tolerate skipping meals, become irritable"]],
      ["Q28. How frequently do you feel thirsty?", ["Low thirst", "Moderate thirst", "High thirst"]],
      ["Q29. Is your hunger timing regular every day?", ["Very irregular", "Mostly regular", "Very sharp and time-bound"]]
    ]
  }
];

let qid = 1;
sections.forEach(section => {
  let html = `<h3>${section.title}</h3>`;
  section.qs.forEach(q => {
    html += `<p><b>${q[0]}</b></p><div class="option-grid">`;
    q[1].forEach(opt => {
      html += `<div class="option-box"
        onclick="toggleOption(this,'${qid}','${opt}')">${opt}</div>`;
    });
    html += `</div>`;
    qid++;
  });
  questionsDiv.innerHTML += html;
});

function toggleOption(el, qid, val) {
  el.classList.toggle("selected");
  answers[qid] = answers[qid] || [];
  answers[qid].includes(val)
    ? answers[qid] = answers[qid].filter(v => v !== val)
    : answers[qid].push(val);
}

// -------------------------
// SUBMIT
// -------------------------
function submitForm() {

  if (submitBtn.disabled) return;

  if (!capturedBlob) return alert("Please capture a photo first");
  if (Object.keys(answers).length === 0)
    return alert("Please answer at least one question");

  const name = document.getElementById("name").value.trim();
  const age = document.getElementById("age").value.trim();

  if (!name || !age) return alert("Please enter name and age");

  submitBtn.disabled = true;
  submitBtn.innerText = "Submitting...";
  submitBtn.style.opacity = "0.6";

  const fd = new FormData();
  fd.append("image", capturedBlob, "photo.png");
  fd.append("answers", JSON.stringify(answers));
  fd.append("name", name);
  fd.append("age", age);

  fetch("https://prakriti-website.onrender.com/submit", {
    method: "POST",
    body: fd
  })
  .then(res => {
    if (!res.ok) throw new Error("Server error");
    return res.json();
  })
  .then(() => {
    // 🔒 Mark as submitted for THIS SESSION ONLY
    sessionStorage.setItem("prakriti_submitted", "true");

    submitBtn.innerText = "Already Submitted";
    submitBtn.style.cursor = "not-allowed";

    resultCard.style.display = "block";
    resultDiv.innerHTML = "✅ Data submitted successfully. Thank you!";
  })
  .catch(() => {
    submitBtn.disabled = false;
    submitBtn.innerText = "Submit Data";
    alert("Submission failed. Please try again.");
  });
}
