document.addEventListener("DOMContentLoaded", function() {
    fetch("/api/admin/stats")
    .then(response => response.json())
    .then(data => {
        document.getElementById("total-users").innerText = data.total_users;
        document.getElementById("model-accuracy").innerText = data.model_accuracy + "%";
        document.getElementById("total-predictions").innerText = data.total_predictions;
    })
    .catch(error => console.error("Error fetching stats:", error));
});
