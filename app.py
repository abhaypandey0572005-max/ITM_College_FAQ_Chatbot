"""
ITM GIDA Gorakhpur - College FAQ Chatbot
-----------------------------------------
Beginner-friendly Flask backend.

How it works:
1. We load all FAQ questions & answers from faqs.json
2. When user sends a message, we compare it against every stored question
   using TF-IDF (Term Frequency-Inverse Document Frequency) + cosine
   similarity. This is smarter than plain text matching because it
   understands which words in a question are most "important" (like
   "fee", "hostel", "admission") versus common filler words.
3. We pick the FAQ with the highest similarity score and return its answer,
   plus a few "related questions" the user might also want to ask.
4. If no question matches well enough (score too low), we return a
   default "I don't understand" message.
"""

from flask import Flask, render_template, request, jsonify
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import json
import os
import random

app = Flask(__name__)

# ---------- Load FAQ data once when server starts ----------
FAQ_PATH = os.path.join(os.path.dirname(__file__), "faqs.json")
with open(FAQ_PATH, "r", encoding="utf-8") as f:
    faqs = json.load(f)

all_questions = [faq["question"] for faq in faqs]

# Build the TF-IDF model once on all stored FAQ questions.
# This turns each question into a vector of word-importance scores.
vectorizer = TfidfVectorizer(stop_words="english")
question_vectors = vectorizer.fit_transform(all_questions)

# Minimum similarity score needed to accept a match (tune this if needed)
SIMILARITY_THRESHOLD = 0.25


def get_best_match(user_message):
    """
    Compares user_message against every FAQ question using TF-IDF +
    cosine similarity. Returns (answer, related_questions_list).
    """
    user_vector = vectorizer.transform([user_message])
    scores = cosine_similarity(user_vector, question_vectors)[0]

    best_index = scores.argmax()
    best_score = scores[best_index]

    if best_score < SIMILARITY_THRESHOLD:
        fallback = ("Sorry, I couldn't understand that. Please try asking "
                    "about admission, fees, courses, hostel, or college timings.")
        related = random.sample(all_questions, min(3, len(all_questions)))
        return fallback, related

    answer = faqs[best_index]["answer"]

    # Find the next-best matching questions (excluding the one we just
    # answered) to suggest as "You might also ask" follow-ups.
    ranked_indices = scores.argsort()[::-1]
    related = []
    for idx in ranked_indices:
        if idx == best_index:
            continue
        related.append(all_questions[idx])
        if len(related) == 3:
            break

    return answer, related


# ---------- Routes ----------

@app.route("/")
def home():
    """Serves the chatbot webpage."""
    return render_template("index.html")


@app.route("/get_response", methods=["POST"])
def get_response():
    """
    Receives the user's message (JSON) from the frontend,
    finds the best matching answer plus related questions,
    and sends them back as JSON.
    """
    data = request.get_json()
    user_message = data.get("message", "")

    if not user_message.strip():
        return jsonify({"answer": "Please type a question.", "related": []})

    answer, related = get_best_match(user_message)
    return jsonify({"answer": answer, "related": related})


if __name__ == "__main__":
    app.run(debug=True)
