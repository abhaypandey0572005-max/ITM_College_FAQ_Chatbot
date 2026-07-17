// Grab the elements we need from the page
const chatBox = document.getElementById("chat-box");
const userInput = document.getElementById("user-input");
const sendBtn = document.getElementById("send-btn");
const suggestions = document.getElementById("suggestions");
const themeToggle = document.getElementById("theme-toggle");
const loader = document.getElementById("loader");

const STORAGE_KEY = "itm_chat_history";
const THEME_KEY = "itm_theme";

// ---------- Loader (shown briefly on first page load) ----------
window.addEventListener("load", () => {
  setTimeout(() => loader.classList.add("hidden"), 400);
});

// ---------- Dark mode ----------
function applyTheme(theme) {
  if (theme === "dark") {
    document.body.classList.add("dark-mode");
    themeToggle.textContent = "☀️";
  } else {
    document.body.classList.remove("dark-mode");
    themeToggle.textContent = "🌙";
  }
}

const savedTheme = localStorage.getItem(THEME_KEY) || "light";
applyTheme(savedTheme);

themeToggle.addEventListener("click", () => {
  const isDark = document.body.classList.contains("dark-mode");
  const newTheme = isDark ? "light" : "dark";
  applyTheme(newTheme);
  localStorage.setItem(THEME_KEY, newTheme);
});

// ---------- Chat history persistence ----------
function saveHistory(text, sender) {
  const history = JSON.parse(localStorage.getItem(STORAGE_KEY) || "[]");
  history.push({ text, sender });
  // Keep only the last 30 messages so storage doesn't grow forever
  localStorage.setItem(STORAGE_KEY, JSON.stringify(history.slice(-30)));
}

function restoreHistory() {
  const history = JSON.parse(localStorage.getItem(STORAGE_KEY) || "[]");
  if (history.length === 0) return;

  // We have previous messages, so hide the quick-start suggestion chips
  hideSuggestions();
  history.forEach((item) => renderMessage(item.text, item.sender));
}

// ---------- Rendering messages ----------
function renderMessage(text, sender) {
  const msgDiv = document.createElement("div");
  msgDiv.classList.add("message", sender === "user" ? "user-message" : "bot-message");
  msgDiv.textContent = text;
  chatBox.appendChild(msgDiv);

  // Only bot messages get a feedback (thumbs up/down) row
  if (sender === "bot") {
    const feedback = document.createElement("div");
    feedback.classList.add("feedback");
    feedback.innerHTML = `<button class="thumb-up" title="Helpful">👍</button><button class="thumb-down" title="Not helpful">👎</button>`;

    feedback.querySelector(".thumb-up").addEventListener("click", (e) => {
      e.currentTarget.classList.add("active");
      feedback.querySelector(".thumb-down").classList.remove("active");
    });
    feedback.querySelector(".thumb-down").addEventListener("click", (e) => {
      e.currentTarget.classList.add("active");
      feedback.querySelector(".thumb-up").classList.remove("active");
    });

    chatBox.appendChild(feedback);
  }

  chatBox.scrollTop = chatBox.scrollHeight;
}

// Adds a message bubble AND saves it to history (used for live chat)
function addMessage(text, sender) {
  renderMessage(text, sender);
  saveHistory(text, sender);
}

// ---------- "You might also ask" related question chips ----------
function showRelatedQuestions(relatedList) {
  if (!relatedList || relatedList.length === 0) return;

  const label = document.createElement("div");
  label.classList.add("related-label");
  label.textContent = "You might also ask:";
  chatBox.appendChild(label);

  const box = document.createElement("div");
  box.classList.add("related-box");

  relatedList.forEach((q) => {
    const btn = document.createElement("button");
    btn.classList.add("chip");
    btn.textContent = q;
    btn.addEventListener("click", () => sendMessage(q));
    box.appendChild(btn);
  });

  chatBox.appendChild(box);
  chatBox.scrollTop = chatBox.scrollHeight;
}

// ---------- Typing indicator ----------
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

function hideSuggestions() {
  if (suggestions) suggestions.style.display = "none";
}

// ---------- Sending messages ----------
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

    setTimeout(() => {
      removeTypingIndicator();
      addMessage(data.answer, "bot");
      showRelatedQuestions(data.related);
    }, 500);
  } catch (error) {
    removeTypingIndicator();
    addMessage("Something went wrong. Please try again.", "bot");
  }
}

sendBtn.addEventListener("click", () => sendMessage());

userInput.addEventListener("keypress", function (e) {
  if (e.key === "Enter") {
    sendMessage();
  }
});

if (suggestions) {
  suggestions.querySelectorAll(".chip").forEach((chip) => {
    chip.addEventListener("click", () => {
      sendMessage(chip.textContent);
    });
  });
}

// Restore any previous conversation when the page loads
restoreHistory();
