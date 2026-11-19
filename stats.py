import streamlit as st
import plotly.express as px

#display stats as columns only if game is over
if st.session_state.game_over == True: 

    #calculate the players score 
    questions_used = st.session_state.question_count
    hints_used = st.session_state.hint_count

    def calculate_score(questions_used, hints_used):
        base_score=100
        question_penalty = questions_used * 4 #5 questions to guess correctly for max score if no hints used (is it too harsh?)
        hint_penalty = hints_used * 20
        no_hints_bonus =  20 if hints_used == 0 else 0 #bonus for not using any hints

        score = base_score - question_penalty -  hint_penalty + no_hints_bonus
        return(max(0, min(100, score))) #cap the score between 0 and 100 

    #create a barchart showing key stats
    fig = px.bar(
        st.session_state.game_history, x="Game", y=["Guess Score", "Questions Used", "Hints Used"], 
        barmode="group",
        title="Your Stats"
)   
    fig.update_yaxes(title_text="") #remove value label
    st.plotly_chart(fig)
    st.caption("In this chart the guess score is out of 10 (score/10) for visual clarity")
    

    # calculate and display as a progress bar
    score = calculate_score(questions_used, hints_used)
    st.metric(label="Your Guess Score", value=score)
    st.progress(score)


    #show the maths behind the score
    with st.expander("How is the guess score calculated?"):
        st.write("Guess Score = Base Score - Question Penalty - Hints Penalty (+ No Hints Used Bonus)")
        st.write("Base Score = 100 points")
        st.write("Question penaly = Questions Used x 4 ")
        st.write("Hints penalty = Hints Used x 20")
        st.write("No Hints Used = + 20 Bonus Points")
        

#if game is not over show a message
else:
   with st.container(border=True):
    st.subheader("🔒 Stats Locked 🔒")
    st.info("Please wait until your current game is over to view your statistics.")