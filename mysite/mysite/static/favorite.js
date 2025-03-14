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

                // Refresh the page after updating the favorite status
                setTimeout(() => {
                    location.reload();
                }, 100); // Slight delay to allow UI change before reload
            })
            .catch(error => {
                console.error('Error:', error);  // Log any errors that occur
            });
        });
    });
});
