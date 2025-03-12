console.log("js loaded");

document.querySelectorAll('.tutorial-btn').forEach(button => {
    button.addEventListener('click', function() {
        console.log('Tutorial button clicked');
        const setId = button.getAttribute('data-set-id');  // Get the data-set-id attribute
        console.log(setId);  // Log the data-set-id value (for debugging)

        // Check if a tutorial is already active, and remove if so
        const existingPopupContainer = document.querySelector('.tutorial-popup-container');
        if (existingPopupContainer) {
            existingPopupContainer.remove();
        }

        // Reset currentPopup index each time a new tutorial is triggered
        currentPopup = 0;

        if (setId === 'create-tutorial') {
            showTutorialPopup(createTutorials);  // Pass the create tutorials
        } else if (setId === 'library-tutorial') {
            showTutorialPopup(libraryTutorials);  // Pass the library tutorials
        } else if (setId === 'home-tutorial') {
            showTutorialPopup(homeTutorials);  // Pass the home tutorials
        }
    });
});

let currentPopup = 0;

// Create tutorial steps
const createTutorials = [
    { 
        message: "This is the Create Flashcard page. Here you can create new flashcards for your study sets.", 
        position: { top: '80px', left: '250%' } // Position can be adjusted here
    },
    { 
        message: "Use this Dropdown to select which set you want to add the flashcard to.", 
        position: { top: '140px', left: '495%' } // Position can be adjusted here
    },
    { 
        message: "This is where you can add the question to the card.", 
        position: { top: '250px', left: '460%' } // Position for this step
    },
    { 
        message: "This is where you can add the answer to the card.", 
        position: { top: '600px', left: '460%' } // Position for this step
    },
    { 
        message: "Clicking 'Create Flashcard' will add the card to the set.", 
        position: { top: '810px', left: '430%' } // Position for this step
    }
];

// Library tutorial steps
const libraryTutorials = [
    { 
        message: "This is the Library page. Here you can view and manage your flashcard sets.", 
        position: { top: '100px', left: '50%' } // Position for this step
    },
    { 
        message: "Click on any flashcard set to view details or start studying.", 
        position: { top: '200px', left: '50%' } // Position for this step
    }
];

// Home tutorial steps
const homeTutorials = [
    { 
        message: "This is the Home page. From here, you can navigate to your library, create new flashcards, and manage your account.", 
        position: { top: '100px', left: '50%' } // Position for this step
    },
    { 
        message: "Click on the settings icon to manage your account and preferences.", 
        position: { top: '200px', left: '50%' } // Position for this step
    }
];

// Function to display the tutorial popups based on the tutorial steps passed
function showTutorialPopup(tutorials) {
    const popupContainer = document.createElement('div');
    popupContainer.classList.add('tutorial-popup-container');
    document.body.appendChild(popupContainer);
    
    // Set inline styles for popup container (removed centering logic)
    popupContainer.style.position = 'fixed';
    popupContainer.style.zIndex = '9999';
    popupContainer.style.width = '300px';
    popupContainer.style.textAlign = 'center';

    showNextPopup(popupContainer, tutorials);
}

// Function to show the next popup in the sequence
function showNextPopup(popupContainer, tutorials) {
    if (currentPopup < tutorials.length) {
        const popup = document.createElement('div');
        popup.classList.add('tutorial-popup');
        popup.innerHTML = `
            <div class="popup-message">
                <p>${tutorials[currentPopup].message}</p>
            </div>
            <button class="next-btn">Next</button>
        `;
        popupContainer.appendChild(popup);

        // Create the triangle and append it to the popup
        const triangle = document.createElement('div');
        triangle.classList.add('triangle');
        popup.appendChild(triangle);

        // Set inline styles for the triangle (pointing to the form, for example)
        triangle.style.position = 'absolute';
        triangle.style.top = '50%'; // Adjust this to position it where you want
        triangle.style.left = '-10px'; // Adjust this to make the triangle appear to the left
        triangle.style.width = '0';
        triangle.style.height = '0';
        triangle.style.borderLeft = '10px solid transparent';
        triangle.style.borderRight = '10px solid transparent';
        triangle.style.borderTop = '10px solid rgba(0, 0, 0, 0.8)'; // Triangle color

        // Set inline styles for the individual popup
        popup.style.backgroundColor = 'rgba(0, 0, 0, 0.8)';
        popup.style.color = 'white';
        popup.style.padding = '20px';
        popup.style.marginBottom = '10px';
        popup.style.borderRadius = '5px';
        popup.style.width = '100%';
        popup.style.boxSizing = 'border-box';
        popup.style.position = 'absolute'; // Changed from relative to absolute for correct positioning

        // Dynamically position each popup based on the tutorial data
        const position = tutorials[currentPopup].position;

        // Use fixed pixel-based values for top and left
        const top = position.top || '100px';  // Default to 100px if not specified
        const left = position.left || '50%';  // Default to 50% horizontally if not specified

        // Apply the calculated styles
        popup.style.top = top;
        popup.style.left = left;

        // Set inline styles for the 'Next' button
        const nextButton = popup.querySelector('.next-btn');
        nextButton.style.backgroundColor = '#84F3DA';
        nextButton.style.color = 'black';
        nextButton.style.border = 'none';
        nextButton.style.padding = '10px';
        nextButton.style.width = '100%';
        nextButton.style.marginTop = '10px';
        nextButton.style.cursor = 'pointer';
        nextButton.style.borderRadius = '5px';

        // Hover effect for the button
        nextButton.addEventListener('mouseover', function() {
            nextButton.style.backgroundColor = '#53af9a';
        });

        nextButton.addEventListener('mouseout', function() {
            nextButton.style.backgroundColor = '#84F3DA';
        });

        // Next button click event
        nextButton.addEventListener('click', function() {
            // Remove both the popup and triangle
            popup.remove();
            currentPopup++;
            if (currentPopup < tutorials.length) {
                showNextPopup(popupContainer, tutorials); // Show next popup
            } else {
                popupContainer.remove(); // Remove the popup container when all tutorials are done
                currentPopup = 0;  // Reset to allow re-triggering of tutorials
            }
        });
    }
}
