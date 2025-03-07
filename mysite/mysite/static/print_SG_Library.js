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

        // Radio button for selecting print options (with images)
        let radio1 = document.createElement('input');
        radio1.type = 'radio';
        radio1.name = 'print_option';
        radio1.value = 'print_answer_key';
        radio1.checked = true;
        radio1.style.margin = '10px';
        radio1.style.width = '20px';
        radio1.style.height = '20px';
        radio1.style.position = 'absolute';  
        radio1.style.top = '40%';
        radio1.style.left = '20px'; 
        hoverBox.appendChild(radio1);

        let label1 = document.createElement('label');
        label1.innerHTML = 'Print Study Guide (With answers)';
        label1.style.position = 'absolute';
        label1.style.top = '40%';
        label1.style.left = '55px'; 
        hoverBox.appendChild(label1);

        // Add image next to the first radio button
        let img1 = document.createElement('img');
        img1.src = static_img1 // Replace with your image path--SG_Answers.jpeg
        img1.style.position = 'absolute';
        img1.style.top = '40%';
        img1.style.left = '160px';  // Adjust as necessary to position next to the radio button
        img1.style.width = '50px';  // Set the size of the image
        img1.style.height = '50px';  // Adjust the height of the image
        hoverBox.appendChild(img1);

        let radio2 = document.createElement('input');
        radio2.type = 'radio';
        radio2.name = 'print_option';
        radio2.value = 'print_blank';
        radio2.style.margin = '10px';
        radio2.style.width = '20px';
        radio2.style.height = '20px';
        radio2.style.position = 'absolute';
        radio2.style.top = '50%';
        radio2.style.left = '20px'; 
        hoverBox.appendChild(radio2);

        let label2 = document.createElement('label');
        label2.innerHTML = 'Print Study Guide (No answers)';
        label2.style.position = 'absolute';
        label2.style.top = '50%';
        label2.style.left = '55px'; 
        hoverBox.appendChild(label2);

        // Add image next to the second radio button
        let img2 = document.createElement('img');
        img2.src = static_img2  // Replace with your image path--SG.jpeg
        img2.style.position = 'absolute';
        img2.style.top = '50%';
        img2.style.left = '160px';  // Adjust as necessary to position next to the radio button
        img2.style.width = '50px';  // Set the size of the image
        img2.style.height = '50px';  // Adjust the height of the image
        hoverBox.appendChild(img2);

        // Add a button for printing the page
        let printButton = document.createElement('button');
        printButton.innerHTML = "Print";
        printButton.style.backgroundColor = '#84F3DA';
        printButton.style.border = '1px solid rgb(3, 92, 71)';
        printButton.style.width = '100px';
        printButton.style.height = '30px';
        printButton.style.position = 'absolute';  
        printButton.style.bottom = '10px';
        printButton.style.left = '50%';  
        printButton.style.transform = 'translateX(-50%)';  
        printButton.style.zIndex = '10000'; 
        
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
