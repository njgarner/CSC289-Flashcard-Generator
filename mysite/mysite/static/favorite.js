document.addEventListener("DOMContentLoaded", function () {
    document.querySelectorAll('.favorite-btn').forEach(button => {
        button.addEventListener('click', function () {
            let setId = this.dataset.setId;

            fetch(`/toggle_favorite/${setId}/`, {
                method: "POST",
                headers: {
                    "X-CSRFToken": getCSRFToken(),
                    "Content-Type": "application/json"
                },
                credentials: "same-origin"
            })
            .then(response => response.json())
            .then(data => {
                if (data.error) {
                    alert(data.error);
                } else {
                    this.innerHTML = data.favorited ? "❤️" : "♡";
                    document.getElementById("favorite-count").textContent = data.favorite_count;

                    const setElement = document.getElementById(`set-${setId}`);
                    const favList = document.getElementById("favorites-sets-list");
                    const allList = document.getElementById("all-sets-list");

                    // If favorited, clone and append to favorites
                    if (data.favorited) {
                        const clone = setElement.cloneNode(true);
                        favList.appendChild(clone);
                        updateFavoriteButton(clone);
                    } else {
                        // Unfavorited: remove from favorites list
                        const favSet = favList.querySelector(`#set-${setId}`);
                        if (favSet) favSet.remove();
                    }
                }
            })
            .catch(error => console.error("Error:", error));
        });
    });

    function updateFavoriteButton(setElement) {
        const favButton = setElement.querySelector('.favorite-btn');
        favButton.innerHTML = "❤️";
        favButton.addEventListener('click', function () {
            favButton.click(); // trigger the original click handler
        });
    }
});

function getCSRFToken() {
    let cookies = document.cookie.split("; ");
    for (let i = 0; i < cookies.length; i++) {
        let cookie = cookies[i].split("=");
        if (cookie[0] === "csrftoken") return cookie[1];
    }
    return "";
}
