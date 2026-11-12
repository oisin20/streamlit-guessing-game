import streamlit as st
import os
from openai import OpenAI
import random

# game intro 
st.title("Guess the Celebrity")
st.write("You have 20 questions to guess the celebrity. Only yes or no questions are allowed. Are you ready!?")

#connect the api
with st.sidebar:
    api_key = st.text_input(
        "UOS AI API-Key",
        type="password",
        key="uos_api_key",
        placeholder="sk-...",
    ).strip()

if not api_key: #check if the api key is provided, if not stop the app and ask for it
    st.info("For the game to run correctly we need your Uni API key. Please enter it in the sidebar.")
    st.stop()

client = OpenAI(
    base_url="https://litellm.uni-osnabrueck.de/v1",
    api_key=api_key
)


#select celebrity  - store in a list and randomly select one (will add more later)
celebrities = ["Angela Merkel", "Cristiano Ronaldo", "Michael Jackson", "Richard Feynman", "Steve Jobs"]
selected_celebrity = random.choice(celebrities)

#remove the selected celebrity from list for later runs
celebrities.remove(selected_celebrity)

#give the model rules, instructions and the selected celebrity
response = client.chat.completions.create(
    model="Qwen/Qwen3.5-122B-A10B-FP8",
    messages=[
        {"role": "system", "content": f"""You are the quizmaster of a guessing game. The user is trying to guess a celebrity in under 20 questions.
You should only respond yes or no, if their question is too broad or not answerable, please respond 'I can only answer yes or no questions'.
If they write 'hint' or similar, please give them a hint about the celebrity. The celebrity is: {selected_celebrity}"""}
    ]
)


#track the number of questions
question_count = 0
st.sidebar.write(f"Questions remaining: {20 - question_count}") #display questions left in sidebar

#question responses
question = st.text_input("Ask a yes or no question about the celebrity. If you want help type 'hint'.")

# pass the question to the model get a response and display it 
if question:
    question_count += 1 # add to the question count
    response = client.chat.completions.create(
        model="Qwen/Qwen3.5-122B-A10B-FP8",
        messages=[
            {"role": "user", "content": f"Is the celebrity {question}?"}
        ]
    )
    st.write(response.choices[0].message.content)

#if user requests a hint, model generates a hint and display it
if question.lower() == "hint":
    response = client.chat.completions.create(
        model="Qwen/Qwen3.5-122B-A10B-FP8",
        messages=[
            {"role": "user", "content": f"Give me a hint about the celebrity {selected_celebrity}."}
        ]
    )
    st.write(response.choices[0].message.content)

