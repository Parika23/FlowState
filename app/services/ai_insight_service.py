import os

from dotenv import load_dotenv
from google import genai


load_dotenv()


class AIInsightService:

    def __init__(self):

        api_key = os.getenv("GEMINI_API_KEY")

        if not api_key:
            raise RuntimeError(
                "GEMINI_API_KEY is not configured."
            )

        self.client = genai.Client(
            api_key=api_key
        )

        self.model = "gemini-3.6-flash"

    def generate_insight(self, data):

        # Do not call Gemini without enough history
        # to support a meaningful pattern-based insight.
        if not data or len(data) < 3:
            return None

        prompt = f"""
You are the AI productivity coach inside FlowState.

Analyze the user's productivity data below.

User data:
{data}

Give a concise, practical analysis.

Return exactly three sections:

1. PATTERN
Identify the most important pattern in the data.

2. INSIGHT
Explain what the pattern could mean for the user's productivity.

3. ACTION
Give one practical action the user can take.

Rules:
- Use only the information provided.
- Do not diagnose medical conditions.
- Do not make extreme claims.
- Do not invent missing data.
- Keep the response under 150 words.
"""

        try:

            response = self.client.models.generate_content(
                model=self.model,
                contents=prompt
            )

            if not response.text:
                return None

            return response.text.strip()

        except Exception:

            return (
                "AI insights are temporarily unavailable. "
                "Please try again later."
            )
