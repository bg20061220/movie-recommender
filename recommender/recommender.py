import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from load_data import clean_movie_data
from rapidfuzz import process , fuzz
df = clean_movie_data('data/movies.csv')


# Create combined_features column
df['combined_features'] = (
    df['overview'] + ' ' +
    df['genres'].apply(lambda x: ' '.join(x)) + ' ' +
    df['keywords'].apply(lambda x: ' '.join(x)) + ' ' +
    df['cast'].apply(lambda x: ' '.join(x)) + ' ' +
    df['director']
)

# Vectorize the combined features
vectorizer = TfidfVectorizer(stop_words='english')
df['combined_features'] = df['combined_features'].fillna('')
tfidf_matrix = vectorizer.fit_transform(df['combined_features'])

# Compute similarity matrix
similarity_matrix = cosine_similarity(tfidf_matrix, tfidf_matrix)

# Function to get movie recommendations based on title
def get_recommendations(movie_title, df, similarity_matrix, top_n=5):
    titles = df['title'].tolist()

    # Use fuzzy matching to find the closest title
    match = process.extractOne(movie_title, titles, scorer=fuzz.WRatio)

    if match is None or match[1] < 60:
        return []  # No good match found

    matched_title = match[0]
    idx = df[df['title'] == matched_title].index[0]

    # Get similarity scores
    similarity_scores = list(enumerate(similarity_matrix[idx]))
    similarity_scores = sorted(similarity_scores, key=lambda x: x[1], reverse=True)

    # Return top_n similar movie titles
    similar_movies = [df.iloc[i[0]]['title'] for i in similarity_scores[1:top_n+1]]
    return similar_movies

if __name__ == "__main__":
    print(get_recommendations("Avengers Ultron" , df , similarity_matrix, top_n=5))