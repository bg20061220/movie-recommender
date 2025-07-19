import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from .load_data import clean_movie_data
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
def recommend(movie_title, df, top_n=30):
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

def hybrid_recommend(movie_title, df, genre_scores, top_n=10, content_weight=0.7, genre_weight=0.3):
    titles = df['title'].tolist()
    match = process.extractOne(movie_title, titles, scorer=fuzz.WRatio)
    if match is None or match[1] < 60:
        return []
    matched_title = match[0]
    idx = df[df['title'] == matched_title].index[0]

    similarity_scores = list(enumerate(similarity_matrix[idx]))
    
    # Normalize similarity scores
    sim_values = [score for _, score in similarity_scores]
    min_sim = min(sim_values)
    max_sim = max(sim_values)
    normalized_sim_scores = [
        (i, (score - min_sim) / (max_sim - min_sim + 1e-8))
        for i, score in similarity_scores
    ]

    max_genre_score = max(genre_scores.values()) if genre_scores else 1

    hybrid_scores = []
    for i, sim_score in normalized_sim_scores:
        movie_genres = df.iloc[i]['genres']
        genre_score = sum(genre_scores.get(g, 0) for g in movie_genres)
        genre_score = genre_score / max(1, len(movie_genres))  # average score per genre
        genre_score = genre_score / max_genre_score  # normalize to 0–1

        final_score = content_weight * sim_score + genre_weight * genre_score
        hybrid_scores.append((i, final_score))

    hybrid_scores = sorted(hybrid_scores, key=lambda x: x[1], reverse=True)
    top_indices = [i for i, score in hybrid_scores if i != idx][:10]
    return df.iloc[top_indices]['title'].tolist()

if __name__ == "__main__":
    print(recommend("Avengers Ultron" , df , top_n=5))