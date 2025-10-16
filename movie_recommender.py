# Load datasets
movies = ['movie_genre', 'movie_id', 'movie_name']
ratings = ['movie_name', 'rating', 'user_id']

# Load movies from file. Return dict mapping movie_name -> (movie_id, movie_genre)
def load_movies(filename: str) -> dict:
    return {}

# Load ratings. Return dict mapping movie_name -> list of (user_id, rating)
def load_ratings(filename: str) -> dict:
   return {}

# Movie popularity
# Return top n movies ranked by avg rating
def top_movies(n: int, ratings: dict) -> list:
    return []

# Movie popularity in genre
# Return top n movies in genre by avg rating
def top_movies_in_genre(n: int, genre: str, movies: dict, ratings: dict) -> list:
    # Collect movies that match the genre
    # movies: mapping movie_name -> (movie_id, movie_genre)
    # ratings: mapping movie_name -> list of (user_id, rating)
    genre_movies = {}
    for m_name, info in movies.items():
        # support both tuple/list or dict entries
        # assume genre stored as second element when sequence
        movie_genre = None
        if isinstance(info, (list, tuple)) and len(info) >= 2:
            movie_genre = info[1]
        elif isinstance(info, dict) and 'genre' in info:
            movie_genre = info.get('genre')
        # If the movie's genre matches, compute its average rating (if any)
        if movie_genre == genre:
            movie_ratings = ratings.get(m_name, [])
            if not movie_ratings:
                # no ratings — skip or treat as zero; here we skip
                continue
            # movie_ratings expected as list of (user_id, rating)
            # handle numeric rating or tuples
            vals = []
            for item in movie_ratings:
                if isinstance(item, (list, tuple)) and len(item) >= 2:
                    vals.append(float(item[1]))
                else:
                    # assume item is a numeric rating
                    try:
                        vals.append(float(item))
                    except Exception:
                        continue
            if vals:
                avg = sum(vals) / len(vals)
                genre_movies[m_name] = avg

    # sort movies by average rating descending, then by name for deterministic order
    sorted_movies = sorted(genre_movies.items(), key=lambda x: (-x[1], x[0]))
    # return only the movie names (top n)
    return [name for name, _ in sorted_movies[:n]]

# Genre popularity
# Return top n genres ranked by avg of avg movie ratings
def top_genres(n: int, movies: dict, ratings: dict) -> list:
    # Compute average rating per movie, group by genre, then average those averages
    genre_avgs = {}
    genre_counts = {}
    for m_name, info in movies.items():
        movie_genre = None
        if isinstance(info, (list, tuple)) and len(info) >= 2:
            movie_genre = info[1]
        elif isinstance(info, dict) and 'genre' in info:
            movie_genre = info.get('genre')
        if movie_genre is None:
            continue
        movie_ratings = ratings.get(m_name, [])
        nums = []
        for item in movie_ratings:
            if isinstance(item, (list, tuple)) and len(item) >= 2:
                try:
                    nums.append(float(item[1]))
                except Exception:
                    continue
            else:
                try:
                    nums.append(float(item))
                except Exception:
                    continue
        if nums:
            avg = sum(nums) / len(nums)
            genre_avgs[movie_genre] = genre_avgs.get(movie_genre, 0.0) + avg
            genre_counts[movie_genre] = genre_counts.get(movie_genre, 0) + 1
    genre_mean = {g: (genre_avgs[g] / genre_counts[g]) for g in genre_avgs}
    sorted_genres = sorted(genre_mean.items(), key=lambda x: (-x[1], x[0]))
    return [g for g, _ in sorted_genres[:n]]

# User preference for genre
# Return user's most preferred genre by the avg of avg ratings by user of movies in genre
def user_top_genre(user_id: str, movies: dict, ratings: dict) -> str:
    # Determine which genre the user gives highest average ratings to
    # Build per-genre list of ratings by the user
    genre_ratings = {}
    for m_name, user_ratings in ratings.items():
        # find user's rating for this movie
        for item in user_ratings:
            uid = None
            r = None
            if isinstance(item, (list, tuple)) and len(item) >= 2:
                uid, r = item[0], item[1]
            else:
                continue
            if str(uid) != str(user_id):
                continue
            # find genre
            info = movies.get(m_name)
            movie_genre = None
            if isinstance(info, (list, tuple)) and len(info) >= 2:
                movie_genre = info[1]
            elif isinstance(info, dict) and 'genre' in info:
                movie_genre = info.get('genre')
            if movie_genre is None:
                continue
            try:
                val = float(r)
            except Exception:
                continue
            genre_ratings.setdefault(movie_genre, []).append(val)
    # compute avg per genre
    best_genre = ''
    best_avg = -1
    for g, vals in genre_ratings.items():
        if not vals:
            continue
        avg = sum(vals) / len(vals)
        if avg > best_avg:
            best_avg = avg
            best_genre = g
    return best_genre

# Recommend movies
# Return 3 most popular movies from user's top genre that the user has not yet rated
def recommend_movies(user_id: str, movies: dict, ratings: dict) -> list:
    return []

