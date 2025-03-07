document.addEventListener("DOMContentLoaded", function () {
    document.querySelectorAll('.favorite-btn').forEach(button => {
        button.addEventListener('click', function () {
            let deckId = this.getAttribute('data-deck-id');

            fetch(`/favorite/${deckId}/`, {
                method: 'POST',
                headers: {
                    'X-CSRFToken': document.querySelector('[name=csrfmiddlewaretoken]').value,
                    'Content-Type': 'application/json'
                },
                credentials: 'same-origin'
            })
            .then(response => response.json())
            .then(data => {
                if (data.favorited) {
                    this.innerText = "❤️";  // Update button to filled heart
                } else {
                    this.innerText = "♡";  // Update button to empty heart
                }
                // Refresh the page to reflect the updated state
                location.reload();
            })
            .catch(error => console.error('Error:', error));
        });
    });
});
