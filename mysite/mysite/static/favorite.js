document.addEventListener("DOMContentLoaded", function () {
    const favList = document.getElementById("favorites-sets-list");
    const allList = document.getElementById("all-sets-list");

    function handleFavoriteClick(event) {
        const button = event.currentTarget;
        const setId = button.dataset.setId;

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
                return;
            }

            button.innerHTML = data.favorited ? "❤️" : "♡";
            document.getElementById("favorite-count").textContent = data.favorite_count;

            const setElement = document.getElementById(`set-${setId}`);

            if (data.favorited) {
                const clone = setElement.cloneNode(true);
                clone.id = `set-${setId}`; // ensure ID is consistent
                favList.appendChild(clone);
                attachFavoriteHandler(clone.querySelector('.favorite-btn'));
            } else {
                const favSet = favList.querySelector(`#set-${setId}`);
                if (favSet) favSet.remove();
            }
        })
        .catch(error => console.error("Error:", error));
    }

    function attachFavoriteHandler(button) {
        button.addEventListener('click', handleFavoriteClick);
    }

    // Attach to initial buttons
    document.querySelectorAll('.favorite-btn').forEach(attachFavoriteHandler);
});

function getCSRFToken() {
    const cookies = document.cookie.split("; ");
    for (let i = 0; i < cookies.length; i++) {
        const [name, value] = cookies[i].split("=");
        if (name === "csrftoken") return value;
    }
    return "";
}
