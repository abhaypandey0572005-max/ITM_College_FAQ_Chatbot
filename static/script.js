// Grab the elements we need from the page
const chatBox = document.getElementById("chat-box");
const userInput = document.getElementById("user-input");
const sendBtn = document.getElementById("send-btn");
const suggestions = document.getElementById("suggestions");

// Adds a message bubble to the chat window
function addMessage(text, sender) {
  const msgDiv = document.createElement("div");
  msgDiv.classList.add("message", sender === "user" ? "user-message" : "bot-message");
  msgDiv.textContent = text;
  chatBox.appendChild(msgDiv);
  chatBox.scrollTop = chatBox.scrollHeight; // auto-scroll to latest message
}

// Shows an animated "typing..." bubble while we wait for the bot's answer
function showTypingIndicator() {
  const typingDiv = document.createElement("div");
  typingDiv.classList.add("typing-indicator");
  typingDiv.id = "typing-indicator";
  typingDiv.innerHTML = "<span></span><span></span><span></span>";
  chatBox.appendChild(typingDiv);
  chatBox.scrollTop = chatBox.scrollHeight;
}

function removeTypingIndicator() {
  const typingDiv = document.getElementById("typing-indicator");
  if (typingDiv) typingDiv.remove();
}

// Hides the quick-suggestion chips once the user starts chatting
function hideSuggestions() {
  if (suggestions) suggestions.style.display = "none";
}

// Sends the user's message to the Flask backend and shows the reply
async function sendMessage(prefilledText) {
  const message = (prefilledText !== undefined ? prefilledText : userInput.value).trim();
  if (!message) return;

  hideSuggestions();
  addMessage(message, "user");
  userInput.value = "";

  showTypingIndicator();

  try {
    const response = await fetch("/get_response", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ message: message })
    });

    const data = await response.json();

    // Small delay so the typing indicator feels natural, not instant
    setTimeout(() => {
      removeTypingIndicator();
      addMessage(data.answer, "bot");
    }, 500);
  } catch (error) {
    removeTypingIndicator();
    addMessage("Something went wrong. Please try again.", "bot");
  }
}

// Send message on button click
sendBtn.addEventListener("click", () => sendMessage());

// Send message on Enter key press
userInput.addEventListener("keypress", function (e) {
  if (e.key === "Enter") {
    sendMessage();
  }
});

// Clicking a suggestion chip sends that question automatically
if (suggestions) {
  suggestions.querySelectorAll(".chip").forEach((chip) => {
    chip.addEventListener("click", () => {
      sendMessage(chip.textContent);
    });
  });
}
