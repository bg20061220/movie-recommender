import streamlit as st 
from recommender.load_data import clean_movie_data
from recommender.genre_recommender import  get_recommendations 
from recommender.recommender import recommend , hybrid_recommend
# Load the movie data
@st.cache_data
def load_data() :
    return clean_movie_data('data/movies.csv')

df = load_data() 

st.title("🎬 Movie Recommendation App")

tab1, tab2 , tab3  = st.tabs(["📌 Content-Based", "🧠 Quiz-Based" , "Hybrid Recommender"])

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
    if 'recs_to_show' not in st.session_state: 
        st.session_state.recs_to_show = 5 
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
            print(f"Quiz done in tab 2 : {st.session_state.get('quiz_done', False)}")
                  

            st.rerun()
        # Show Results 
    if st.session_state.quiz_done : 
            st.success("🎉 Quiz Completed!")
            st.subheader("🎥 Movies you'll probably love:")

            recs = get_recommendations(st.session_state.genre_scores, df)
            for title in recs[:st.session_state.recs_to_show]:  
                st.markdown(f"- {title}")

            if st.session_state.recs_to_show < len(recs): 
                if st.button("Show More Recommendations"):
                    st.session_state.recs_to_show += 5
                    st.rerun()
            if st.button("🔁 Restart Quiz"):
                for key in [
                    "quiz_started", "quiz_index", "quiz_done",
                    "genre_scores",  "user_choice"
                ]:
                    st.session_state.pop(key, None)
            st.rerun()     

 # Hybrid Recommender

with tab3 : 
        st.subheader("Hybrid Movie Recommender")
        quiz_done = st.session_state.get('quiz_done', False)
        genre_scores = st.session_state.get('genre_scores', {})
        is_disabled = not quiz_done or not genre_scores or sum(genre_scores.values()) == 0
        print(f"Quiz done: {quiz_done}")
        if is_disabled:
            st.warning("🚨 You must complete the quiz first to use the hybrid recommender.")
            st.info("Go to the **Quiz Tab** to finish it. Once done, this section will unlock.")
        if "hybrid_rec_index" not in st.session_state : 
             st.session_state.hybrid_rec_index = 0 
             st.session_state.hybrid_rec_results = [] 
        if "run_hybrid" not in st.session_state: 
            st.session_state.run_hybrid = False      
         
        content_weight = st.slider("Content Similarity Weight", 
            min_value=0.0, max_value=1.0, value=0.5, step=0.05, 
            help="Adjust the weight for content similarity in hybrid recommendations.", disabled=is_disabled) 
        
        genre_weight = 1 - content_weight

        base_movie = st.text_input("Enter a movie title for hybrid recommendations:" , disabled=is_disabled)


        if st.button("Get Hybrid Recommendations", disabled=is_disabled):

            if base_movie.strip() == "":
                st.warning("Please enter a valid movie title.")
            else:
                st.session_state.run_hybrid = True
                st.session_state.hybrid_rec_index = 0
                st.session_state.hybrid_rec_results = hybrid_recommend(
                    base_movie, df, genre_scores, content_weight, genre_weight
                )
                st.rerun()

        # Now check if hybrid should run
        if st.session_state.run_hybrid and st.session_state.hybrid_rec_results:
            recs_to_show = st.session_state.hybrid_rec_results[
                st.session_state.hybrid_rec_index : st.session_state.hybrid_rec_index + 5
            ]
            for title in recs_to_show:
                st.markdown(f"- {title}")
            st.session_state.hybrid_rec_index += 5

            if st.session_state.hybrid_rec_index >= len(st.session_state.hybrid_rec_results):
                st.info("✅ No more recommendations.")
            else:
                if st.button("Show More"):
                    st.rerun()

        