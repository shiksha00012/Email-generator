<<<<<<< HEAD
# MailAI — AI Email Assistant

A full-stack AI-powered email assistant built with **FastAPI**, **Gemini API**, **MySQL**, and vanilla **HTML/CSS/JS**.

---

## Features

| Feature | Endpoint | Description |
|---|---|---|
| Compose | `POST /api/emails/compose` | Generate a professional email from a purpose + tone |
| Smart Reply | `POST /api/emails/reply` | Auto-reply to a received email |
| Tone Converter | `POST /api/emails/convert-tone` | Rewrite an email in a different tone |
| Summarizer | `POST /api/emails/summarize` | Extract key points, action items, deadlines |
| History | `GET /api/history/` | View, retrieve, and delete saved emails |

---

## Project Structure

```
email_assistant/
├── app/
│   ├── __init__.py
│   ├── main.py              # FastAPI app, CORS, router registration, DB health check
│   ├── database.py          # SQLAlchemy MySQL engine, models, session, init_db
│   ├── schemas.py           # Pydantic request & response models
│   ├── gemini_service.py    # All Gemini API prompt logic
│   └── routers/
│       ├── __init__.py
│       ├── emails.py        # /api/emails/* endpoints
│       └── history.py       # /api/history/* endpoints
├── templates/
│   └── index.html           # Frontend UI (served by FastAPI)
├── static/                  # CSS / JS / images (if needed)
├── .env.example             # Environment variable template
├── requirements.txt
├── run.py                   # Server entry point
└── README.md
```

---

## Quick Start

### 1. Set up MySQL

Make sure MySQL is running, then create the database:
```sql
CREATE DATABASE email_assistant CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
```
> SQLAlchemy will create the `email_history` table automatically on first run.

### 2. Create a virtual environment
```bash
cd email_assistant
python -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate
```

### 3. Install dependencies
```bash
pip install -r requirements.txt
```

### 4. Set up environment variables
```bash
cp .env.example .env
```
Edit `.env` and fill in your values:
```
GEMINI_API_KEY=your_gemini_api_key_here
DATABASE_URL=mysql+pymysql://root:your_password@localhost:3306/email_assistant
```
Get a free Gemini API key at: https://aistudio.google.com/apikey

### 5. Run the server
```bash
python run.py
```
Open your browser at **http://localhost:8000**

If MySQL credentials are wrong the server prints a clear error on startup instead of failing silently.

---

## MySQL Table Schema

SQLAlchemy auto-creates this table, but here it is for reference:

```sql
CREATE TABLE email_history (
    id             INT          NOT NULL AUTO_INCREMENT PRIMARY KEY,
    type           VARCHAR(50)  NOT NULL,          -- compose | reply | tone | summary
    prompt_preview VARCHAR(200) NOT NULL,
    output         TEXT         NOT NULL,
    tone           VARCHAR(50)  DEFAULT NULL,       -- formal | professional | friendly | concise
    created_at     DATETIME     NOT NULL
) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
```

---

## API Reference

### POST `/api/emails/compose`
Generate a new email.
```json
{
  "purpose": "Request 3 days leave for a family event",
  "recipient": "My manager, Priya",
  "context": "Dates: June 20–22",
  "tone": "professional"
}
```
Tone options: `formal` | `professional` | `friendly` | `concise`

**Response:**
```json
{
  "id": 1,
  "type": "compose",
  "output": "Subject: Leave Request – June 20–22\n\nDear Priya, ...",
  "created_at": "2025-06-18T10:30:00"
}
```

---

### POST `/api/emails/reply`
Generate a smart reply to a received email.
```json
{
  "email": "Hi, can we schedule a meeting tomorrow at 2 PM?",
  "instruction": "Confirm but suggest 3 PM instead"
}
```

---

### POST `/api/emails/convert-tone`
Rewrite an email in a different tone.
```json
{
  "email": "hey just wanted to check if u got my report thx",
  "target_tone": "formal"
}
```

---

### POST `/api/emails/summarize`
Summarize a long email thread.
```json
{
  "thread": "Long email thread text goes here..."
}
```
**Response:**
```json
{
  "id": 4,
  "key_points": ["Budget approved for Q3", "New vendor selected"],
  "action_items": ["Send contract to legal by Friday"],
  "deadlines": ["Friday, June 20"],
  "created_at": "2025-06-18T10:30:00"
}
```

---

### GET `/api/history/`
List saved emails (newest first).
```
GET /api/history/?limit=20&offset=0&type_filter=compose
```

### GET `/api/history/{id}`
Get a single saved email with full output.

### DELETE `/api/history/{id}`
Delete a single saved email.

### DELETE `/api/history/`
Clear all history.

### GET `/health`
Returns MySQL connection status.

---

## Interactive API Docs

FastAPI auto-generates docs at:
- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

---

## Common MySQL Errors

| Error | Fix |
|---|---|
| `Access denied for user` | Check `DB_USER` and `DB_PASSWORD` in `.env` |
| `Unknown database 'email_assistant'` | Run `CREATE DATABASE email_assistant CHARACTER SET utf8mb4;` in MySQL |
| `Can't connect to MySQL server` | Make sure MySQL service is running (`sudo systemctl start mysql`) |
| `Authentication plugin 'caching_sha2_password'` | Already handled by `cryptography` in requirements |

---

## Tech Stack

| Layer | Technology |
|---|---|
| Backend | Python 3.11+, FastAPI |
| AI | Google Gemini 1.5 Flash |
| Database | MySQL 8+ |
| Driver | PyMySQL + cryptography |
| ORM | SQLAlchemy 2.0 |
| Validation | Pydantic v2 |
| Frontend | HTML / CSS / Vanilla JS |
| Server | Uvicorn (ASGI) |

