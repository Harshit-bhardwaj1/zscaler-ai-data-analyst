# Zscaler AI Data Analyst

AI-powered business data analyst prototype built for the Zscaler AI Product Builder Assessment.

## Product

The application allows users to ask natural-language business questions across multiple structured tables.

Example:

> Which customer has the highest churn risk?

The system:

1. Understands the business question.
2. Identifies relevant data tables.
3. Generates or selects analysis logic.
4. Generates SQL when AI is available.
5. Validates SQL for safety.
6. Executes the query against PostgreSQL.
7. Validates the result.
8. Returns a plain-English answer.
9. Shows evidence, tables used, assumptions and SQL.
10. Maintains conversation context for follow-up questions.

## Tech Stack

### Frontend

- React
- Vite
- Axios
- Lucide React

### Backend

- Python
- FastAPI
- SQLAlchemy
- PostgreSQL
- SQLGlot
- Groq API

## Project Structure

```text
zscaler-ai-data-analyst/
│
├── backend/
│   ├── app/
│   │   ├── routes/
│   │   ├── services/
│   │   ├── models.py
│   │   ├── database.py
│   │   ├── config.py
│   │   ├── seed.py
│   │   └── main.py
│   ├── .env
│   └── requirements.txt
│
├── frontend/
│   ├── src/
│   │   ├── components/
│   │   ├── pages/
│   │   ├── services/
│   │   ├── App.jsx
│   │   └── main.jsx
│   └── package.json
│
├── README.md
├── DECISIONS.md
├── AI_USAGE.md
└── ARCHITECTURE.md