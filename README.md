# FlowState — Personal Productivity Intelligence Platform

FlowState is a full-stack productivity analytics platform designed to help users understand how their daily habits, wellbeing, focus, and work patterns influence their overall performance.

Instead of relying on a single productivity metric, FlowState combines daily check-ins, analytical scoring, historical trends, interactive visualizations, and AI-generated insights to provide a more complete picture of personal performance.

---

## Overview

Productivity is influenced by multiple factors such as sleep, energy, mood, stress, screen time, focus, task completion, and recovery.

FlowState allows users to record these daily factors through a simple check-in system and transforms the collected data into:

- Performance scores
- Productivity trends
- Recovery and sleep analysis
- Focus and execution metrics
- Historical visualizations
- Personalized analytical insights
- AI-generated recommendations

The goal is to help users understand what contributes to their best-performing days rather than simply tracking tasks completed.

---

## Key Features

### 📊 Performance Dashboard

The FlowState dashboard provides a high-level overview of the user's current performance.

It includes:

- Overall FlowState score
- Recovery
- Capacity
- Focus
- Productivity
- Execution
- Sustainability
- Performance summaries
- Historical trends

### 📈 Productivity Analytics

FlowState analyzes historical daily check-ins to identify patterns across important behavioural metrics.

Analytics include:

- Productivity trends
- Recovery trends
- Sleep patterns
- Focus patterns
- Performance changes over time
- Task completion behaviour
- Comparative performance metrics

Interactive visualizations make it easier to understand changes across multiple days.

### 🌊 FlowState Performance Model

The application evaluates productivity across multiple dimensions instead of relying on a single metric.

| Area | Description |
|------|-------------|
| Recovery | Sleep, rest, hydration and physical recovery |
| Capacity | Energy and mental readiness |
| Focus | Ability to invest attention effectively |
| Productivity | Effectiveness of meaningful work |
| Execution | Consistency in turning plans into action |
| Sustainability | Whether the current pace is realistic to maintain |

This provides a multidimensional view of personal productivity.

### 🤖 AI-Powered Insights

FlowState includes an AI insight service that analyzes recent productivity data and generates structured recommendations.

AI insights follow a simple:

Pattern → Insight → Action

approach.

The system identifies meaningful patterns in recent behaviour and translates them into practical recommendations.

The application also includes error handling so the core analytics experience can continue when AI generation is unavailable.

### 📝 Daily Check-Ins

Users can record daily information such as:

- Sleep
- Recreational screen time
- Focus hours
- Planned tasks
- Completed tasks
- Energy
- Mood
- Stress
- Exercise
- Water intake
- Flow state
- Additional notes

These records form the foundation of the application's analytics.

### 📋 My Logs

Users can view their historical daily check-ins in a structured table.

The logs provide a quick overview of:

- Date
- Sleep
- Screen time
- Focus
- Planned and completed tasks
- Completion rate
- Flow state
- Energy
- Mood

### 🔐 Authentication

FlowState includes user authentication with:

- User registration
- Login
- Password handling
- Session-based authentication
- User-specific productivity data

Each user's daily logs are associated with their own account.

---

## Technology Stack

### Backend

- Python
- Flask
- Flask-SQLAlchemy
- Flask-Login
- Flask-WTF

### Data & Analytics

- Pandas
- NumPy
- Scikit-learn
- Matplotlib
- Seaborn

### Database

- PostgreSQL
- SQLAlchemy ORM

### Frontend

- HTML5
- CSS3
- Bootstrap
- JavaScript
- Plotly

### AI

- Google Gemini API

### Development Tools

- Git
- GitHub
- VS Code
- Python Virtual Environment

---

## Application Architecture

FlowState follows a modular Flask architecture.

