document.addEventListener('DOMContentLoaded', () => {
    const chatMessages = document.getElementById('chat-messages');
    const userInput = document.getElementById('user-input');
    const sendButton = document.getElementById('send-button');

    // Helper function to convert Markdown-style links to HTML <a> tags
    function convertMarkdownLinksToHtml(text) {
        
        const regex = /\[([^\]]+)\]\((https?:\/\/[^)]+)\)/g;
       
        return text.replace(regex, '<a href="$2" target="_blank" class="text-blue-600 hover:underline">$1</a>');
    }

    // Function to display messages in the chat interface
    function displayMessage(message, sender) {
        const messageDiv = document.createElement('div');
        messageDiv.classList.add('message', `${sender}-message`);
        
        messageDiv.innerHTML = convertMarkdownLinksToHtml(message);
        chatMessages.appendChild(messageDiv);
      
        chatMessages.scrollTop = chatMessages.scrollHeight;
    }

    // Function to send message to backend and get response
    async function sendMessage() {
        const userText = userInput.value.trim();
        if (userText === '') return; 

        // Display user's message immediately
        displayMessage(userText, 'user');
        userInput.value = ''; 
        userInput.disabled = true; 
        sendButton.disabled = true; 

        try {
            // Make a POST request to your Django backend's chat API endpoint
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
