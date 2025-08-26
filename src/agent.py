from groq import Groq
from dotenv import load_dotenv
import os

class WaterIntakeAgent:
    def __init__(self):
        # Load environment variables from .env
        load_dotenv()

        # Get API key from environment
        api_key = os.getenv("GROQ_API_KEY")
        if not api_key:
            raise ValueError("GROQ_API_KEY not found. Check your .env file.")

        # Create Groq client
        self.client = Groq(api_key=api_key)

    def analyze_intake(self, liters_per_day):
        """Analyze the given water intake and return AI-generated feedback."""
        chat_completion = self.client.chat.completions.create(
            messages=[
                {"role": "system", "content": "You are a helpful assistant."},
                {
                    "role": "user",
                    "content": f"Analyze my water intake: {liters_per_day} liters/day"
                }
            ],
            model="llama3-8b-8192"
        )

        # Return only the AI response
        return chat_completion.choices[0].message.content


