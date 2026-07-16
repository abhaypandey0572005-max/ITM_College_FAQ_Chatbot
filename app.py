"""
ITM GIDA Gorakhpur - College FAQ Chatbot
-----------------------------------------
Beginner-friendly Flask backend.

How it works:
1. We load all FAQ questions & answers from faqs.json
2. When user sends a message, we compare it against every stored question
   using Python's built-in difflib (SequenceMatcher) which gives a
   "similarity score" between 0 and 1.
3. We pick the FAQ with the highest similarity score and return its answer.
4. If no question matches well enough (score too low), we return a
   default "I don't understand" message.
"""

from flask import Flask, render_template, request, jsonify
from difflib import SequenceMatcher
import json
import os
import re

app = Flask(__name__)

# ---------- Load FAQ data once when server starts ----------
FAQ_PATH = os.path.join(os.path.dirname(__file__), "faqs.json")
with open(FAQ_PATH, "r", encoding="utf-8") as f:
    faqs = json.load(f)

# Minimum similarity score needed to accept a match (tune this if needed)
SIMILARITY_THRESHOLD = 0.35

# Common filler words that we ignore while comparing, so they don't
# distract from the important keywords (fee, admission, hostel, etc.)
STOPWORDS = {
    "is", "the", "a", "an", "of", "for", "to", "what", "how", "do",
    "does", "i", "you", "your", "please", "tell", "me", "about",
    "much", "are", "can", "in", "at", "college", "clg"
}


def clean_words(text):
    """Lowercases text, removes punctuation, and drops filler words."""
    text = re.sub(r"[^a-z0-9\s]", "", text.lower())
    words = [w for w in text.split() if w not in STOPWORDS]
    return words


def get_similarity(user_text, faq_text):
    """
    Returns a similarity score (0 to 1) between the user's message and
    a stored FAQ question, combining two signals:
      1. Word overlap (how many important keywords match) - handles
         reordered words and extra/missing words well.
      2. Character similarity (difflib) - catches close spelling/typos.
    """
    user_words = set(clean_words(user_text))
    faq_words = set(clean_words(faq_text))

    if user_words and faq_words:
        overlap = len(user_words & faq_words) / len(user_words | faq_words)
    else:
        overlap = 0

    char_sim = SequenceMatcher(None, user_text.lower(), faq_text.lower()).ratio()

    # Weight word overlap more heavily since it better reflects meaning
    return (0.7 * overlap) + (0.3 * char_sim)


def get_best_answer(user_message):
    """
    Compares user_message against every FAQ question.
    Returns the answer of the best matching FAQ, or a fallback message.
    """
    best_score = 0
    best_answer = None

    for faq in faqs:
        score = get_similarity(user_message, faq["question"])
        if score > best_score:
            best_score = score
            best_answer = faq["answer"]

    if best_score >= SIMILARITY_THRESHOLD:
        return best_answer
    else:
        return ("Sorry, I couldn't understand that. Please try asking about "
                "admission, fees, courses, hostel, or college timings.")


# ---------- Routes ----------

@app.route("/")
def home():
    """Serves the chatbot webpage."""
    return render_template("index.html")


@app.route("/get_response", methods=["POST"])
def get_response():
    """
    Receives the user's message (JSON) from the frontend,
    finds the best matching answer, and sends it back as JSON.
    """
    data = request.get_json()
    user_message = data.get("message", "")

    if not user_message.strip():
        return jsonify({"answer": "Please type a question."})

    answer = get_best_answer(user_message)
    return jsonify({"answer": answer})


if __name__ == "__main__":
    app.run(debug=True)
