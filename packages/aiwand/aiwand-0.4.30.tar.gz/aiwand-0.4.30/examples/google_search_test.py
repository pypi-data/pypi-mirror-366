"""
Test the google search tool for Gemini models.
"""

import aiwand
from dotenv import load_dotenv

load_dotenv()

def main():
    user_prompt = "'When was the last F1 GP and who won?"
    response = aiwand.call_ai(
        debug=True,
        model="gemini-2.5-flash-lite",
        use_google_search=True,
        user_prompt=user_prompt
    )
    print(response)


if __name__ == "__main__":
    main()