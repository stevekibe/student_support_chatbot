document.addEventListener('DOMContentLoaded', () => {
    const chatMessages = document.getElementById('chat-messages');
    const userInput = document.getElementById('user-input');
    const sendButton = document.getElementById('send-button');

    // Function to display messages in the chat interface
    function displayMessage(message, sender) {
        const messageDiv = document.createElement('div');
        messageDiv.classList.add('message', `${sender}-message`);
        // Using innerHTML to allow for links (e.g., from the knowledge base)
        messageDiv.innerHTML = message;
        chatMessages.appendChild(messageDiv);
        // Auto-scroll to the bottom of the chat window
        chatMessages.scrollTop = chatMessages.scrollHeight;
    }

    // Function to send message to backend and get response
    async function sendMessage() {
        const userText = userInput.value.trim();
        if (userText === '') return; // Do nothing if input is empty

        // Display user's message immediately
        displayMessage(userText, 'user');
        userInput.value = ''; // Clear the input field
        userInput.disabled = true; // Disable input while waiting for response
        sendButton.disabled = true; // Disable send button

        try {
            // Make a POST request to your Django backend's chat API endpoint
            // IMPORTANT: Ensure this URL matches your Django server's address and path
            const response = await fetch('http://127.0.0.1:8000/api/chat/', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                // Send the user's message as JSON
                body: JSON.stringify({ message: userText }),
            });

            // Check if the HTTP response was successful
            if (!response.ok) {
                // If not successful, throw an error to be caught by the catch block
                throw new Error(`HTTP error! status: ${response.status}`);
            }

            // Parse the JSON response from the backend
            const data = await response.json();
            // Display the bot's response
            displayMessage(data.response, 'bot');

        } catch (error) {
            // Log the error to the console for debugging
            console.error('Error fetching chat response:', error);
            // Display a user-friendly error message in the chat
            displayMessage("I'm sorry, I'm having trouble connecting right now. Please try again later.", 'bot');
        } finally {
            // Re-enable input and send button regardless of success or failure
            userInput.disabled = false;
            sendButton.disabled = false;
            userInput.focus(); // Put focus back on the input field
        }
    }

    // Event listener for the Send button click
    sendButton.addEventListener('click', sendMessage);

    // Event listener for the Enter key press in the input field
    userInput.addEventListener('keypress', (e) => {
        if (e.key === 'Enter') {
            sendMessage(); // Trigger the send message function
        }
    });
});