// Grab the elements we need from the page
const chatBox = document.getElementById("chat-box");
const userInput = document.getElementById("user-input");
const sendBtn = document.getElementById("send-btn");

// Adds a message bubble to the chat window
function addMessage(text, sender) {
  const msgDiv = document.createElement("div");
  msgDiv.classList.add("message", sender === "user" ? "user-message" : "bot-message");
  msgDiv.textContent = text;
  chatBox.appendChild(msgDiv);
  chatBox.scrollTop = chatBox.scrollHeight; // auto-scroll to latest message
}

// Sends the user's message to the Flask backend and shows the reply
async function sendMessage() {
  const message = userInput.value.trim();
  if (!message) return;

  addMessage(message, "user");
  userInput.value = "";

  try {
    const response = await fetch("/get_response", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ message: message })
    });

    const data = await response.json();
    addMessage(data.answer, "bot");
  } catch (error) {
    addMessage("Something went wrong. Please try again.", "bot");
  }
}

// Send message on button click
sendBtn.addEventListener("click", sendMessage);

// Send message on Enter key press
userInput.addEventListener("keypress", function (e) {
  if (e.key === "Enter") {
    sendMessage();
  }
});
