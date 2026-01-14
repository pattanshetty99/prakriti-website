function submitForm() {

  const image = document.getElementById("image").files[0];
  if (!image) {
    alert("Please upload image");
    return;
  }

  let answers = [];

  document.querySelectorAll("input[type=checkbox]:checked")
    .forEach(cb => answers.push(cb.value));

  document.querySelectorAll("input[type=radio]:checked")
    .forEach(rb => answers.push(rb.value));

  const formData = new FormData();
  formData.append("image", image);
  formData.append("answers", JSON.stringify(answers));

  fetch("https://prakriti-website.onrender.com/predict", {
    method: "POST",
    body: formData
  })
  .then(res => res.json())
  .then(data => {
    document.getElementById("result").innerHTML =
      `Prakriti: <b>${data.prakriti}</b><br>
       Confidence: ${data.confidence}`;
  });
}
