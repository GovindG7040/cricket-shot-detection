function previewImage(event) {
    var reader = new FileReader();
    reader.onload = function() {
        var output = document.getElementById('image-preview');
        output.src = reader.result;
        output.style.display = "block";
    };
    reader.readAsDataURL(event.target.files[0]);
}

async function uploadImage() {
    let fileInput = document.getElementById("image-upload");
    let file = fileInput.files[0];

    if (!file) {
        alert("Please select an image first!");
        return;
    }

    let formData = new FormData();
    formData.append("file", file);

    try {
        let response = await fetch("/predict_shot", {  // Ensure FastAPI route is correct
            method: "POST",
            body: formData
        });

        if (!response.ok) {
            throw new Error("Failed to get a valid response from server.");
        }

        let data = await response.json();
        document.getElementById("prediction-result").innerText = "Shot Type: " + data.prediction;
    } catch (error) {
        console.error("Error:", error);
        document.getElementById("prediction-result").innerText = "Error in prediction. Please try again.";
    }
}
