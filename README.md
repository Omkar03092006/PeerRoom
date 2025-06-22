# 🎓 StudyMate

StudyMate is a hybrid Python–Java powered verification platform that helps connect **students of the same subject and year** into WhatsApp groups—**only after verifying their identity via OCR from student ID cards**.

It uses:
- ✅ **Java + Tesseract** for powerful OCR and ID verification
- ✅ **Flask (Python)** as the web backend
- ✅ **HTML/CSS** for a simple frontend interface
- ✅ WhatsApp auto-link routing based on subject/year extracted via OCR

---

## 💡 Use Case

Students upload a **photo of their college ID**.

> If they are verified as a real student (e.g., "2nd year CSE"),  
> they get access to the WhatsApp group for that department & year.  
> No fake accounts. No outsiders. No spam. 🛡️

---

## 🧰 Tech Stack

| Layer       | Tech Used                   |
|-------------|-----------------------------|
| Frontend    | HTML + CSS                  |
| Backend     | Python 3.10+, Flask         |
| OCR Engine  | Java 8+, Tesseract via Tess4J |
| Logic Bridge| Python `subprocess` to call Java |
| Storage     | In-memory / optional SQLite |
| Messaging   | WhatsApp group invite links |

---

🔒 Security Notes
Only verified data from Java’s OCR output is accepted.

No WhatsApp links are shown unless full match is achieved.

Can integrate CAPTCHA + hashed logs for future safety



