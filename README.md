# ITM GIDA Gorakhpur - College FAQ Chatbot

A simple web-based chatbot built with **Flask** that answers frequently
asked questions about Institute of Technology and Management, GIDA, Gorakhpur
(admission process, fees, courses, hostel, timings, etc.)

## How it works

1. All FAQs (question + answer pairs) are stored in `faqs.json`.
2. When a user types a message, the backend (`app.py`) compares it against
   every stored question using Python's built-in `difflib` library, which
   calculates a similarity score between two pieces of text.
3. The FAQ with the highest similarity score is picked, and its answer is
   sent back to the chat window.
4. If nothing matches well enough, the bot replies with a fallback message
   asking the user to rephrase.

## Project structure

```
ITM_Chatbot/
├── app.py                 # Flask backend + matching logic
├── faqs.json              # FAQ dataset (edit this to add/change questions)
├── requirements.txt        # Python dependencies
├── templates/
│   └── index.html          # Chat webpage
└── static/
    ├── style.css            # Chat UI styling
    └── script.js            # Chat frontend logic (sends/receives messages)
```

## How to run it

1. Install Python (3.8 or above) if not already installed.
2. Open a terminal in the `ITM_Chatbot` folder.
3. Install Flask:
   ```
   pip install -r requirements.txt
   ```
4. Run the app:
   ```
   python app.py
   ```
5. Open your browser and go to:
   ```
   http://127.0.0.1:5000
   ```
6. Start chatting! Try questions like:
   - "What is the admission process?"
   - "How much is the BCA fee?"
   - "What courses do you offer?"
   - "Is hostel available?"

## How to add more FAQs

Just open `faqs.json` and add a new object in this format:

```json
{
  "question": "Your new question here",
  "answer": "Your answer here"
}
```

No need to touch `app.py` — it automatically loads whatever is in `faqs.json`.

## Notes / Improvements you can make later

- Current matching uses simple text similarity (`difflib`). For better
  accuracy with longer FAQ lists, you could upgrade to TF-IDF matching
  using `scikit-learn`.
- Fee figures used here are approximate (as told by the student) — update
  `faqs.json` with exact figures from the college office if needed.
- You can deploy this on free hosting like Render or PythonAnywhere for a
  live demo link in your project submission.

## For CodeAlpha Internship Submission

This project can double as the **FAQ Chatbot** task for the CodeAlpha AI
internship, in addition to being a BCA college project. Suggested repo
name: `CodeAlpha_FAQChatbot` (if submitting there) or
`ITM_College_FAQ_Chatbot` (for college submission).
