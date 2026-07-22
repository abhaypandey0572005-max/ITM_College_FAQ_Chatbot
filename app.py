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


FALLBACK_MESSAGES = {
    "en": ("Sorry, I couldn't understand that. Please try asking about "
           "admission, fees, courses, hostel, or college timings."),
    "hi": ("माफ करें, मैं इसे समझ नहीं पाया। कृपया एडमिशन, फीस, कोर्स, "
           "हॉस्टल, या कॉलेज टाइमिंग के बारे में पूछने की कोशिश करें।")
}

# ---------- Greeting detection ----------
# If someone just says "hi", "hello", "good morning", etc., we don't want
# to run that through FAQ matching (it would either fail or accidentally
# match some unrelated question). Instead we recognize these common
# greeting words/phrases and reply with a friendly hello of our own,
# nudging the person toward asking their real question next.
GREETING_WORDS = {
    "hi", "hii", "hiii", "hello", "helo", "hey", "heya", "hola",
    "namaste", "namaskar", "yo",
    "good morning", "good afternoon", "good evening", "good night",
    "morning", "evening",
    "how are you", "how r u", "whats up", "what's up", "sup",
}

GREETING_REPLIES = {
    "en": [
        "Hello! 👋 How can I help you today? Feel free to ask about admission, fees, courses, hostel, or anything else about ITM Gorakhpur.",
        "Hi there! I'm doing great, thanks for asking. What would you like to know about ITM Gorakhpur - admission, fees, courses, or hostel?",
    ],
    "hi": [
        "नमस्ते! 👋 आज मैं आपकी क्या मदद कर सकता हूं? एडमिशन, फीस, कोर्स, हॉस्टल या ITM गोरखपुर से जुड़ी किसी भी बात के बारे में पूछ सकते हैं।",
        "हेलो! मैं बढ़िया हूं, पूछने के लिए शुक्रिया। आप ITM गोरखपुर के बारे में क्या जानना चाहेंगे - एडमिशन, फीस, कोर्स या हॉस्टल?",
    ],
}


def is_greeting(user_message):
    """
    Returns True if the user's message is just a greeting/small-talk
    (like "hi", "hello", "good morning") rather than an actual question.
    """
    cleaned = user_message.strip().lower().strip("?.!,")
    # Only treat it as a pure greeting if it's short - a longer message
    # that happens to start with "hi" (e.g. "hi, what is the fee for BCA")
    # should still go through normal FAQ matching.
    if len(cleaned.split()) > 4:
        return False
    return cleaned in GREETING_WORDS


# ---------- Keyword shortcuts ----------
# Single words like "location" or "hostel" don't share much text with a
# full question like "Where is the college located?", so plain TF-IDF
# similarity can sometimes score them too low. This dictionary lets us
# jump straight to the right FAQ the instant we spot one of these
# keywords in the user's message, without needing an exact sentence match.
# Key = keyword the user might type, Value = the exact FAQ question text
# it should map to (must match a "question" field in faqs.json).
KEYWORD_MAP = {
    "location": "Where is the college located?",
    "address": "Where is the college located?",
    "located": "Where is the college located?",
    "hostel": "Is hostel facility available?",
    "hostels": "Is hostel facility available?",
    "timing": "What is the college timing?",
    "timings": "What is the college timing?",
    "time": "What is the college timing?",
    "contact": "How can I contact the college?",
    "phone": "What is the college phone number?",
    "number": "What is the college phone number?",
    "email": "What is the college email address?",
    "admission": "What is the admission process?",
    "admissions": "What is the admission process?",
    "courses": "What courses are offered by the college?",
    "course": "What courses are offered by the college?",
    "placement": "Does the college help with placements?",
    "placements": "Does the college help with placements?",
    "library": "Does the college have a library?",
    "canteen": "Is there a canteen in the college?",
    "transport": "Is there a transport facility?",
    "bus": "Is there a transport facility?",
    "internet": "Is internet facility available in college?",
    "wifi": "Is internet facility available in college?",
    "scholarship": "Is there a scholarship facility?",
    "scholarships": "Is there a scholarship facility?",
    "ragging": "What is ragging policy of the college?",
    "documents": "What documents are required for admission?",
    "document": "What documents are required for admission?",
    "attendance": "What is the attendance requirement?",
    "affiliation": "Which university is the college affiliated to?",
    "university": "Which university is the college affiliated to?",
    "aicte": "Is the college AICTE approved?",
    "established": "When was the college established?",
    "history": "When was the college established?",
}


def get_keyword_match(user_message):
    """
    Checks if the user's message is just a single keyword (or very short
    phrase) that directly maps to a known FAQ, via KEYWORD_MAP.
    Returns the matching question's index in `faqs`, or None if no
    keyword shortcut applies.
    """
    cleaned = user_message.strip().lower()
    # Strip simple punctuation so "hostel?" or "hostel." still matches
    cleaned = cleaned.strip("?.! ")

    # Only use this shortcut for short inputs (1-2 words) - longer,
    # more detailed questions should go through full TF-IDF matching
    # so we don't accidentally override a more specific question.
    if len(cleaned.split()) > 2:
        return None

    if cleaned in KEYWORD_MAP:
        target_question = KEYWORD_MAP[cleaned]
        return all_questions.index(target_question)

    return None


def get_best_match(user_message, lang="en"):
    """
    Compares user_message against every FAQ question using TF-IDF +
    cosine similarity. Returns (answer, related_questions_list).
    The 'lang' parameter picks which language the answer is returned in
    ("en" for English, "hi" for Hindi) - the matching itself always
    happens against the English questions since that's what the model
    was trained on.
    """
    # First, check if this is just a greeting ("hi", "hello", etc.)
    if is_greeting(user_message):
        replies = GREETING_REPLIES.get(lang, GREETING_REPLIES["en"])
        reply = random.choice(replies)
        # Suggest a few starter questions instead of random FAQs, since
        # the person hasn't asked anything specific yet.
        starter_questions = [
            "What is the admission process?",
            "What courses are offered by the college?",
            "Is hostel facility available?",
        ]
        return reply, starter_questions

    # Next, check for a direct keyword shortcut (e.g. just "hostel")
    keyword_index = get_keyword_match(user_message)

    if keyword_index is not None:
        best_index = keyword_index
        scores = cosine_similarity(vectorizer.transform([user_message]), question_vectors)[0]
    else:
        user_vector = vectorizer.transform([user_message])
        scores = cosine_similarity(user_vector, question_vectors)[0]

        best_index = scores.argmax()
        best_score = scores[best_index]

        if best_score < SIMILARITY_THRESHOLD:
            fallback = FALLBACK_MESSAGES.get(lang, FALLBACK_MESSAGES["en"])
            related = random.sample(all_questions, min(3, len(all_questions)))
            return fallback, related

    answer_key = "answer_hi" if lang == "hi" else "answer"
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
    Receives the user's message and preferred language (JSON) from the
    frontend, finds the best matching answer plus related questions,
    and sends them back as JSON.
    """
    data = request.get_json()
    user_message = data.get("message", "")
    lang = data.get("lang", "en")

    if not user_message.strip():
        empty_msg = "कृपया कोई प्रश्न टाइप करें।" if lang == "hi" else "Please type a question."
        return jsonify({"answer": empty_msg, "related": []})

    answer, related = get_best_match(user_message, lang)
    return jsonify({"answer": answer, "related": related})


if __name__ == "__main__":
    app.run(debug=True)
