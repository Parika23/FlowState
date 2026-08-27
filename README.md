# 🌊 FlowState

🔗 **[Live Demo](https://flowstate-kf0c.onrender.com/)** — try it with demo account `flow_explorer`
*(hosted on a free tier — may take ~30s to wake up on first load)*

**A personal productivity & wellbeing tracker that scores your days, spots patterns, and predicts tomorrow.**

FlowState is a full-stack Flask web app. Every day, you log a few simple numbers — sleep, focus, mood, stress, tasks completed — and FlowState turns that into a performance score, historical trends, and an AI-generated insight about what's actually driving your good (and bad) days.

---

## What it actually does

Most habit trackers stop at "here's your data in a table." FlowState goes one step further and asks: *what does this data mean, and what should I do about it?*

1. **You check in** — a short daily form: sleep hours, focus hours, energy, mood, stress, exercise, water, tasks planned vs. completed, and whether you hit a "flow state."
2. **It's scored** — your check-in is converted into a multi-dimensional performance score (not just one number).
3. **It's analyzed** — trends, correlations, and comparisons are calculated across your history.
4. **It's predicted** — a machine learning model forecasts tomorrow's performance based on today's behavior.
5. **It's explained** — an AI insight layer (Google Gemini) reads your recent data and writes a plain-English takeaway.

---

## The FlowState Model

Instead of one productivity number, every day is scored across six dimensions:

| Dimension | What it captures |
|---|---|
| **Recovery** | Sleep and physical rest |
| **Capacity** | Energy and mental readiness |
| **Focus** | Attention actually invested in work |
| **Productivity** | Effectiveness of that work |
| **Execution** | How much of the plan actually got done |
| **Sustainability** | Whether this pace is realistic to keep up |

This is the core design idea behind the app: a "good day" isn't just tasks-completed, it's a combination of how rested, focused, and consistent you were.

---

## Key features

- **📝 Daily check-ins** — a validated form (Flask-WTF) capturing sleep, screen time, focus, tasks, mood, stress, exercise, hydration, and flow state, with duplicate-entry protection per day.
- **📊 Dashboard** — your current FlowState score across all six dimensions, plus a performance summary.
- **📈 Analytics** — historical trends, sleep/recovery/productivity patterns, and correlation analysis across your check-ins, built with Pandas and visualized with Matplotlib/Seaborn.
- **🔮 Next-day prediction** — a `scikit-learn` `LinearRegression` model trained on your own history, predicting tomorrow's flow-state index, productivity score, and recovery score from today's behavior (evaluated with MAE and R²).
- **🤖 AI-generated insights** — your last 14 days of data is sent to the Gemini API, which returns a plain-English pattern → insight → action recommendation. Falls back gracefully if the AI call fails, so the rest of the app keeps working.
- **📤 Export** — download your analytics as CSV or Excel straight from the browser.
- **📋 My Logs** — a searchable table of every check-in you've ever made.
- **🔐 Accounts** — registration, login, and session-based auth (Flask-Login), with every user's data fully isolated from every other user's.

---

## Tech stack

| Layer | Tools |
|---|---|
| Backend | Python, Flask, Flask-SQLAlchemy, Flask-Login, Flask-WTF |
| Database | PostgreSQL, SQLAlchemy ORM, Flask-Migrate |
| Data & ML | Pandas, NumPy, scikit-learn, Matplotlib, Seaborn |
| AI | Google Gemini API |
| Frontend | HTML5, CSS3, Bootstrap, JavaScript, Plotly |
| Dev tools | Git, GitHub, VS Code |

---

## How it's built

```
FlowState/
├── app/
│   ├── models/            # User, DailyLog, Prediction, Insight
│   ├── routes/             # auth, main (dashboard/analytics), logs
│   ├── services/           # all the business logic lives here
│   │   ├── analytics_service.py       # trend + correlation analysis
│   │   ├── analytics_dataframe.py     # raw logs → Pandas DataFrame
│   │   ├── performance_engine.py      # the 6-dimension scoring model
│   │   ├── trend_service.py           # historical trend calculations
│   │   ├── insights_service.py        # rule-based insight generation
│   │   ├── prediction_service.py      # ML next-day prediction
│   │   ├── report_service.py          # CSV / Excel export
│   │   └── ai_insight_service.py      # Gemini API integration
│   ├── templates/          # Jinja2 + Bootstrap views
│   └── static/             # CSS, JS, generated chart images
├── migrations/              # Flask-Migrate / Alembic
├── seed_data.py             # generates demo users + historical logs
├── run.py                   # app entry point
└── requirements.txt
```

The app follows a clean **routes → services → models** structure: routes stay thin, all the scoring/analytics/ML logic lives in the service layer, and every service filters by `user_id` so the app is multi-tenant by design.

---

## Getting started

### 1. Clone and enter the project
```bash
git clone https://github.com/Parika23/FlowState
cd FlowState
```

### 2. Create and activate a virtual environment
```bash
python -m venv venv
venv\Scripts\activate      # Windows
source venv/bin/activate   # macOS / Linux
```

### 3. Install dependencies
```bash
pip install -r requirements.txt
```

### 4. Set up environment variables
Create a `.env` file in the project root:
```
SECRET_KEY=your-secret-key
DATABASE_URL=your-postgresql-url
GEMINI_API_KEY=your-gemini-api-key
```
Never commit `.env` — it holds your secrets.

### 5. Set up the database
```bash
flask db upgrade
```

### 6. (Optional) Load demo data
```bash
python seed_data.py
```
This creates a few demo accounts (`flow_explorer`, `deep_focus`, `recovery_first`, `struggling_week`) with realistic historical logs, so the dashboard has something to show right away. **Demo accounts are for local testing only.**

### 7. Run the app
```bash
python run.py
```
Visit **http://127.0.0.1:5000**

---

## Why FlowState

Most productivity apps optimize for one thing: task completion. FlowState was built around a different question — *what actually makes a day go well?* — and treats sleep, focus, mood, and pacing as first-class inputs, not afterthoughts. The prediction and insight layers exist so the app doesn't just describe the past, it gives you something to act on tomorrow.

---

## Roadmap

- Persist and cache trained prediction models instead of retraining on every load
- Weekly / monthly summary reports
- Long-term habit correlation analysis
- Progressive Web App support
- Richer account management (password reset, profile settings)

---

## Author

**Parika Mahajan**
B.Tech, Computer Science & Engineering
