# 🎓 ITM GIDA Gorakhpur — College FAQ Chatbot

A simple, web-based FAQ chatbot built with **Flask** and **TF-IDF + Cosine Similarity** that answers common questions about **Institute of Technology and Management (ITM), GIDA, Gorakhpur** — covering admissions, courses, fee structure, hostel, timings, eligibility, placements, and more.

🔗 **Live Demo:** https://itm-college-faq-chatbot.vercel.app/
---

## ✨ Features

- 🤖 Smart FAQ matching using TF-IDF + Cosine Similarity (NLP-based, not just keyword search)
- 🌐 **Bilingual support** — English & Hinglish, switchable with one tap
- 🌙 Light / Dark mode toggle
- 💬 "You might also ask" — related question suggestions
- 👍👎 Feedback buttons on every bot response
- 💾 Chat history saved locally (persists on page reload)
- 📱 Fully responsive, mobile-friendly UI

## 🛠️ Tech Stack

| Layer | Technology |
|---|---|
| Backend | Python, Flask |
| NLP / Matching | scikit-learn (TF-IDF Vectorizer, Cosine Similarity) |
| Frontend | HTML, CSS, JavaScript |
| Deployment | Render |

## 📂 Project Structure

```
ITM_College_FAQ_Chatbot/
├── app.py              # Flask backend + TF-IDF matching logic
├── faqs.json           # FAQ knowledge base (English + Hinglish)
├── requirements.txt    # Python dependencies
├── templates/
│   └── index.html      # Chatbot UI
└── static/
    ├── style.css        # Styling
    └── script.js         # Chat logic, language & theme toggle
```

## 🚀 Running Locally

```bash
git clone https://github.com/abhaypandey0572005-max/ITM_College_FAQ_Chatbot.git
cd ITM_College_FAQ_Chatbot
pip install -r requirements.txt
python app.py
```

Then open `http://127.0.0.1:5000/` in your browser.

## 💡 How It Works

1. All FAQs are loaded from `faqs.json` when the server starts.
2. Each FAQ question is converted into a TF-IDF vector — this captures which words matter most (e.g. "fee", "hostel") vs. common filler words.
3. When a user asks something, their message is compared against every stored question using cosine similarity.
4. The best-matching FAQ's answer is returned, along with the next best matches as "related questions."
5. If no question matches well enough, a fallback message guides the user toward topics the bot can help with.

---

## 👤 About the Developer

**Abhay Pandey**

- 💼 LinkedIn: [linkedin.com/in/abhay-pandey-a6a2ba346](https://www.linkedin.com/in/abhay-pandey-a6a2ba346)
- 💻 GitHub: [github.com/abhaypandey0572005-max](https://github.com/abhaypandey0572005-max)

Built as a real-world project to help ITM GIDA Gorakhpur students and prospective students get instant answers to common college queries.

---

*⭐ If you found this project useful, consider giving it a star on GitHub!*
