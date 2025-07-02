import pandas as pd
import ast


def clean_movie_data(file_path):
    # Load the dataset (adjust separator if needed)
    df = pd.read_csv(file_path)

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
        genres = []
        for genre in known_genres:
            if genre in genres_str:
                genres.append(genre)
        return genres

    # Apply genre parsing
    df['genres'] = df['genres'].apply(parse_genres)


    # Convert stringified lists (genres, keywords, cast, crew) into actual Python lists
    # Some columns might be stored as strings representing lists or dicts

    def parse_column(col):
        def try_parse(x):
            try:
                return ast.literal_eval(x)
            except:
                return []
        return col.apply(try_parse)

    # Parse the columns that are likely stringified lists/dicts
    for col in ['genres', 'keywords', 'cast', 'crew']:
        if col in df.columns:
            df[col] = parse_column(df[col])

    # Convert 'release_date' to datetime
    if 'release_date' in df.columns:
        df['release_date'] = pd.to_datetime(df['release_date'], errors='coerce')

    # Optional: fill NaNs in 'overview' with empty string
    df['overview'] = df['overview'].fillna('')

    # Reset index for cleanliness
    df = df.reset_index(drop=True)

    return df

if __name__ == "__main__":
    cleaned_df = clean_movie_data('data/movies.csv')
    print(cleaned_df.head())
    print(f"Data shape after cleaning: {cleaned_df.shape}")
