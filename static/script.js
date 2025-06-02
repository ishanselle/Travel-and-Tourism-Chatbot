document.addEventListener('DOMContentLoaded', function() {
    const chatBox = document.getElementById('chat-box');
    const userInput = document.getElementById('user-input');
    const sendButton = document.getElementById('send-button');
    
    // Function to add a message to the chat
    function addMessage(text, isUser) {
      const messageDiv = document.createElement('div');
      messageDiv.classList.add('message');
      messageDiv.classList.add(isUser ? 'user-message' : 'bot-message');
      
      // Convert newlines to <br> tags in bot responses
      const formattedText = text.replace(/\n/g, '<br>');
      messageDiv.innerHTML = formattedText;
      
      // Add timestamp
      const timeDiv = document.createElement('div');
      timeDiv.classList.add('message-time');
      const now = new Date();
      timeDiv.textContent = now.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
      
      messageDiv.appendChild(timeDiv);
      chatBox.appendChild(messageDiv);
      
      // Scroll to bottom
      chatBox.scrollTop = chatBox.scrollHeight;
    }
    
    // Function to send user message
    function sendMessage() {
      const message = userInput.value.trim();
      if (message) {
        addMessage(message, true);
        userInput.value = '';
        
        // Send to server
        fetch('/get', {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
          },
          body: JSON.stringify({message: message}),
        })
        .then(response => response.json())
        .then(data => {
          addMessage(data.reply, false);
        })
        .catch(error => {
          addMessage("Sorry, I'm having trouble connecting to the server.", false);
          console.error('Error:', error);
        });
      }
    }
    
    // Event listeners
    sendButton.addEventListener('click', sendMessage);
    userInput.addEventListener('keypress', function(e) {
      if (e.key === 'Enter') {
        sendMessage();
      }
    });
  });

  