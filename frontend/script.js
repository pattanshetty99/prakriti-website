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
      document.getElementById("captureBtn").style.display = "inline";
    })
    .catch(err => alert("Camera access denied"));
}

/* Capture Photo */
function capture() {
  const ctx = canvas.getContext("2d");
  ctx.drawImage(video, 0, 0, canvas.width, canvas.height);

  canvas.toBlob(blob => {
    capturedBlob = blob;

    // Show preview
    const imgURL = URL.createObjectURL(blob);
    photoPreview.src = imgURL;
  });

  // Stop camera
  stream.getTracks().forEach(track => track.stop());
  video.srcObject = null;
  document.getElementById("captureBtn").style.display = "none";

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
},
{
title:"Section C: Thirst & Sweating",
qs:[
["Q7. How often do you feel thirsty?",["Low","Very frequent","Moderate"]],
["Q8. How much do you sweat?",["Very little","Excessive","Moderate"]]
]
},
{
title:"Section D: Temperature & Climate",
qs:[
["Q9. Which climate makes you uncomfortable?",["Cold","Hot","Humid"]],
["Q10. Body temperature to touch?",["Cold","Warm","Normal"]]
]
},
{
title:"Section E: Sleep & Energy",
qs:[
["Q11. Sleep quality?",["Light","Moderate","Deep"]],
["Q12. Sleep duration?",["Short","Normal","Long"]],
["Q13. Energy level?",["Low","High","Steady"]]
]
},
{
title:"Section F: Physical Activity",
qs:[
["Q14. Activity level?",["Restless","Moderate","Sedentary"]],
["Q15. Physical endurance?",["Low","Moderate","High"]]
]
},
{
title:"Section G: Psychological Traits",
qs:[
["Q16. Emotional reaction?",["Anxiety","Anger","Calm"]],
["Q17. Stress response?",["Worry","Anger","Silent"]],
["Q18. Decision making?",["Quick changing","Confident","Slow firm"]],
["Q19. Memory?",["Forgetful","Sharp","Long memory"]]
]
},
{
title:"Section H: Food Habits",
qs:[
["Q20. Preferred taste?",["Sweet/Sour","Spicy/Salty","Bitter"]],
["Q21. Eating speed?",["Very fast","Fast","Slow"]],
["Q22. Skipping meal effect?",["Weak","Angry","No effect"]]
]
},
{
title:"Section I: Skin & Hair",
qs:[
["Q23. Skin type?",["Dry","Oily","Smooth"]],
["Q24. Hair type?",["Dry","Thin","Thick"]],
["Q25. Nails?",["Brittle","Soft","Strong"]]
]
},
{
title:"Section J: Self Assessment",
qs:[
["Q26. Overall nature?",["Light","Intense","Stable"]]
]
},
{
title:"Section K–T: Advanced Traits",
qs:[
["Q27. Speaking style?",["Fast","Sharp","Slow"]],
["Q28. Voice quality?",["Low","Loud","Deep"]],
["Q29. Body odor?",["Mild","Strong","Sweet"]],
["Q30. Sweat smell?",["None","Strong","Mild"]],
["Q31. Sun reaction?",["Dry","Burns","Normal"]],
["Q32. Skin irritation?",["Occasional","Frequent","Rare"]],
["Q33. Hunger regularity?",["Irregular","Very regular","Mild"]],
["Q34. Hunger time?",["Varies","Noon","Morning/Evening"]],
["Q35. Emotion duration?",["Fast change","Intense","Slow change"]],
["Q36. Forgiveness?",["Fast forgive","Slow forgive","Forget quickly"]],
["Q37. Work style?",["Multitask","Focused","Routine"]],
["Q38. Deadline handling?",["Nervous","Competitive","Calm"]],
["Q39. Muscle strength?",["Weak flexible","Strong firm","Strong slow"]],
["Q40. Recovery speed?",["Slow","Fast","Moderate"]],
["Q41. Affected season?",["Autumn","Summer","Rainy"]],
["Q42. Wind reaction?",["Uncomfortable","Slight","Normal"]],
["Q43. Cravings?",["Frequent","Strong","Rare"]],
["Q44. Food craving?",["Warm","Cold/Spicy","Sweet"]],
["Q45. Attachment?",["Detached","Moderate","Strong"]],
["Q46. Reaction to change?",["Unstable","Effort","Resist"]]
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
