"""
ITM GIDA Gorakhpur - College FAQ Chatbot
-----------------------------------------
Beginner-friendly Flask backend.

How it works:
1. We load all FAQ questions & answers from faqs.json (each FAQ has an
   English question/answer AND a Hindi question_hi/answer_hi).
2. When user sends a message, we compare it against every stored question
   IN THE SELECTED LANGUAGE using TF-IDF (Term Frequency-Inverse Document
   Frequency) + cosine similarity. This is smarter than plain text matching
   because it understands which words in a question are most "important"
   (like "fee", "hostel", "admission") versus common filler words.
3. We pick the FAQ with the highest similarity score and return its answer,
   plus a few "related questions" the user might also want to ask -- all
   in the language the user selected.
4. If no question matches well enough (score too low), we return a
   default "I don't understand" message in that language.
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

# English questions (fall back to English if a Hindi field is somehow missing)
all_questions_en = [faq["question"] for faq in faqs]
# Hindi questions
all_questions_hi = [faq.get("question_hi", faq["question"]) for faq in faqs]

# Build a separate TF-IDF model for each language, since English stop-words
# ("is", "the", "what") don't apply to Hindi text.
vectorizer_en = TfidfVectorizer(stop_words="english")
question_vectors_en = vectorizer_en.fit_transform(all_questions_en)

vectorizer_hi = TfidfVectorizer()
question_vectors_hi = vectorizer_hi.fit_transform(all_questions_hi)

# Minimum similarity score needed to accept a match (tune this if needed)
SIMILARITY_THRESHOLD = 0.25

FALLBACK_MESSAGES = {
    "en": ("Sorry, I couldn't understand that. Please try asking "
           "about admission, fees, courses, hostel, or college timings."),
    "hi": ("क्षमा करें, मैं समझ नहीं पाया। कृपया दाखिला, फीस, कोर्स, "
           "हॉस्टल, या कॉलेज के समय के बारे में पूछें।"),
}


def get_best_match(user_message, lang="en"):
    """
    Compares user_message against every FAQ question (in the given
    language) using TF-IDF + cosine similarity. Returns
    (answer, related_questions_list) in that same language.
    """
    if lang == "hi":
        vectorizer = vectorizer_hi
        question_vectors = question_vectors_hi
        all_questions = all_questions_hi
        answer_key = "answer_hi"
    else:
        vectorizer = vectorizer_en
        question_vectors = question_vectors_en
        all_questions = all_questions_en
        answer_key = "answer"

    user_vector = vectorizer.transform([user_message])
    scores = cosine_similarity(user_vector, question_vectors)[0]

    best_index = scores.argmax()
    best_score = scores[best_index]

    if best_score < SIMILARITY_THRESHOLD:
        fallback = FALLBACK_MESSAGES.get(lang, FALLBACK_MESSAGES["en"])
        related = random.sample(all_questions, min(3, len(all_questions)))
        return fallback, related

    answer = faqs[best_index].get(answer_key, faqs[best_index]["answer"])

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
    Receives the user's message and selected language (JSON) from the
    frontend, finds the best matching answer plus related questions in
    that language, and sends them back as JSON.
    """
    data = request.get_json()
    user_message = data.get("message", "")
    lang = data.get("lang", "en")
    if lang not in ("en", "hi"):
        lang = "en"

    if not user_message.strip():
        empty_prompt = "Please type a question." if lang == "en" else "कृपया अपना प्रश्न लिखें।"
        return jsonify({"answer": empty_prompt, "related": []})

    answer, related = get_best_match(user_message, lang)
    return jsonify({"answer": answer, "related": related})


if __name__ == "__main__":
    app.run(debug=True)
