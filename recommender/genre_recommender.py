import pandas as pd
from load_data import clean_movie_data
import random

df = clean_movie_data('data/movies.csv')

# define take_quiz() and get_recommendations()
# Only keep rows that have non-empty genres
df = df[df['genres'].apply(lambda x: isinstance(x, list) and len(x) > 0)].reset_index(drop=True)
known_genres = [
    'Action', 'Adventure', 'Animation', 'Comedy', 'Crime', 'Documentary',
    'Drama', 'Family', 'Fantasy', 'History', 'Horror', 'Music',
    'Mystery', 'Romance', 'Science Fiction', 'TV Movie', 'Thriller',
    'War', 'Western'
]

# Initialize score dictionary
genre_scores = {genre: 0 for genre in known_genres}

def take_quiz(df , genre_scores , rounds = 10):
        print("\n🎬 Welcome to the Movie Taste Quiz!\nChoose your favorite from the two options each round:\n")
        valid_attempts = 0 
        while valid_attempts < rounds:
                movie_pair = df.sample(2).reset_index(drop=True)
                movie1, movie2 = movie_pair.iloc[0], movie_pair.iloc[1]

                print(f"1️⃣ {movie1['title']} — Genres: {', '.join(movie1['genres'])}")
                print(f"2️⃣ {movie2['title']} — Genres: {', '.join(movie2['genres'])}")
                print("3️⃣ Pass (I don't know either)")


                choice = input("Pick 1, 2, or 3: ").strip()
                while choice not in ["1", "2", "3"]:
                    choice = input("Invalid input. Please pick 1, 2, or 3: ").strip()

                if choice == "1":
                    chosen_movie = movie1
                elif choice == "2":
                    chosen_movie = movie2
                else:
                    print("⏭️ Skipping this round.\n")
                    continue  
                # Update genre scores
                for genre in chosen_movie['genres']:
                    if genre in genre_scores:
                        genre_scores[genre] += 1
                valid_attempts += 1
                print()
               

        return genre_scores   

def get_recommendations(genre_scores, df):
     # Get two top 2 genres 
     sorted_genres = sorted(genre_scores.items(), key = lambda x: x[1] , reverse = True)
     top_genres = [g[0] for g in sorted_genres[:2]]

     print(f"Your top genres are: {', '.join(top_genres)}\n")
     genre1, genre2 = top_genres
     
     genre1_only = df[df['genres'].apply(lambda x: genre1 in x and genre2 not in x)]
     genre1_only = genre1_only.sort_values(by= 'vote_count' , ascending=False).head(3)

     genre2_only = df[df['genres'].apply(lambda x: genre2 in x and genre1 not in x)]
     genre2_only = genre2_only.sort_values(by = 'vote_count' , ascending=False).head(3)

     both_genres = df[df['genres'].apply(lambda x: genre1 in x and genre2 in x)]
     both_genres = both_genres.sort_values(by='vote_count', ascending=False).head(3)

     final_recommendations = pd.concat([genre1_only, genre2_only, both_genres])
     final_recommendations = final_recommendations['title'].tolist()

     return final_recommendations

if __name__ == "__main__":
    genre_scores = take_quiz(df, genre_scores, rounds=10)
    recommendations = get_recommendations(genre_scores, df)

    print("\n🎉 Based on your quiz results, we recommend these movies for you:")
    for movie in recommendations:
        print(f"- {movie}")

