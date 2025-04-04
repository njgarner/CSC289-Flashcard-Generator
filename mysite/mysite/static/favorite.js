document.addEventListener("DOMContentLoaded", function () {
    // Loop through each favorite button
    document.querySelectorAll('.favorite-btn').forEach(button => {
        button.addEventListener('click', function () {
            let setId = this.dataset.setId; // Get set ID from button's data attribute

            fetch(`/toggle_favorite/${setId}/`, {  // Send AJAX request to backend
                method: "POST",
                headers: {
                    "X-CSRFToken": getCSRFToken(),  // Get CSRF token
                    "Content-Type": "application/json"
                },
                credentials: "same-origin"
            })
            .then(response => response.json()) // Parse JSON from response
            .then(data => {
                if (data.error) {
                    alert(data.error);  // Alert user if max favorites reached
                } else {
                    // Toggle button state
                    this.classList.toggle("favorited", data.favorited);
                    this.innerHTML = data.favorited ? "❤️" : "♡";  // Match original design

                    console.log("Favorite count before update:", document.getElementById("favorite-count").textContent);
                    console.log("New favorite count:", data.favorite_count);

                    // Update the favorite count dynamically
                    document.getElementById("favorite-count").textContent = data.favorite_count;

                    // Update dropdown text dynamically without reloading
                    if (data.last_viewed_set) {
                        let setSelector = document.getElementById("set-selector");
                        if (setSelector) {
                            setSelector.innerText = data.last_viewed_set + " ▼";
                        }
                    }
                }
            })
            .catch(error => console.error("Error:", error));
        });
    });
});

// Function to get CSRF token from cookies (Required for Django POST requests)
function getCSRFToken() {
    let cookies = document.cookie.split("; ");
    for (let i = 0; i < cookies.length; i++) {
        let cookie = cookies[i].split("=");
        if (cookie[0] === "csrftoken") return cookie[1];
    }
    return "";
}
