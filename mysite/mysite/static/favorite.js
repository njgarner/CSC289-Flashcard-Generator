document.addEventListener("DOMContentLoaded", function () {

    // Loop through each favorite button
    document.querySelectorAll('.favorite-btn').forEach(button => {
        button.addEventListener('click', function () {

            // Get the set ID from the button's data attribute
            let setId = this.getAttribute('data-set-id');

            // Send a POST request to the backend to toggle the favorite status
            fetch(`/favorite/${setId}/`, {
                method: 'POST',
                headers: {
                    'X-CSRFToken': document.querySelector('[name=csrfmiddlewaretoken]').value,
                    'Content-Type': 'application/json'
                },
                credentials: 'same-origin'
            })
            .then(response => response.json())  // Parse JSON from response
            .then(data => {
                // Check if the set was favorited
                if (data.favorited) {
                    this.innerText = "❤️";  // Change button to filled heart
                } else {
                    this.innerText = "♡";  // Change button to empty heart
                }

                 // Dynamically update the dropdown text without reloading the page
                // Get the last viewed set from the session (update with the correct set)
                let lastViewedSet = data.last_viewed_set; // Ensure backend sends the updated last viewed set title
                if (lastViewedSet) {
                    document.getElementById("set-selector").innerText = lastViewedSet + " ▼";
                }
            })
            .catch(error => {
                console.error('Error:', error);  // Log any errors that occur
            });
        });
    });
});