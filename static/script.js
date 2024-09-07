// Function to update the file name display
function updateFileName() {
  const fileInput = document.getElementById("pdf");
  const fileNameSpan = document.getElementById("fileName");

  if (fileInput.files.length > 0) {
    fileNameSpan.textContent = fileInput.files[0].name;
  } else {
    fileNameSpan.textContent = "No file chosen";
  }
}

// Function to upload the selected PDF file and fetch results
function uploadFile() {
  const formData = new FormData(document.getElementById("uploadForm"));
  const pdfInput = document.getElementById("pdf");
  const courseName = pdfInput.files[0]?.name.split(".pdf")[0] || "";

  fetch("/upload", {
    method: "POST",
    body: formData,
  })
    .then((response) => response.json())
    .then((data) => {
      if (data.success) {
        const resultsDiv = document.getElementById("results");
        resultsDiv.innerHTML = "";

        if (data.deadlines.length > 0) {
          resultsDiv.innerHTML += "<h2>Deadlines</h2>";
          data.deadlines.forEach((deadline) => {
            resultsDiv.innerHTML += `
            <div class="card">
              <h3>Deadline</h3>
              <p>${courseName}: ${deadline}</p>
            </div>
          `;
          });
        }

        if (data.exams.length > 0) {
          resultsDiv.innerHTML += "<h2>Exams</h2>";
          data.exams.forEach((exam) => {
            resultsDiv.innerHTML += `
            <div class="card">
              <h3>Exam</h3>
              <p>${courseName}: ${exam}</p>
            </div>
          `;
          });
        }
      } else {
        alert(data.message || "An error occurred.");
      }
    })
    .catch((error) => console.error("Error:", error));
}
