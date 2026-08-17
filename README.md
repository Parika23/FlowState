# FlowState

FlowState is a productivity analytics web application designed to help users track and understand lifestyle and productivity patterns through structured data and analytics.

The project combines a Flask based web application with data processing and analysis to provide insights into factors such as tasks, energy levels, sleep, and screen time.

> **Status:** 🚧 Work in Progress
> FlowState is currently under active development. Additional analytics and AI-powered features will be added in future iterations.

## Features

* Track productivity and lifestyle related data
* Store and manage user data using SQL
* Analyze productivity patterns using Python and Pandas
* Generate insights from collected data
* Web-based interface built with Flask
* Structured and modular application architecture

## Tech Stack

* **Python**
* **Flask**
* **Pandas**
* **Scikit-learn**
* **SQL**
* **HTML / CSS**
* **Tailwind CSS**
* **Git & GitHub**

## Project Structure

```text
FlowState/
├── app/
├── migrations/
├── instance/
├── requirements.txt
├── config.py
├── extensions.py
├── run.py
├── seed_data.py
├── .gitignore
└── README.md
```

## Getting Started

### 1. Clone the repository

```bash
git clone https://github.com/Parika23/FlowState.git
cd FlowState
```

### 2. Create a virtual environment

```bash
python -m venv venv
```

### 3. Activate the virtual environment

**Windows:**

```bash
venv\Scripts\activate
```

### 4. Install dependencies

```bash
pip install -r requirements.txt
```

### 5. Configure environment variables

Create a `.env` file in the project root and add the required environment variables.

> Do not commit `.env` to GitHub. It is already included in `.gitignore`.

### 6. Run the application

```bash
python run.py
```

Then open the local URL provided by Flask in your browser.

## Development

FlowState is being developed iteratively. New features, improvements, analytics capabilities, and AI functionality will be added as development progresses.

## Planned Improvements

* Advanced productivity analytics
* Improved dashboards and visualizations
* AI-powered productivity insights
* LLM integration
* Retrieval-Augmented Generation (RAG)
* Personalized recommendations
* Additional data-driven productivity features

## License

This project is currently intended for educational and portfolio purposes.
