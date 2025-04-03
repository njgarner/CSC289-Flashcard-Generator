document.addEventListener("DOMContentLoaded", function () {
    let flashcards = [
        {% for flashcard in flashcards %}
            { question: "{{ flashcard.question|escapejs }}", answer: "{{ flashcard.answer|escapejs }}" },
        {% endfor %}
    ];

    let currentIndex = 0;
    let answeredQuestions = 0; // To track answered questions
    let totalQuestions = flashcards.length;
    let showingQuestion = true; // Track whether the question or answer is displayed
    let cardContent = document.getElementById("card-content");
    let flashcardElement = document.getElementById("flashcard");

    // Function to update the displayed flashcard
    function updateCardContent() {
        if (flashcards.length > 0) {
            cardContent.innerText = showingQuestion ? flashcards[currentIndex].question : flashcards[currentIndex].answer;

            // Highlight the corresponding number box
            updateNumberBox();
        }
    }

    // Function to update the number boxes
    function updateNumberBox() {
        document.querySelectorAll('.number-box').forEach(box => box.classList.remove('selected-box'));
        const selectedBox = document.querySelectorAll('.number-box')[currentIndex];
        selectedBox.classList.add('selected-box');
    }

    // Toggle between question and answer on flashcard click (NOT for quiz mode)
    flashcardElement.addEventListener("click", function () {
        if (document.getElementById("quiz-mode").style.display === 'none') {
            showingQuestion = !showingQuestion;
            updateCardContent();
        }
    });

    // Event listeners for the number boxes
    document.querySelectorAll('.number-box').forEach(box => {
        box.addEventListener('click', function () {
            const index = parseInt(box.getAttribute('data-index'));
            if (index < flashcards.length) {
                currentIndex = index;
                showingQuestion = true; // Reset to show question first
                updateCardContent();
            }
        });
    });

    // Event listeners for the arrow buttons
    document.getElementById("previous-arrow").addEventListener("click", function () {
        currentIndex = (currentIndex - 1 + flashcards.length) % flashcards.length;
        showingQuestion = true; // Reset to show question first
        updateCardContent();
    });

    document.getElementById("next-arrow").addEventListener("click", function () {
        if (currentIndex === flashcards.length - 1) {
            // Switch to quiz mode when reaching the last flashcard
            document.querySelector('.arrow-button').style.display = 'none'; // Hide arrows
            document.getElementById("next-arrow").style.display = 'none'; // Hide next button
            document.getElementById("previous-arrow").style.display = 'none'; // Hide previous button
            document.querySelector('.number-box-container').style.display = 'none';
            document.getElementById("quiz-mode").style.display = 'flex'; // Show quiz mode

            // Display a random question for the quiz
            getNextRandomQuestion();
        } else {
            currentIndex = (currentIndex + 1) % flashcards.length;
            showingQuestion = true; // Reset to show question first
            updateCardContent();
        }
    });

    // Function to get the next random question
    function getNextRandomQuestion() {
        const randomIndex = Math.floor(Math.random() * flashcards.length);
        currentIndex = randomIndex;
        showingQuestion = true; // Reset to show the question
        updateCardContent();
    }

    // Submit the answer in quiz mode
    document.getElementById("submit-answer").addEventListener("click", function () {
        const userAnswer = document.getElementById("answer-input").value.trim().toLowerCase();
        const correctAnswer = flashcards[currentIndex].answer.trim().toLowerCase();

        const resultElement = document.getElementById("result");

        if (userAnswer === correctAnswer) {
            resultElement.innerText = "Correct!";
            resultElement.style.color = "green";
        } else {
            resultElement.innerText = "Incorrect!";
            resultElement.style.color = "red";
        }

        // Show the result on the flashcard in place of the question
        flashcardElement.innerHTML = resultElement.innerText;

        // Disable further input
        document.getElementById("answer-input").disabled = true;
        document.getElementById("submit-answer").disabled = true;

        // Track answered questions
        answeredQuestions++;

        // Check if all questions are answered
        if (answeredQuestions === totalQuestions) {
            document.getElementById("complete").style.display = 'block'; // Show the "Complete" message
            document.getElementById("quiz-mode").style.display = 'none'; // Hide quiz mode
        }
    });

    updateCardContent();  // Initialize the card content
});
