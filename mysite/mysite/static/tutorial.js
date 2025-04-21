console.log("✅ favorite.js loaded");

// Button listener to trigger tutorial
document.addEventListener("DOMContentLoaded", function () {
    document.querySelectorAll('.tutorial-btn').forEach(button => {
        button.addEventListener('click', function () {
            console.log("📌 Tutorial button clicked");

            const setId = button.getAttribute('data-set-id');
            console.log("👉 Set ID:", setId);

            // Remove existing popup
            const existingPopup = document.querySelector('.tutorial-popup-container');
            if (existingPopup) existingPopup.remove();

            currentPopup = 0;

            if (setId === 'study-tutorial') {
                showTutorialPopup(studyTutorials);
            } else if (setId === 'world-tutorial') {
                showTutorialPopup(worldTutorials);
            } else if (setId === 'library-tutorial') {
                showTutorialPopup(libraryTutorials);
            } else if (setId === 'classroom-student-tutorial') {
                showTutorialPopup(studentTutorials);
            } else if (setId === 'classroom-teacher-tutorial') {
                showTutorialPopup(teacherTutorials);
            } else if (setId === 'color-tutorial') {
                showTutorialPopup(colorTutorials);
            } else if (setId === 'createset-tutorial') {
                showTutorialPopup(createsetTutorials);
            }
        });
    });
});

let currentPopup = 0;

// Tutorial Steps
const studyTutorials = [
    {
        message: "This is the Study Time page. This is where you can study and practice your flashcards.",
        target: "h1.page-title",
        position: "bottom"
    },
    {
        message: "This is where your card will be displayed.",
        target: "#flashcard",
        position: "top"
    },
    {
        message: "Select which set you would like to study with this dropdown!",
        target: "#set-selector",
        position: "right"
    }, 
    {
        message: "This 'Shuffle' button will take you to a random card in the set.",
        target: "#rand-button",
        position: "right"
    },
    {
        message: "This 'previous' button will take you to the previous card in the set.",
        target: "#previous",
        position: "top"
    },
    {
        message: "This 'next' button will take you to the next card in the set.",
        target: "#next",
        position: "top"
    },
    {
        message: "This 'Learn' button will test you on the cards once you have gone through them.",
        target: "#learn-button",
        position: "right"
    },
    {
        message: "This 'Flip' button will flip the card to show the question or answer.",
        target: "#flip-button",
        position: "right"
    },
    {
        message: "This 'Review' button will flip the card to show the question or answer.",
        target: "#review-button",
        position: "right"
    }
];
const worldTutorials = [
    {
        message: "This is the World Sets page. Here you can view sets shared by other users.",
        target: "h2.page-title",
        position: "bottom"
    },
    {
        message: "The search bar can be used to search for sets!",
        target: ".clear-btn",
        position: "right"
    },
    {
        message: "The drop down allows you to filter your search by; title, description, or category.",
        target: ".clear-btn",
        position: "right"
    },
    {
        message: "Hit the clear button to clear your search.",
        target: ".clear-btn",
        position: "right"
    },
    {
        message: "You can select to display the sets all together or seperated by category.",
        target: "#cat-btn",
        position: "right"
    }
];
const libraryTutorials = [
    {
        message: "This is the Library page. Here you can create and view your sets.",
        target: "h2.page-title",
        position: "bottom"
    },
    {
        message: "The search bar can be used to search for sets in your library.",
        target: ".clear-btn",
        position: "right"
    },
    {
        message: "The drop down allows you to filter your search by; title, description, or category.",
        target: ".clear-btn",
        position: "right"
    },
    {
        message: "Hit the clear button to clear your search.",
        target: ".clear-btn",
        position: "right"
    },
    {
        message: "Sets can be created by clicking this button.",
        target: ".add-box",
        position: "right"
    },
    {
        message: "You can display all the sets, the favorited sets, or display by category.",
        target: "#cat-btn",
        position: "right"
    },
    {
        message: "Sets assigned by a teacher can also be displayed.",
        target: "#cat-btn",
        position: "right"
    }
];
const studentTutorials = [
    {
        message: "This is the Classroom page. Here you can manage the classrooms you are a part of.",
        target: "h1.page-title",
        position: "bottom"
    },
    {
        message: "Enter the classroom code provided by the teacher to join the class.",
        target: "#join-btn",
        position: "right"
    }
];
const teacherTutorials = [
    {
        message: "This is the Classrooms page. Here you can create classrooms to assign sets to your students.",
        target: "h1.page-title",
        position: "bottom"
    },
    {
        message: "The search bar can be used to search for classes.",
        target: ".clear-btn",
        position: "right"
    },
    {
        message: "The drop down allows you to filter your search by name and description.",
        target: ".clear-btn",
        position: "right"
    },
    {
        message: "Hit the clear button to clear your search.",
        target: ".clear-btn",
        position: "right"
    },
    {
        message: "Classrooms can be created by clicking this button.",
        target: ".add-box",
        position: "right"
    }
];
const colorTutorials = [
    {
        message: "This is the customization page. Here you change the colors of your cards and add buttons.",
        target: "h2",
        position: "bottom"
    },
    {
        message: "Each element has 2 default colors--The first 2 boxes.",
        target: "#clearColorsBtn",
        position: "right"
    },
    {
        message: "You can use the third box under each element to select a color from a color picker.",
        target: "#clearColorsBtn",
        position: "right"
    },
    {
        message: "Hitting the 'clear' button resets the colors to default.",
        target: "#clearColorsBtn",
        position: "right"
    }
];
const createsetTutorials = [
    {
        message: "This is the Create a Set page. This page allows you to create a set with your desired specifications.",
        target: "h2",
        position: "bottom"
    },
    {
        message: "Type you set name here.",
        target: "#title",
        position: "right"
    },
    {
        message: "Type a category here. When more sets are added to your library they can be grouped by categories.",
        target: "#category",
        position: "right"
    },
    {
        message: "Add a description for your set to explain what it is.",
        target: "#description",
        position: "right"
    },
    {
        message: "The visibility buttons decide whether the set will be visible on the World Sets page or not.",
        target: ".radio-group",
        position: "right"
    },
    {
        message: "Make sure to save your set when your done!.",
        target: ".button",
        position: "right"
    },
];