FlowState
│
├── app/
│   ├── models/
│   │   ├── user.py
│   │   └── daily_log.py
│   │
│   ├── routes/
│   │   ├── auth.py
│   │   ├── main.py
│   │   └── logs.py
│   │
│   ├── services/
│   │   ├── analytics_service.py
│   │   ├── analytics_dataframe.py
│   │   ├── performance_calculator.py
│   │   ├── trend_service.py
│   │   ├── insights_service.py
│   │   ├── prediction_service.py
│   │   ├── report_service.py
│   │   └── ai_insight_service.py
│   │
│   ├── templates/
│   │   ├── auth/
│   │   ├── dashboard/
│   │   ├── analytics/
│   │   ├── logs/
│   │   └── home.html
│   │
│   └── static/
│       └── images/
│           └── flowstate-logo.png
│
├── migrations/
├── seed_data.py
├── run.py
├── requirements.txt
└── README.md

---

## Data Flow

The general application flow is:

User
  ↓
Daily Check-In
  ↓
Database
  ↓
Data Processing
  ├── Performance Calculation
  ├── Trend Analysis
  ├── Analytics
  ├── Predictions
  └── Insights
        ↓
   AI Insight Layer
        ↓
     Dashboard
        ↓
   User Decisions

---

## Database Structure

The core application stores users and their daily productivity records.

### User

Stores authentication and account information.

### DailyLog

Stores daily productivity and wellbeing information associated with a user.

The relationship can be represented as:

User
 │
 └── DailyLog
      ├── Sleep
      ├── Screen Time
      ├── Focus
      ├── Tasks
      ├── Energy
      ├── Mood
      ├── Stress
      ├── Exercise
      ├── Hydration
      └── Flow State

---

## Demo Data

The project includes a seed-data script for local development and testing.

The current seed setup provides multiple demo users with different behavioural patterns:

- Balanced productivity
- High focus
- Recovery-oriented behaviour
- Lower-performing periods

Each demo account receives historical daily logs so that the dashboard and analytics can be tested with different types of data.

### Demo Usernames

- flow_explorer
- deep_focus
- recovery_first
- struggling_week

These accounts are intended for local testing and demonstration only.

Do not use development/demo credentials for sensitive information or production authentication.

---

## Running Locally

### 1. Clone the repository

git clone https://github.com/Parika23/FlowState
cd FlowState

### 2. Create a virtual environment

On Windows:

python -m venv venv

Activate it:

venv\Scripts\activate

### 3. Install dependencies

pip install -r requirements.txt

### 4. Configure environment variables

Create a local .env file containing the required application configuration.

Example variables:

SECRET_KEY=your-secret-key
DATABASE_URL=your-database-url
GEMINI_API_KEY=your-gemini-api-key

Never commit .env to GitHub.

### 5. Prepare the database

Run the application's database migration/setup process for your environment.

### 6. Seed demo data

python seed_data.py

### 7. Start the application

python run.py

The application will be available at:

http://127.0.0.1:5000

---

## Environment Variables

FlowState uses environment variables for configuration and credentials.

Typical variables include:

- SECRET_KEY
- DATABASE_URL
- GEMINI_API_KEY

Secrets should remain in .env during local development and should be configured securely through environment variables on the production hosting platform.

---

## Project Goals

FlowState was designed around three main ideas:

### 1. Measure

Collect meaningful daily behavioural and productivity data.

### 2. Understand

Use analytics and historical trends to identify patterns.

### 3. Improve

Turn those patterns into actionable recommendations.

The objective is not simply to maximize productivity, but to help users discover a sustainable personal flow state.

---

## Future Improvements

Potential future improvements include:

- More advanced predictive modelling
- Personalized productivity forecasting
- Improved recommendation ranking
- Long-term habit analysis
- Weekly and monthly reports
- More granular trend detection
- Expanded AI-assisted coaching
- Progressive web application support
- Advanced account management

---

## Security Notes

- Never commit .env files.
- Never expose API keys in source code.
- Use environment variables for secrets.
- Use production-specific credentials.
- Do not use development/demo credentials for sensitive information.
- Do not deploy the local Python virtual environment.

---

## Project Status

FlowState is a functional full-stack productivity analytics platform featuring:

- User authentication
- Daily productivity logging
- Multidimensional performance scoring
- Historical analytics
- Trend visualization
- AI-generated insights
- Multiple testing datasets
- Responsive web interface
- Modular Flask backend

---

## Author

Parika Mahajan

B.Tech Computer Science & Engineering

FlowState — Personal Productivity Intelligence Platform

