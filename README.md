# Guess the Celebrity

The user has to guess the celebrity by engaging with an AI quizmaster, they have 20 questions and 3 hints to determine their choice. Users must provide their own API key to connect to the game.

## How to play
- Each game consists of 20 questions, when all questions are used you lose.
- Each game 3 hints are available, type 'hint' to access them.
- Game is won when the celebrity is correctly guessed, or when questions run out.
- Stats page shows key info like, games played, score, questions asked etc.

## Running it locally

1. Install the requirements:
   ```bash
   pip install -r requirements.txt
   ```
2. Start the app:
   ```bash
   streamlit run app.py
   ```

Once the game opens paste your University of Osnabrück AI API key in the sidebar to begin.

## Files
- `app.py` – App setup, page navigation, API key check, and the celebrity/hint list
- `game.py` – The chat interface and game logic
- `stats.py` – Score summary and stats chart
- `requirements.txt` – Required Python libraries
