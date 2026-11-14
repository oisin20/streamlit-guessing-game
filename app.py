import streamlit as st
import os
from openai import OpenAI, AuthenticationError, APIConnectionError
import random

#session state intialization
if "question_count" not in st.session_state:
    st.session_state['question_count'] = 0
if "hint_count" not in st.session_state:
    st.session_state['hint_count'] = 0
if "display_hint" not in st.session_state:
    st.session_state['display_hint'] = ''

# game intro 
st.title("Guess the Celebrity")
st.write("You have 20 questions to guess the celebrity. Only yes or no questions are allowed. Are you ready!?")


#intialize api key in session state
if "api_key" not in st.session_state:
    st.session_state.api_key = ""
if "key_check" not in st.session_state: #track if the key is valid
    st.session_state.key_check = False

#connect the api
with st.sidebar:
    api_key = st.text_input(
        "Please input your UOS AI API-Key",
        type="password",
        key="api_key",
        placeholder="sk-...",
    ).strip()



    #catch possible errors
    if not api_key: #key not inputted
        st.error("Please input your API key")
    else:
        try:
            with st.spinner("Checking key"):
                client = OpenAI(
            base_url="https://litellm.uni-osnabrueck.de/v1",
            api_key=api_key)
                client.chat.completions.create(
            model="Qwen/Qwen3.5-122B-A10B-FP8",
            messages=[{"role": "user", "content": "test"}],
            max_tokens=1
                )

                st.session_state.key_check = True #change to true
                st.toast("Key works. Let the game begin!!!") #toast disappears after 4 seconds

        except AuthenticationError:
                st.error("Key is invalid.")
                st.session_state.key_check = False
                st.stop()
        except APIConnectionError:
                st.error("Problem connecting with server. Please try again later.")
                st.session_state.key_check = False
                st.stop()
        except Exception as e:
                st.error(f"Error: {e}") #catch all other other errors with the api
                st.session_state.key_check = False
                st.stop()


       
#save the key to a separate variable
if api_key:
 valid_key = st.session_state.api_key

if not api_key: #check if the api key is provided, if not stop the app and ask for it
    st.info("For the game to run correctly we need your Uni API key. Please enter it in the sidebar.")
    st.stop()

#transition from key checking to game beginning
if st.session_state.key_check == True:
    st.button("Start Game")

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
}


#select celebrity using random 
if 'celebrity' not in st.session_state:
    celebrity = random.choice(list(celebrities))
    st.session_state.celebrity = celebrity #save



#give the model rules, instructions and the selected celebrity
if "message" not in st.session_state:
    st.session_state.message = client.chat.completions.create(
        model="Qwen/Qwen3.5-122B-A10B-FP8",
        messages=[
            {"role": "system", "content": f"""You are the quizmaster of a guessing game. The user is trying to guess a celebrity in under 20 questions.
You should only respond yes or no, if their question is too broad or not answerable, please respond 'I can only answer yes or no questions'.
If they ask for a hint tell them they must write 'hint' in this format, and they just wasted a question. The celebrity is: {st.session_state.celebrity}"""},
            {"role": "user", "content": "Let's begin!"}
        ]
)

#track the number of questions
questions_remaining = 20 - st.session_state.quesstion_count
st.sidebar.metric("Questions remaining", questions_remaining) #display questions left in sidebar

#track hints
hints_remaining = 20 - st.session_state.quesstion_count
st.sidebar.metric("Hints remaining", hints_remaining) #beautify later

#ask user for questions
question = st.chat_input("Ask a yes or no question about the celebrity. If you want help type 'hint'.")


#if question is asked add to count and save - don't count hints
if question :
    if question.strip().lower() != "hint":
        st.session_state.question_count += 1 
        st.session_state.message.append({"role": "user", "content": question})

    #feed question to model and get response
    try: 
        with st.spinner("Pondering"):
                response = client.chat.completions.create(
                    model="Qwen/Qwen3.5-122B-A10B-FP8",
                                message=st.session_state.message)
    except APIConnectionError:
        st.error("Problem connecting with server. Please try again later.")
        st.session_state.key_check = False
        st.stop()
    except Exception as e:
        st.error(f"Error: {e}") #catch all other other errors with the api
        st.session_state.key_check = False
        st.stop()
        
    assistant_reply = response.choices[0].message.content
    st.markdown(assistant_reply)
    st.session_state.message.append({"role": "assistant", "content": assistant_reply})

    #if user requests a hint, lookup in dictionary and add to sidebar
    if question.lower() == "hint":
        if st.session_state.hint_count >= 3: #no hints for chancers 
            st.write("You are out of hints.")
        else:
            st.session_state.display_hint.append(celebrities[st.session_state.celebrity][st.session_state.hint_count]) #append to state for permanent display
            st.session_state.hint_count += 1 #increment after to match indexing


#keep hints displayed permanently
st.sidebar.write(st.session_state.display_hint.append)


#if questions expire or guess is correct reset session state