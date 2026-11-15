import streamlit as st

#display stats as columns
if st.session_state.game_over == True:
    col1, col2, col3, col4, col5 = st.columns(5)
    col1.metric(label="Games Played",value=st.session_state.games_played)
    col2.metric(label="Games Won",value=st.session_state.wins)
    col3.metric(label="Questions Asked",value=st.session_state.question_count)
    col1.metric(label="Hints Used",value=st.session_state.hint_count)

    #calculate the player score 

    questions_used = st.session_state.question_count
    hints_used = st.session_state.hint_count

    def calculate_score(questions_used, hints_used):
        base_score=100
        question_penalty = questions_used * 4 #5 questions to guess correctly for max score if no hints used (may be too harsh)
        hint_penalty = hints_used * 20
        no_hints_bonus =  20 if hints_used == 0 else 0 #bonus for not using any hints

        score = base_score - question_penalty -  hint_penalty + no_hints_bonus
        return(max(0, min(100, score))) #cap the score between 0 and 100 

    # calculate and display as a progress bar
    score = calculate_score(questions_used, hints_used)
    st.metric(label="Peformance Score", value=score)
    st.progress(score)

    #show the maths behind the score
    with st.expander("How is this score calculated?"):
        st.write("Performance Score = Base Score - Question Penalty - Hints Penalty (+ No Hints Used Bonus)")
        st.write("Base Score = 100 points")
        st.write("Question penaly = Questions Used x 4 ")
        st.write("Hints penalty = Hints Used x 20")
        st.write("No Hints Used = + 20 Bonus Points")


else:
    st.write("Please wait until your game is over to view your stats.")