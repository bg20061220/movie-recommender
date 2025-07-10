import streamlit as st 
from recommender.load_data import clean_movie_data
from recommender.genre_recommender import take_quiz, get_recommendations 
from recommender.recommender import recommend
# Load the movie data
@st.cache_data
def load_data() :
    return clean_movie_data('data/movies.csv')

df = load_data() 

st.title("🎬 Movie Recommendation App")

tab1, tab2 = st.tabs(["📌 Content-Based", "🧠 Quiz-Based"])

# Content Based Recommender 

with tab1 : 
    st.subheader("Recommend Movies Based on a Movie You Like")
    movie_name = st.text_input("Enter a movie title you like:")

    if "rec_results" not in st.session_state : 
        st.session_state.rec_results = []
        st.session_state.rec_index = 0 
    
    if st.button("Recommend" if st.session_state.rec_index==0 else "Recommend More") : 
        if movie_name : 
            if st.session_state.rec_index == 0 : 
                st.session_state.rec_results = recommend(movie_name, df)

            next_batch = st.session_state.rec_results[st.session_state.rec_index :st.session_state.rec_index + 5]     
            if not next_batch :
                st.info("No more recommendations available.")
            else : 
                for title in next_batch : 
                    st.markdown(f"- {title}")
                st.session_state.rec_index += 5    
        else:
            st.warning("Please enter a movie title.")    
          
    if movie_name != st.session_state.get('last_movie', ''):
        st.session_state.rec_index = 0
        st.session_state.rec_results = []
        st.session_state.last_movie = movie_name


# Quiz Based Recommender

with tab2 : 
    st.subheader("Take Quick Movie Taste Quiz")

    if st.button("Start Quiz") : 
        genre_scores = {genre: 0 for genre in df['genres'].explode().dropna().unique()}
        genre_scores = take_quiz(df , genre_scores, rounds=10)
        recommendations = get_recommendations(genre_scores, df)
        st.success(" Based on your quiz results, we recommend these movies for you:")
        for title in recommendations:
            st.markdown(f"- {title}")   