// Inject the CSS styles directly into the document's head
function injectCSS() {
    const style = document.createElement('style');
    style.innerHTML = `
        /* Popup styles */
        .tutorial-popup-container {
            position: absolute;
            z-index: 9999;
            pointer-events: none;
        }

        .tutorial-popup {
            position: fixed;
            background-color: rgba(0, 0, 0, 0.85);
            color: white;
            padding: 15px;
            border-radius: 5px;
            width: 280px;
            z-index: 10000;
            box-shadow: 0 0 10px rgba(0, 0, 0, 0.5);
            pointer-events: auto;
        }

        .popup-message {
            margin-bottom: 10px;
        }

        .next-btn {
            display: block;
            margin-left: auto;
            margin-right: auto;
            margin-top: 10px;
            padding: 8px 12px;
            background-color: #84F3DA;
            border: none;
            color: #000;
            border-radius: 4px;
            cursor: pointer;
        }

        /* Triangle pointer styles */
        .popup-triangle {
            position: absolute;
            width: 0;
            height: 0;
            border-left: 6px solid transparent;
            border-right: 6px solid transparent;
            border-top: 6px solid rgba(0, 0, 0, 0.85); /* Change color as needed */
        }
    `;
    document.head.appendChild(style);
}

// Call injectCSS to add the styles
injectCSS();

function showTutorialPopup(tutorials) {
    const container = document.createElement('div');
    container.className = 'tutorial-popup-container';
    document.body.appendChild(container);

    container.style.pointerEvents = 'none'; // makes popups non-interactive except for button
    showNextPopup(container, tutorials);
}

