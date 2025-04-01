document.getElementById("login-form").addEventListener("submit", async function(event) {
    event.preventDefault();

    let formData = new FormData(this);

    let response = await fetch("/login", {
        method: "POST",
        body: formData
    });

    if (response.redirected) {
        window.location.href = response.url;  // Redirect to dashboard
    } else {
        let data = await response.json();
        alert(data.message);  // Show error if login fails
    }
});
