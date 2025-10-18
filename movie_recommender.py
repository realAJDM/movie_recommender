from collections import defaultdict
import logging
from collections import defaultdict
from typing import Dict, List, Tuple

# Load datasets
movies = ['movie_genre', 'movie_id', 'movie_name']
ratings = ['movie_name', 'rating', 'user_id']

# Load movies from file. Return dict mapping movie_name -> (movie_id, movie_genre)
def load_movies(filename: str) -> dict:
    """
    Loads movie data from a file, standardizing all keys to lowercase.

    Args:
        filename: The path to the movies data file. The expected format per line is
                  'movie_genre|movie_id|movie_name'.

    Returns:
        A dictionary mapping each movie_name (in lowercase) to a tuple 
        containing its (movie_id, movie_genre in lowercase).
    """
    movie_data = {}
    try:
        with open(filename, 'r', encoding='utf-8') as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                
                parts = line.split('|', 2)
                if len(parts) == 3:
                    genre, movie_id, movie_name = parts
                    # Convert genre and movie_name to lowercase
                    # to ensure case-insensitivity.
                    movie_data[movie_name.lower()] = (movie_id, genre.lower())
    except FileNotFoundError:
        print(f"Error: The file '{filename}' was not found.")
    except Exception as e:
        print(f"An error occurred while reading {filename}: {e}")
    return movie_data


def load_ratings(filename: str) -> dict:
    """
    Loads movie ratings from a file, standardizing movie names to lowercase.

    Args:
        filename: The path to the ratings data file. The expected format per line is
                  'movie_name|rating|user_id'.

    Returns:
        A dictionary mapping each movie_name (in lowercase) to a list of 
        (user_id, rating) tuples.
    """
    ratings_data = defaultdict(list)
    try:
        with open(filename, 'r', encoding='utf-8') as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                
                parts = line.split('|')
                if len(parts) == 3:
                    movie_name, rating_str, user_id = parts
                    try:
                        rating = float(rating_str)
                        if 0 <= rating <= 5:
                            # Use movie_name.lower() as the key.
                            ratings_data[movie_name.lower()].append((user_id, rating))
                        else:
                            print(f"Warning: Rating '{rating}' for movie '{movie_name}' is outside the valid range (0-5). Skipping line.")
                    except ValueError:
                        print(f"Warning: Could not parse rating '{rating_str}' for movie '{movie_name}'. Skipping line.")
    except FileNotFoundError:
        print(f"Error: The file '{filename}' was not found.")
    except Exception as e:
        print(f"An error occurred while reading {filename}: {e}")
    return dict(ratings_data)
# Movie popularity
# Return top n movies ranked by avg rating
def top_movies(n: int, ratings: dict) -> list:
    """
    Finds the top n movies ranked by average rating.

    Args:
        n: The number of top movies to return.
        ratings: A dictionary mapping movie names to a list of (user_id, rating) tuples.

    Returns:
        A list of tuples, where each tuple contains (movie_name, average_rating),
        sorted in descending order of average rating. In case of a tie, movies
        are sorted alphabetically by name.
    """
    if n <= 0:
        return []
    
    avg_ratings = {}
    for movie_name, user_ratings in ratings.items():
        if not user_ratings:
            print(f"Warning: Movie '{movie_name}' has no ratings. Skipping.")
            continue
        total_rating = sum(rating for user_id, rating in user_ratings)
        avg_ratings[movie_name] = total_rating / len(user_ratings)

    sorted_movies = sorted(avg_ratings.items(), key=lambda item: (-item[1], item[0]))
    return sorted_movies[:n]

def top_movies_in_genre(n: int, genre: str, movies: MoviesDict, ratings: RatingsDict) -> List[str]:
    """Return the top-n movies in a given genre ranked by average rating.

    Args:
        n: number of movies to return
        genre: genre string to filter by (exact match)
        movies: mapping movie_name -> (movie_id, movie_genre)
        ratings: mapping movie_name -> list of (user_id, rating)

    Returns:
        list of top-n movie names in the genre
    """
    genre_movies = {}
    for m_name, info in movies.items():
        movie_genre = None
        if isinstance(info, (list, tuple)) and len(info) >= 2:
            movie_genre = info[1]
        elif isinstance(info, dict) and 'genre' in info:
            movie_genre = info.get('genre')
        if movie_genre == genre:
            movie_ratings = ratings.get(m_name, [])
            if not movie_ratings:
                continue
            vals = []
            for item in movie_ratings:
                if isinstance(item, (list, tuple)) and len(item) >= 2:
                    try:
                        vals.append(float(item[1]))
                    except Exception:
                        continue
                else:
                    try:
                        vals.append(float(item))
                    except Exception:
                        continue
            if vals:
                avg = sum(vals) / len(vals)
                genre_movies[m_name] = avg
    sorted_movies = sorted(genre_movies.items(), key=lambda x: (-x[1], x[0]))
    return [name for name, _ in sorted_movies[:n]]


