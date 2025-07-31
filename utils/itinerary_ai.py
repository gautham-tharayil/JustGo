import os
import requests
import json

class ItineraryGenerator:
    """
    A class to handle the generation of travel itineraries using the Google Gemini AI model.
    """
    def __init__(self):
        """Initializes the generator and retrieves the API key."""
        self.api_key = os.getenv("GEMINI_API_KEY")
        if not self.api_key:
            raise ValueError("⚠️ GEMINI_API_KEY environment variable not set.")
        
        self.api_url = (
            f"https://generativelanguage.googleapis.com/v1beta/models/"
            f"gemini-1.5-flash:generateContent?key={self.api_key}"
        )

    def generate_itinerary(self, destination_data, duration, interests, budget_data, preferences, start_date=None):
        """Generates a travel itinerary by calling the Gemini API."""
        prompt = self._build_prompt(destination_data, duration, interests, budget_data, preferences, start_date)

        payload = {"contents": [{"parts": [{"text": prompt}]}]}

        try:
            response = requests.post(self.api_url, json=payload)
            response.raise_for_status()
            data = response.json()

            candidates = data.get("candidates", [])
            if not candidates:
                raise ValueError("No candidates in Gemini response")

            itinerary_text = candidates[0]["content"]["parts"][0]["text"]
            return {"itinerary_text": itinerary_text, "model_used": "gemini-1.5-flash"}

        except requests.exceptions.RequestException as e:
            raise ConnectionError(f"Network error calling Gemini API: {e}")
        except (KeyError, IndexError) as e:
            raise ValueError(f"Unexpected response format: {e}")

    def _build_prompt(self, destination, duration, interests, budget, preferences, start_date):
        """Constructs a detailed prompt for the AI."""
        prompt = f"""
        You are an expert travel planner. Create a detailed itinerary.

        Destination: {destination.get('city')}, {destination.get('country')}
        Duration: {duration} days
        Start Date: {start_date}
        Interests: {', '.join(interests) if interests else 'General sightseeing'}
        Budget: {budget.get('amount')} {budget.get('currency')}
        Travel Style: {preferences.get('travel_style')}

        Provide a clear, day-by-day plan with morning, afternoon, and evening activities.
        Each activity should include a short engaging description and practical local tips.
        """
        return prompt.strip()
