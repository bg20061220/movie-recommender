import pandas as pd
import ast
from sklearn.preprocessing import MinMaxScaler


def clean_movie_data(file_path):
    # Load the dataset (adjust separator if needed)
    df = pd.read_csv(file_path)
    print("Before cleaning:")
    print(df['popularity'].head(2).tolist())
    # Columns to keep for recommendation
    useful_cols = [
        'title',
        'genres',
        'overview',
        'keywords',
        'cast',
        'director',
        'vote_average',
        'vote_count',
        'popularity',
        'release_date'
    ]

    # Drop columns not in useful_cols
    df = df[useful_cols]

    known_genres = [
        'Action', 'Adventure', 'Animation', 'Comedy', 'Crime', 'Documentary',
        'Drama', 'Family', 'Fantasy', 'History', 'Horror', 'Music',
        'Mystery', 'Romance', 'Science Fiction', 'TV Movie', 'Thriller',
        'War', 'Western'
    ]
    
    # Function to parse genres string using known genres list
    def parse_genres(genres_str):
        if not isinstance(genres_str, str):
            return []

        words = genres_str.split()  # split on spaces
        genre_list = []

        for genre in known_genres:
            genre_tokens = genre.split()  # e.g., ['Science', 'Fiction']
            if all(token in words for token in genre_tokens):
                genre_list.append(genre)

        return genre_list


    # Apply genre parsing
    df['genres'] = df['genres'].apply(parse_genres)
    
    def split_cast_by_two_words(cast_str):
        if not isinstance(cast_str, str) or cast_str.strip() == "":
            return []
    
        words = cast_str.split()
        # Group every 2 words as a name
        names = [' '.join(words[i:i+2]) for i in range(0, len(words), 2)]
        return names

    # Apply to your cast column
    df['cast'] = df['cast'].apply(split_cast_by_two_words)

    # Convert stringified lists (genres, keywords, cast, crew) into actual Python lists
    # Some columns might be stored as strings representing lists or dicts

    def parse_column(col):
        def try_parse(x):
            if isinstance(x, str):
                return x.split()
            return []
        return col.apply(try_parse)


    # Parse the columns that are likely stringified lists/dicts
    for col in ['keywords']:
        if col in df.columns:
            df[col] = parse_column(df[col])

    # Convert 'release_date' to datetime
    if 'release_date' in df.columns:
        df['release_date'] = pd.to_datetime(df['release_date'], errors='coerce')

    # Optional: fill NaNs in 'overview' with empty string
    df['overview'] = df['overview'].fillna('')

    
    # Initialize the scaler
    scaler = MinMaxScaler()
    df['popularity'] = df['popularity'].fillna(df['popularity'].mean())

    # Reshape and normalize the popularity column
    df['popularity'] = scaler.fit_transform(df[['popularity']])


    # Reset index for cleanliness
    df = df.reset_index(drop=True)

    return df

if __name__ == "__main__":
    cleaned_df = clean_movie_data('data/movies.csv')
    print("\nAfter cleaning:")
    print(cleaned_df['popularity'].head(10).tolist())
