import streamlit as st 
from recommender.load_data import clean_movie_data
from recommender.genre_recommender import  get_recommendations 
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

    # Initialize the quiz state 
    if "quiz_started" not in st.session_state : 
        st.session_state.quiz_started = False 
        st.session_state.quiz_index = 0 
        st.session_state.quiz_done = False 
        st.session_state.genre_scores = {}
        # st.session_state.quiz_movies = None 
        st.session_state.user_choice = None

    # Start the quiz
    if not st.session_state.quiz_started : 
        if st.button("🚀 Start Quiz"): 
            st.session_state.quiz_started = True
            st.session_state.quiz_index = 0
            st.session_state.genre_scores = {g: 0 for g in df['genres'].explode().unique()}
            # st.session_state.quiz_movies = df.sample(25).reset_index(drop=True)
            st.session_state.quiz_done = False 
            st.rerun() 

    # Run Quiz if started and not done 
    if st.session_state.quiz_started and not st.session_state.quiz_done : 
        i = st.session_state.quiz_index
        if f"movie_pair_{st.session_state.quiz_index}" not in st.session_state:
            st.session_state[f"movie_pair_{st.session_state.quiz_index}"] = df.sample(2).reset_index(drop=True)

        movie_pair = st.session_state[f"movie_pair_{st.session_state.quiz_index}"]
        movie1, movie2 = movie_pair.iloc[0], movie_pair.iloc[1]
        st.markdown(f"**Round {st.session_state.quiz_index + 1} of 10**")
        st.markdown(f"🎬 1️⃣ {movie1['title']} — {', '.join(movie1['genres'])}")
        st.markdown(f"🎬 2️⃣ {movie2['title']} — {', '.join(movie2['genres'])}")

        # Create selection radio 
        choice = st.radio("Pick your Favorite movie :", 
                          (movie1['title'], movie2['title'] , "Skip"), index = None , 
                          key = f"quiz_choice_{st.session_state.quiz_index}")
        
        # Next Button 
        if st.button("Next") : 
            
            if choice != "Skip" and choice is not None : 
                selected = movie1 if choice == movie1['title'] else movie2 
                for genre in selected['genres']: 
                    st.session_state.genre_scores[genre] += 1 
                st.session_state.quiz_index += 1
            
            prev_key = f"movie_pair_{i}"
            if prev_key in st.session_state: 
                del st.session_state[prev_key]     
            if st.session_state.quiz_index >= 10 : 
                st.session_state.quiz_done = True 

            st.rerun()
        # Show Results 
    if st.session_state.quiz_done : 
            st.success("🎉 Quiz Completed!")
            st.subheader("🎥 Movies you'll probably love:")

            recs = get_recommendations(st.session_state.genre_scores, df)
            for title in recs : 
                st.markdown(f"- {title}")

            if st.button("🔁 Restart Quiz"):
                for key in [
                    "quiz_started", "quiz_index", "quiz_done",
                    "genre_scores",  "user_choice"
                ]:
                    st.session_state.pop(key, None)
            st.rerun()     