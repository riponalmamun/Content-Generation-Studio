# 🚀 Content Generation Studio

**Content Generation Studio** is a scalable, production-ready **AI-powered content generation backend** built with **FastAPI**.  
It provides structured APIs for generating, managing, and analyzing AI-driven content using modern LLM workflows, memory management, analytics, and rate-limiting.

---

## ✨ Key Features

- ⚡ **FastAPI-based RESTful backend**
- 🤖 **OpenAI-powered content generation**
- 🧠 **Conversation & long-term memory management**
- 📊 **Usage analytics & tracking**
- 🔐 **Authentication & security utilities**
- ⏱️ **Rate limiting for API protection**
- 🧩 **Clean, modular, and scalable architecture**
- 📄 **Swagger/OpenAPI auto documentation**

---

## 🏗️ Project Architecture
```bash
content-generation-studio/
│
├── app/
│ ├── api/ # API route definitions
│ │ ├── analytics.py
│ │ ├── auth.py
│ │ ├── content.py
│ │ ├── conversations.py
│ │ ├── memory.py
│ │ └── messages.py
│ │
│ ├── core/ # Core configurations & prompts
│ │ ├── config.py
│ │ ├── prompts.py
│ │ └── security.py
│ │
│ ├── db/ # Database setup
│ │ ├── base.py
│ │ ├── init_db.py
│ │ └── session.py
│ │
│ ├── models/ # Database models
│ │ ├── user.py
│ │ ├── conversation.py
│ │ ├── memory.py
│ │ └── usage.py
│ │
│ ├── schemas/ # Pydantic schemas
│ │ ├── user.py
│ │ ├── content.py
│ │ ├── conversation.py
│ │ └── memory.py
│ │
│ ├── services/ # Business logic & AI services
│ │ ├── openai_service.py
│ │ ├── embedding_service.py
│ │ ├── conversation_service.py
│ │ ├── memory_service.py
│ │ └── analytics_service.py
│ │
│ ├── utils/ # Helper utilities
│ │ ├── helpers.py
│ │ └── rate_limiter.py
│ │
│ ├── init.py
│ └── main.py # Application entry point
│
├── debug_imports.py
├── requirements.txt
├── .gitignore
└── README.md
```


---

## ⚙️ Tech Stack
```bash
- **Backend:** FastAPI (Python)
- **AI / LLM:** OpenAI API
- **Database:** SQLAlchemy
- **Validation:** Pydantic
- **Security:** Token-based utilities
- **Documentation:** Swagger / OpenAPI
- **Architecture:** Modular, scalable, production-ready
```
---

## 🚀 Getting Started

1️⃣ Clone the Repository
```bash
git clone https://github.com/riponalmamun/Content-Generation-Studio.git
cd Content-Generation-Studio
```
2️⃣ Create Virtual Environment
```bash
python -m venv venv
source venv/bin/activate    # Linux / Mac
venv\Scripts\activate       # Windows
```
3️⃣ Install Dependencies
```bash

pip install -r requirements.txt

```
4️⃣ Configure Environment Variables
Create a .env file in the root directory:
env
OPENAI_API_KEY=your_openai_api_key
5️⃣ Run the Application
```
Copy code
uvicorn app.main:app --reload
📘 API Documentation
After running the server:

Swagger UI:
```bash
http://localhost:8000/docs
```
ReDoc:
```bash
http://localhost:8000/redoc
```
## 🔐 Security & Rate Limiting
Centralized security utilities

API rate limiting to prevent abuse

Designed for future JWT / OAuth integration

## 📊 Analytics & Monitoring
Track API usage

Monitor conversations and memory

Extendable for billing, quotas, and dashboards

## 🧠 Use Cases
AI content generation platforms

Conversational AI backends

AI SaaS products

Research and experimentation with LLMs

Academic and internship projects

## 🛣️ Future Enhancements
Docker & Docker Compose support

Multi-LLM provider integration

Vector database (FAISS / Pinecone)

User-level usage quotas

Frontend dashboard

## 👨‍💻 Author
Md Ripon Al Mamun
AI Developer | FastAPI | Machine Learning | NLP
GitHub: https://github.com/riponalmamun
