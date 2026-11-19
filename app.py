import streamlit as st
import re
from openai import OpenAI, AuthenticationError, APIConnectionError, APITimeoutError
import random

#create pages
game_page = st.Page("game.py", title="Play", icon="🎮")
stats_page = st.Page("stats.py", title="Stats", icon="📊")

pg = st.navigation([game_page, stats_page], position="top") #put pages at top to save sidebar for hints and count

#celebrity dictionary with hints - AI was used to create the hints
celebrities = {
        "Angela Merkel": [
            "Holds a doctorate in the natural sciences.",
            "Spent early life on the eastern side of a divided country.",
            "Held the top office of a country for over a decade and a half.",
        ],
        "Cristiano Ronaldo": [
            "Born on an island far from the country's mainland.",
            "Has won the top domestic league in more than two countries.",
            "Holds multiple of the sport's top individual awards.",
        ],
        "Michael Jackson": [
            "Started performing before the teenage years, alongside siblings.",
            "A final planned tour was set for London.",
            "Known for a dance move that looks like moving backwards while appearing to walk forwards.",
        ],
        "Richard Feynman": [
            "Worked in the desert during wartime.",
            "Shared a Nobel Prize with two others.",
            "Co-authored a famous set of introductory physics lectures used by students worldwide.",
        ],
        "Steve Jobs": [
            "Was adopted as a baby.",
            "Dropped out of college but kept attending one class.",
            "Was pushed out of the company co-founded, then returned to lead it.",
        ],
        "Jensen Huang": [
            "Worked as a dishwasher at a roadside diner chain before co-founding a company at one.",
            "Holds an engineering degree and spent years designing microprocessors before becoming a CEO.",
            "Known for wearing a signature black leather jacket and had recent controversy.",
        ],
        "Andy Burnham": [
            "Studied English at Cambridge and worked as a parliamentary researcher before entering office.",
            "Served in multiple UK Cabinet roles, including Health Secretary, before leaving Westminster.",
            "Became the first directly elected mayor of a major northern English city-region.",
        ],
        "Taylor Swift": [
            "Grew up on a Christmas tree farm before moving south as a teenager to pursue music.",
            "Re-recorded several earlier studio albums in an ownership dispute.",
            "Headlined a record-breaking global stadium tour structured around distinct musical eras.",
        ],
            "Serena Williams": [
            "Was the youngest of five sisters and began training in a sport before starting school.",
            "Competed professionally alongside an older sister for more than two decades.",
            "Dominated women's tennis for years, winning more major singles titles than anyone else in the modern era.",
        ],
        "Marie Curie": [
            "Worked as a governess to fund an older sister's studies before pursuing her own degree abroad.",
            "Conducted pioneering research into invisible rays emitted by heavy minerals.",
            "Became the first woman to win a Nobel Prize, later winning a second in another science.",
        ]
    }

#session state intialization track everything in one place
if "valid_key" not in st.session_state:
    st.session_state.valid_key = ""
if "game_start" not in st.session_state:
    st.session_state.game_start = False
if "game_over" not in st.session_state: #has the game ended (win or out of questions)
    st.session_state.game_over = False
if "question_count" not in st.session_state:
    st.session_state['question_count'] = 0
if "hint_count" not in st.session_state:
    st.session_state['hint_count'] = 0
if "games_played" not in st.session_state:
    st.session_state.games_played = 0
if "wins" not in st.session_state:
    st.session_state.wins = 0
if "game_history" not in st.session_state:
      st.session_state.game_history = []
if "celebrity" not in st.session_state:
    st.session_state.celebrity = random.choice(list(celebrities)) #random select celeb
if "history" not in st.session_state: #to feed back into llm
    st.session_state.history = [
        {"role": "system", "content": f"""You are the quizmaster of a guessing game. The user is trying to guess a celebrity in 20 questions.
    You should only respond yes or no, if their question is too broad or not answerable, please respond 'I can only answer yes or no questions'.
    If they ask for a hint tell them they must write 'hint' in this format, and they just wasted a question. Never reveal the name of the celebrity. The celebrity is: {st.session_state.celebrity}"""}
    ]
if "display_messages" not in st.session_state: #what the user sees in the chat
    st.session_state.display_messages = []
if "display_hint" not in st.session_state:
    st.session_state['display_hint'] = []

#keep model info
MODEL = "Qwen/Qwen3.5-122B-A10B-FP8"
MAX_TOKENS = 300 #can play around with different figures
MAX_QUESTIONS = 20
MAX_HINTS = 3

#intialize api key in session state
if "api_key" not in st.session_state:
    st.session_state.api_key = ""

# game title
st.title("Guess the Celebrity")

#input the api key
if not st.session_state.game_start: #only show if game hasn't started
    with st.sidebar:
        api_key = st.text_input(
            "Please input your UOS AI API-Key",
            type="password",
            key="api_key",
            placeholder="sk-...",
        ).strip()


    if not api_key: #key not inputted
            st.error("Please input your API key")
            st.stop()

    client = OpenAI(
                base_url="https://litellm.uni-osnabrueck.de/v1",
                api_key=api_key,
                timeout=30.0) #is this too long/short？ (not sure how long uni servers take)

    #only run check if keys not valid
    if api_key != st.session_state.valid_key:
        try:
            with st.spinner("Checking key"):
                    client.chat.completions.create(
                model=MODEL,
                messages=[{"role": "user", "content": "test"}],
                max_tokens=1
                    )

                    st.session_state.valid_key = api_key #save validated key
                    st.toast("Key works. Let the game begin!!!") #toast disappears after 4 seconds

        except AuthenticationError:
                    st.error("Key is invalid.")
                    st.stop()
        except APITimeoutError: 
                    st.error("The server took too long to respond. Please try again later.")
                    st.stop()
        except APIConnectionError:
                    st.error("Problem connecting with server. Please try again later.")
                    st.stop()
        except Exception as e:
                    st.error(f"Error: {e}") #catch all other other errors with the api
                    st.stop()

    #everything above shared gloablly
pg.run()
