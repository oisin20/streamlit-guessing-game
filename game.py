import streamlit as st
from openai import OpenAI, AuthenticationError, APIConnectionError, APITimeoutError

#keep model info
MODEL = "Qwen/Qwen3.5-122B-A10B-FP8"
MAX_TOKENS = 300 #can play around with different figures
MAX_QUESTIONS = 20
MAX_HINTS = 3

#client
client = OpenAI(
            base_url="https://litellm.uni-osnabrueck.de/v1",
            api_key=st.session_state.valid_key,
            timeout=30.0)

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

#score calculator easier to do here and save for each game
def calculate_score(questions_used, hints_used):
        base_score=100
        question_penalty = questions_used * 4 #5 questions to guess correctly for max score if no hints used (is it too harsh?)
        hint_penalty = hints_used * 20
        no_hints_bonus =  20 if hints_used == 0 else 0 #bonus for not using any hints

        score = (base_score - question_penalty -  hint_penalty + no_hints_bonus) / 10 #for visuals on barchart
        return(max(0, min(10, score))) #cap the score between 0 and 100 

#transition from key checking to game beginning
if not st.session_state.game_start:
    st.write("You have 20 questions to guess the celebrity. Only yes or no questions are allowed. Are you ready!?")
    if st.button("Start Game"):
        st.session_state.game_start = True
        st.session_state.games_played += 1
        st.rerun()
    st.stop() #nothing below this line runs until the game has started

#celebrity name for checking guesses
celebrity = st.session_state.celebrity.strip().lower()

#start with the sidebar open for hints and counter
st.set_page_config(page_title="Game",
                   layout="centered",
                   initial_sidebar_state="expanded")

#ask user for questions
question = st.chat_input("Ask a yes or no question about the celebrity. If you want help type 'hint'.",
                         disabled=st.session_state.game_over) #locked once the game has ended


#if question is asked add to count and save - don't count hints
if question :
    if question.strip().lower() != "hint":

        if celebrity in question.lower():
            #correct guess - checked here in code so the model isn't needed
            st.session_state.question_count += 1
            st.session_state.wins += 1
            game_score = calculate_score(st.session_state.question_count,st.session_state.hint_count)
            st.session_state.game_history.append({"Game": f"Game {st.session_state.games_played}", #save to dictionary, needed for stats page
                                                                "Questions Used": st.session_state.question_count,
                                                                "Hints Used": st.session_state.hint_count,
                                                                "Guess Score": game_score,
                                                                 "Result": "Win" })
            st.session_state.display_messages.append({"role": "user", "content": question.strip()})
            st.session_state.display_messages.append({"role": "assistant", "content": f"Congragulations! You win! It was {st.session_state.celebrity}. Check the stats page to find out more about your performance."})
            st.balloons()
            st.session_state.game_over = True
            st.rerun()
            

        else:
            #feed question to model and get response
            messages = st.session_state.history + [{"role": "user", "content": question.strip()}]
            try:
                with st.spinner("Pondering"):
                        response = client.chat.completions.create(
                        model=MODEL,
                        messages=messages,
                        max_tokens=MAX_TOKENS,
                        extra_body={"chat_template_kwargs": {"enable_thinking": False}}, #stop thinking so it isnt shown to user
                    )

            except APIConnectionError:
                st.error("Problem connecting with server. Your question wasn't counted. Please try again.")
            except Exception as e:
                st.error(f"Error: {e}. Your question was not counted.") #catch all other other errors with the api

            else:
                reply = (response.choices[0].message.content).strip()

                #only change the state once the call has worked, so a failed call can't be counted
                st.session_state.question_count += 1
                st.session_state.history.append({"role": "user", "content": question.strip()}) #add to the history to show to model
                st.session_state.history.append({"role": "assistant", "content": reply})
                st.session_state.display_messages.append({"role": "user", "content": question.strip()})  #display messages only for user to see
                st.session_state.display_messages.append({"role": "assistant", "content": reply}) 

                #out of questions - game over
                if st.session_state.question_count >= MAX_QUESTIONS:
                    game_score = calculate_score(st.session_state.question_count,st.session_state.hint_count)
                    st.session_state.game_history.append({"Game": f"Game {st.session_state.games_played}",
                                                                "Questions Used": st.session_state.question_count,
                                                                "Hints Used": st.session_state.hint_count,
                                                                "Guess Score": game_score,
                                                                 "Result": "Loss" })
                    st.session_state.game_over = True
                    st.session_state.display_messages.append({"role": "assistant", "content": f"You lose! No questions remaining, the celebrity was {st.session_state.celebrity}."})

                    st.rerun() #restart script

    #if user requests a hint, lookup in dictionary and add to sidebar
    if question.strip().lower() == "hint":
        if st.session_state.hint_count >= MAX_HINTS: #no hints for chancers
            st.write("You are out of hints.")
        else:
            st.session_state.display_hint.append(celebrities[st.session_state.celebrity][st.session_state.hint_count]) #append to state for permanent display
            st.session_state.hint_count += 1 #increment after to match indexing


#show the conversation - can change the aesthetics later
for msg in st.session_state.display_messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

#if questions expire or guess is correct reset session state
if st.session_state.game_over:
    if st.button("Play again"):
        for key in ["question_count", "hint_count", "display_messages", "display_hint", "history", "celebrity", "game_over"]:
            st.session_state.pop(key, None) #pop deletes keys from session state, allows to reset game while keeping session state :)
        st.session_state.games_played += 1
        st.rerun()

#track the number of questions and hints
st.sidebar.metric("Questions remaining", MAX_QUESTIONS - st.session_state.question_count)
st.sidebar.metric("Hints remaining", MAX_HINTS - st.session_state.hint_count)

#keep hints displayed permanently
for i, hint in enumerate(st.session_state.display_hint, start=1):
    st.sidebar.write(f"Hint {i}: {hint}")

