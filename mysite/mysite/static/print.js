document.querySelectorAll('.print-button').forEach(button => {
    button.addEventListener('click', function() {
        // Get the set ID from the button's data attribute
        const setId = button.getAttribute('data-set-id');
        console.log('Printing flashcards for set ID:', setId);

        // Create the hover box
        let hoverBox = document.createElement('div');
        hoverBox.classList.add('hover-box'); 

        // Style the hover box
        hoverBox.style.backgroundColor = 'rgb(236, 236, 236)';
        hoverBox.style.border = '1px solid rgb(167, 167, 167)';
        hoverBox.style.width = '500px';
        hoverBox.style.height = '400px';
        hoverBox.style.textAlign = 'center';
        hoverBox.style.position = 'fixed';
        hoverBox.style.top = '50%';
        hoverBox.style.left = '50%';
        hoverBox.style.transform = 'translate(-50%, -50%)';
        hoverBox.style.zIndex = '9999';

        // Add text inside the hover box
        hoverBox.innerHTML = "<p>Select print options:</p>";

        // Exit button for closing the hover box
        let exitButton = document.createElement('button');
        exitButton.innerHTML = "X";
        exitButton.style.backgroundColor = '#84F3DA';
        exitButton.style.border = '1px solid rgb(3, 92, 71)';
        exitButton.style.width = '30px';
        exitButton.style.height = '30px';
        exitButton.style.position = 'absolute';
        exitButton.style.top = '10px';
        exitButton.style.right = '10px'; 
        exitButton.style.zIndex = '10000';
        exitButton.addEventListener('click', function() {
            hoverBox.remove();
        });

        // Append the exit button to the hover box
        hoverBox.appendChild(exitButton);

        // Create a container for the print options side by side
        let optionsContainer = document.createElement('div');
        optionsContainer.style.display = 'flex';
        optionsContainer.style.justifyContent = 'space-between';
        optionsContainer.style.padding = '20px';

        // Create the first print option (With answers)
        let option1 = document.createElement('div');
        option1.style.textAlign = 'center';
        option1.style.width = '45%';
        option1.style.display = 'flex';
        option1.style.flexDirection = 'column';
        option1.style.alignItems = 'center';
        option1.style.justifyContent = 'center';

        // Add label above the image for the first option
        let label1 = document.createElement('label');
        label1.innerHTML = 'Print Study Guide (With answers)';
        label1.style.marginBottom = '10px';  // Add space between label and image
        option1.appendChild(label1);

        // Add image for the first option
        let img1 = document.createElement('img');
        img1.src = static_img1;  // Replace with your image path
        img1.style.width = '100px';  // Set the width of the image
        img1.style.height = '150px';  // Set the height of the image
        img1.style.marginBottom = '10px';  // Space between image and radio button
        option1.appendChild(img1);

        // Add radio button below the image for the first option
        let radio1 = document.createElement('input');
        radio1.type = 'radio';
        radio1.name = 'print_option';
        radio1.value = 'print_answer_key';
        radio1.checked = true;
        option1.appendChild(radio1);

        // Append the first option to the options container
        optionsContainer.appendChild(option1);

        // Create the second print option (Without answers)
        let option2 = document.createElement('div');
        option2.style.textAlign = 'center';
        option2.style.width = '45%';
        option2.style.display = 'flex';
        option2.style.flexDirection = 'column';
        option2.style.alignItems = 'center';
        option2.style.justifyContent = 'center';

        // Add label above the image for the second option
        let label2 = document.createElement('label');
        label2.innerHTML = 'Print Study Guide (No answers)';
        label2.style.marginBottom = '10px';  // Add space between label and image
        option2.appendChild(label2);

        // Add image for the second option
        let img2 = document.createElement('img');
        img2.src = static_img2;  // Replace with your image path
        img2.style.width = '100px';  // Set the width of the image
        img2.style.height = '150px';  // Set the height of the image
        img2.style.marginBottom = '10px';  // Space between image and radio button
        option2.appendChild(img2);

        // Add radio button below the image for the second option
        let radio2 = document.createElement('input');
        radio2.type = 'radio';
        radio2.name = 'print_option';
        radio2.value = 'print_blank';
        option2.appendChild(radio2);

        // Append the second option to the options container
        optionsContainer.appendChild(option2);

        // Append the options container to the hover box
        hoverBox.appendChild(optionsContainer);

        // Add a button for printing the page
        let printButton = document.createElement('button');
        printButton.innerHTML = "Print";
        printButton.style.backgroundColor = '#84F3DA';
        printButton.style.border = '1px solid rgb(3, 92, 71)';
        printButton.style.width = '100px';
        printButton.style.height = '30px';
        printButton.style.position = 'absolute';  
        printButton.style.bottom = '10px';  // Adjust this to move the button upwards
        printButton.style.left = '50%';  
        printButton.style.transform = 'translateX(-50%)';  // Centers the button horizontally
        printButton.style.zIndex = '10000';  // Ensure the button is on top

        // Attach the event listener for printing
        printButton.addEventListener('click', function() {
            // Get the selected print option (with or without answers)
            const printWithAnswers = radio1.checked;

            // Fetch the flashcard set details via AJAX using the dynamic setId
            fetch(`/flashcards/${setId}/details/`)  // Dynamic URL based on clicked button's setId
                .then(response => response.json())
                .then(data => {
                    // Conditionally include or exclude answers based on the radio button
                    const content = data.flashcards.map(flashcard => {
                        if (printWithAnswers) {
                            // Include both question and answer
                            return `<li>
                                        <strong>Question:</strong> ${flashcard.question}<br>
                                        <strong>Answer:</strong> ${flashcard.answer}
                                    </li>`;
                        } else {
                            // Only include question, no answer
                            return `<li>
                                        <strong>Question:</strong> ${flashcard.question}
                                    </li>`;
                        }
                    }).join('');

                    // Open a new window for printing
                    let printWindow = window.open('', '', 'height=600,width=800');

                    // Write the content into the new window
                    printWindow.document.write('<html><head><title>Print Flashcards</title>');
                    printWindow.document.write('<style>body { font-family: Arial, sans-serif; }</style>');
                    printWindow.document.write('</head><body>');
                    printWindow.document.write('<h1>' + data.title + '</h1>');  // Set title of the deck
                    printWindow.document.write('<ul>' + content + '</ul>');  // Insert flashcards
                    printWindow.document.write('</body></html>');
                    printWindow.document.close();  // Close the document for rendering

                    printWindow.print();  // Trigger the print dialog
                })
                .catch(error => console.error('Error fetching deck details:', error));
        });

        // Append the print button to the hover box
        hoverBox.appendChild(printButton);

        // Append the hover box to the body
        document.body.appendChild(hoverBox);
    });
});
