import streamlit as st 
from recommender.load_data import clean_movie_data
from recommender.genre_recommender import  get_recommendations 
from recommender.recommender import recommend , hybrid_recommend
import requests 
from functools import lru_cache
import os 
from dotenv import load_dotenv
load_dotenv() 
OMDB_API_KEY = os.getenv("OMDB_API_KEY")

# Styling
st.markdown("""
<style>
    /* Background */
    .stApp {
        background-color: #DCE9F9 !important;
    }
    .css-18e3th9 {
        background-color: #DCE9F9 !important;
    }

    /* Import font */
    @import url('https://fonts.googleapis.com/css2?family=Open+Sans&display=swap');

    /* Font family and color for general text (paragraphs, markdown) */
    .css-10trblm,  /* markdown text */
    .css-1v3fvcr,  /* sidebar text */
    .css-1d391kg,  /* main content text */
    .stMarkdown {
        font-family: 'Open Sans', sans-serif !important;
        color: #2C3E50 !important;
        font-size: 16px !important;
        line-height: 1.5 !important;
    }

    /* Also style list items (ul, ol) for movie lists */
    ul, ol {
        color: #2C3E50 !important;
        font-family: 'Open Sans', sans-serif !important;
        font-size: 16px !important;
        line-height: 1.5 !important;
    }

    /* Headers */
    h1, h2, h3, h4, h5, h6 {
        font-family: 'Open Sans', sans-serif !important;
        color: #1B2838 !important;
    }
</style>
""", unsafe_allow_html=True)





# Load the movie data
@st.cache_data
def load_data() :
    return clean_movie_data('data/movies.csv')

df = load_data() 

@lru_cache(maxsize = 1000)
def get_movie_poster_and_imdb_url(title):
    params = {
         't' : title , 
         'apikey' : OMDB_API_KEY
    }
    response = requests.get("https://www.omdbapi.com/" , params = params)

    if response.status_code == 200 : 
         data = response.json()
         if data.get('Response') == 'True' : 
              poster_url = data.get('Poster' ,  ' ')
              imdb_id = data.get('imdbID', ' '  )
              imdb_url = f"https://www.imdb.com/title/{imdb_id}/" if imdb_id else None
              return poster_url, imdb_url
         else : 
              print(f"Error: {data.get('Error', 'Unknown error')}")
    else : 
         print("API Call failed with status code " , response.status_code)

    return None ,None               
st.title("🎬 Movie Recommendation App")

tab1, tab2 , tab3  = st.tabs(["📌 Content-Based", "🧠 Quiz-Based" , "Hybrid Recommender"])

# Content Based Recommender 
with tab1 : 
    st.subheader("Recommend Movies Based on a Movie You Like")
    movie_name = st.text_input("Enter a movie title you like:")
    # Initialize session state for recommendations
    if "rec_results" not in st.session_state : 
        st.session_state.rec_results = []
        st.session_state.rec_index = 0 
        st.session_state.last_movie = ""
    # Reset recommendations if the movie name changes    
    if movie_name != st.session_state.get('last_movie', ''):
        st.session_state.rec_index = 0
        st.session_state.rec_results = []
        st.session_state.last_movie = movie_name
  

   
    if st.button("Recommend") :
        if movie_name : 
                st.session_state.rec_results = recommend(movie_name, df)
                st.session_state.rec_index = 0
        else:
            st.warning("Please enter a movie title.")           

    if st.session_state.rec_results:      
            next_batch = st.session_state.rec_results[st.session_state.rec_index :st.session_state.rec_index + 5]     
            if not next_batch :
                st.info("No more recommendations available.")
            else : 
                cols = st.columns(2)
                for i , title in enumerate(next_batch):
                    with cols[i % 2]:
                        poster_url , imdb_url = get_movie_poster_and_imdb_url(title )

                        if poster_url:
                            st.image(poster_url, width=100, caption=title)
                        else : 
                             st.write("Poster not found")
                        st.markdown(f"- {title}" , unsafe_allow_html=True)

                        if imdb_url:    
                            st.markdown(f"[🔗 IMDb Page]({imdb_url})", unsafe_allow_html=True)         
            if st.session_state.rec_index + 5 < len(st.session_state.rec_results):
                    if st.button("Show More"):
                        st.session_state.rec_index += 5
            else:
                st.info("✅ No more recommendations available.")            
                      
              
      
          



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
        col1 , col2 = st.columns(2)
        poster1 , _ = get_movie_poster_and_imdb_url(movie1['title'])
        poster2 , _ = get_movie_poster_and_imdb_url(movie2['title'])

        with col1 : 
            if poster1 : 
                  st.image(poster1, width=100, caption=movie1['title'])
            st.markdown(f"- {movie1['title']}")
            st.markdown(f"**Genres:** {', '.join(movie1['genres'])}")
        with col2 :
            if poster2 : 
                  st.image(poster2, width=100, caption=movie2['title'])
            st.markdown(f"- {movie2['title']}")
            st.markdown(f"**Genres:** {', '.join(movie2['genres'])}")

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
            for title in recs[:st.session_state.recs_to_show]:  
                poster_url, imdb_url= get_movie_poster_and_imdb_url(title)
                col1 , col2 = st.columns([1 , 3])
                with col1 : 
                    if poster_url:
                        st.image(poster_url, width=100, caption=title)
                    else : 
                        print("Poster not found")
                with col2 :
                    st.markdown(f"### {title}")

                    if imdb_url:
                            st.markdown(f"[🔗 IMDb Page]({imdb_url})", unsafe_allow_html=True)
                        

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
                

 # Hybrid Recommender

with tab3 : 
    quiz_done = st.session_state.get('quiz_done', False)
    genre_scores = st.session_state.get('genre_scores', {})
    st.subheader("Hybrid Movie Recommender")
    quiz_done = st.session_state.get('quiz_done', False)
    genre_scores = st.session_state.get('genre_scores', {})
    is_disabled = not quiz_done or not genre_scores or sum(genre_scores.values()) == 0
    if is_disabled:
            st.warning("🚨 You must complete the quiz first to use the hybrid recommender.")
            st.info("Go to the **Quiz Tab** to finish it. Once done, this section will unlock.")
    if "hybrid_rec_index" not in st.session_state : 
             st.session_state.hybrid_rec_index = 0 
             st.session_state.hybrid_rec_results = [] 
    if "run_hybrid" not in st.session_state: 
            st.session_state.run_hybrid = False      
         
    content_weight = st.slider("Movie Title Similarity Weight", 
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
                poster_url , imdb_url = get_movie_poster_and_imdb_url(title)
                col1 , col2 = st.columns([1, 3])
                with col1:
                    if poster_url:
                        st.image(poster_url, width=100, caption=title)
                    else: 
                        print("Poster not found ")
                with col2 : 
                    st.markdown(f"### {title}")
                    if imdb_url:
                         st.markdown(f"[🔗 IMDb Page]({imdb_url})", unsafe_allow_html=True)     
                
                st.markdown("---")
            st.session_state.hybrid_rec_index += 5

            if st.session_state.hybrid_rec_index >= len(st.session_state.hybrid_rec_results):
                st.info("✅ No more recommendations.")
            else:
                if st.button("Show More" , key ="show_more_hybrid"):
                    st.rerun()

        