function showNextPopup(container, tutorials) {
    const step = tutorials[currentPopup];
    const targetElement = document.querySelector(step.target);

    if (!targetElement) {
        console.warn("⚠️ Target element not found:", step.target);
        currentPopup++;
        if (currentPopup < tutorials.length) {
            showNextPopup(container, tutorials);
        } else {
            container.remove();
            currentPopup = 0;
        }
        return;
    }

    const rect = targetElement.getBoundingClientRect();
    console.log(`📐 Positioning popup near: ${step.target}`, rect);

    const popup = document.createElement('div');
    popup.className = 'tutorial-popup';
    popup.innerHTML = `
        <div class="popup-message">
            <p>${step.message}</p>
        </div>
        <button class="next-btn">${currentPopup === tutorials.length - 1 ? 'Close' : 'Next'}</button>
    `;

    // Style the popup
    popup.style.position = 'fixed';
    popup.style.zIndex = '10000';

    // Add the triangle pointer
    const triangle = document.createElement('div');
    triangle.className = 'popup-triangle';
    popup.appendChild(triangle);

    // Determine the position and adjust the triangle's CSS accordingly
    if (step.position === 'top') {
        triangle.style.top = '100%'; // Place the triangle below the box
        triangle.style.left = '50%';
        triangle.style.transform = 'translateX(-50%) rotate(0deg)'; // Point the triangle downwards
    } else if (step.position === 'bottom') {
        triangle.style.bottom = '100%'; // Place the triangle above the box
        triangle.style.left = '50%';
        triangle.style.transform = 'translateX(-50%) rotate(180deg)'; // Point the triangle upwards
    } else if (step.position === 'left') {
        triangle.style.left = '100%'; // Place the triangle to the left of the box
        triangle.style.top = '50%';
        triangle.style.transform = 'translateY(-50%) rotate(-90deg)'; // Point the triangle to the right
    } else if (step.position === 'right') {
        triangle.style.right = '100%'; // Place the triangle to the right of the box
        triangle.style.top = '50%';
        triangle.style.transform = 'translateY(-50%) rotate(90deg)'; // Point the triangle to the left
    }

    // Style and add button
    const nextButton = popup.querySelector('.next-btn');
    nextButton.addEventListener('click', function () {
        popup.remove();
        currentPopup++;
        if (currentPopup < tutorials.length) {
            showNextPopup(container, tutorials);
        } else {
            container.remove();
            currentPopup = 0;
        }
    });

    container.appendChild(popup);
    requestAnimationFrame(() => {
        applyPositioning(popup, rect, step.position);
    });

    function applyPositioning(popup, rect, position) {
        const padding = 10;
        const scrollY = window.scrollY;
        const scrollX = window.scrollX;
        const popupWidth = popup.offsetWidth;
        const popupHeight = popup.offsetHeight;
        const viewportWidth = window.innerWidth;
        const viewportHeight = window.innerHeight;
    
        // Try to flip position if not enough space
        const fitsAbove = rect.top >= popupHeight + padding;
        const fitsBelow = viewportHeight - rect.bottom >= popupHeight + padding;
        const fitsLeft = rect.left >= popupWidth + padding;
        const fitsRight = viewportWidth - rect.right >= popupWidth + padding;
    
        if (position === 'top' && !fitsAbove && fitsBelow) {
            position = 'bottom';
        } else if (position === 'bottom' && !fitsBelow && fitsAbove) {
            position = 'top';
        } else if (position === 'left' && !fitsLeft && fitsRight) {
            position = 'right';
        } else if (position === 'right' && !fitsRight && fitsLeft) {
            position = 'left';
        }
    
        let top, left;
    
        if (position === 'top') {
            top = rect.top + scrollY - popupHeight - padding;
            left = rect.left + rect.width / 2 - popupWidth / 2 + scrollX;
        } else if (position === 'bottom') {
            top = rect.bottom + scrollY + padding;
            left = rect.left + rect.width / 2 - popupWidth / 2 + scrollX;
        } else if (position === 'left') {
            top = rect.top + scrollY + rect.height / 2 - popupHeight / 2;
            left = rect.left - popupWidth - padding + scrollX;
        } else if (position === 'right') {
            top = rect.top + scrollY + rect.height / 2 - popupHeight / 2;
            left = rect.right + padding + scrollX;
        }
    
        // Clamp position so it stays inside viewport
        top = Math.max(scrollY + padding, Math.min(top, scrollY + viewportHeight - popupHeight - padding));
        left = Math.max(scrollX + padding, Math.min(left, scrollX + viewportWidth - popupWidth - padding));
    
        popup.style.top = `${top}px`;
        popup.style.left = `${left}px`;
    
        // Optional: scroll the popup into view if it's still near bottom
        const popupRect = popup.getBoundingClientRect();
        const isClippedBottom = popupRect.bottom > viewportHeight;
        if (isClippedBottom) {
            window.scrollBy({ top: popupRect.bottom - viewportHeight + 20, behavior: 'smooth' });
        }
    }
}