def top_genres(n: int, movies: MoviesDict, ratings: RatingsDict) -> List[str]:
    """Return the top-n genres ranked by the average of average movie ratings per genre.

    Args:
        n: number of genres to return
        movies: mapping movie_name -> (movie_id, movie_genre)
        ratings: mapping movie_name -> list of (user_id, rating)

    Returns:
        list of top-n genres
    """
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


def user_top_genre(user_id: str, movies: MoviesDict, ratings: RatingsDict) -> str:
    """Return the genre that the given user prefers (highest average rating by user for movies in that genre).

    Args:
        user_id: id of the user (string)
        movies: mapping movie_name -> (movie_id, movie_genre)
        ratings: mapping movie_name -> list of (user_id, rating)

    Returns:
        genre string the user prefers, or empty string if no data
    """
    genre_ratings = {}
    for m_name, user_ratings in ratings.items():
        for item in user_ratings:
            uid = None
            r = None
            if isinstance(item, (list, tuple)) and len(item) >= 2:
                uid, r = item[0], item[1]
            else:
                continue
            if str(uid) != str(user_id):
                continue
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


def recommend_movies(user_id: str, movies: MoviesDict, ratings: RatingsDict) -> List[str]:
    """Recommend up to 3 movies: most popular movies from the user's favorite genre that the user has not rated yet.

    Args:
        user_id: id of the user (string)
        movies: mapping movie_name -> (movie_id, movie_genre)
        ratings: mapping movie_name -> list of (user_id, rating)

    Returns:
        list of up to 3 recommended movie names
    """
    fav = user_top_genre(user_id, movies, ratings)
    if not fav:
        return []
    rated = set()
    for m_name, user_ratings in ratings.items():
        for item in user_ratings:
            if isinstance(item, (list, tuple)) and len(item) >= 2:
                if str(item[0]) == str(user_id):
                    rated.add(m_name)
    candidates = top_movies_in_genre(50, fav, movies, ratings)
    recs = [m for m in candidates if m not in rated]
    return recs[:3]


def _menu_load_data(state: dict):
    movies_file = input('Path to movies file (default movies.txt): ').strip() or 'movies.txt'
    ratings_file = input('Path to ratings file (default ratings.txt): ').strip() or 'ratings.txt'
    state['movies'] = load_movies(movies_file)
    state['ratings'] = load_ratings(ratings_file)


def _menu_top_movies(state: dict):
    n = int(input('How many top movies? (n): '))
    res = top_movies(n, state.get('ratings', {}))
    print('\nTop movies:')
    for i, m in enumerate(res, 1):
        print(f"{i}. {m}")


def _menu_top_movies_in_genre(state: dict):
    genre = input('Genre: ').strip()
    n = int(input('How many top movies in this genre? (n): '))
    res = top_movies_in_genre(n, genre, state.get('movies', {}), state.get('ratings', {}))
    print(f'\nTop {n} movies in {genre}:')
    for i, m in enumerate(res, 1):
        print(f"{i}. {m}")


def _menu_top_genres(state: dict):
    n = int(input('How many top genres? (n): '))
    res = top_genres(n, state.get('movies', {}), state.get('ratings', {}))
    print('\nTop genres:')
    for i, g in enumerate(res, 1):
        print(f"{i}. {g}")


def _menu_user_top_genre(state: dict):
    user = input('User id: ').strip()
    res = user_top_genre(user, state.get('movies', {}), state.get('ratings', {}))
    print(f"\nUser {user} top genre: {res}")


def _menu_recommend(state: dict):
    user = input('User id: ').strip()
    res = recommend_movies(user, state.get('movies', {}), state.get('ratings', {}))
    print(f"\nRecommendations for user {user}:")
    if not res:
        print('  (no recommendations)')
    for i, m in enumerate(res, 1):
        print(f"{i}. {m}")


def main():
    state = {'movies': {}, 'ratings': {}}
    actions = [
        ('Load data files', _menu_load_data),
        ('Top n movies (overall)', _menu_top_movies),
        ('Top n movies in genre', _menu_top_movies_in_genre),
        ('Top n genres', _menu_top_genres),
        ('User top genre', _menu_user_top_genre),
        ('Recommend movies for user', _menu_recommend),
        ('Exit', None),
    ]
    while True:
        print('\nMovie Recommender CLI')
        for i, (label, _) in enumerate(actions, 1):
            print(f"{i}. {label}")
        try:
            choice = int(input('Choose an option: ').strip())
        except Exception:
            print('Invalid choice')
            continue
        if choice < 1 or choice > len(actions):
            print('Invalid choice')
            continue
        if actions[choice - 1][0] == 'Exit':
            print('Goodbye')
            break
        handler = actions[choice - 1][1]
        try:
            handler(state)
        except Exception as e:
            logging.exception('Error executing action: %s', e)


if __name__ == '__main__':
    main()
