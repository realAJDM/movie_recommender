# Load datasets
movies = ['movie_genre', 'movie_id', 'movie_name']
ratings = ['movie_name', 'rating', 'user_id']

# Load movies from file. Return dict mapping movie_name -> (movie_id, movie_genre)
def load_movies(filename: str) -> dict:
    return {}

# Load ratings. Return dict mapping movie_name -> list of (user_id, rating)
#!/usr/bin/env python3
"""movie_recommender.py

Small movie recommender CLI implementing the following features:
- top_movies: top-n movies by average rating
- top_movies_in_genre: top-n movies in a genre by average rating
- top_genres: top-n genres by average of movie averages
- user_top_genre: user's most preferred genre
- recommend_movies: 3 most popular movies from user's top genre that the user hasn't rated

Usage:
    python movie_recommender.py

The program provides a simple text menu to load data files and run each function.

Input files expected (pipe-delimited):
- movies.txt: movie_genre|movie_id|movie_name
- ratings.txt: movie_name|rating|user_id

This script focuses on correctness and reasonable input validation (skips malformed lines, logs warnings).
"""

import csv
import logging
import os
import sys
from collections import defaultdict
from typing import Dict, List, Tuple

# Configure logging
logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")

# Types
MoviesDict = Dict[str, Tuple[str, str]]  # movie_name -> (movie_id, genre)
RatingsDict = Dict[str, List[Tuple[str, float]]]  # movie_name -> list of (user_id, rating)


def load_movies(filename: str) -> MoviesDict:
    """Parse a pipe-delimited movies file and return a mapping of movie_name -> (movie_id, genre).

    Expected header: movie_genre|movie_id|movie_name

    The function handles quoted movie names, strips whitespace, and logs/ignores malformed lines.
    Movie names are used as keys (stripped). movie_id is converted to int when possible.

    Args:
        filename: path to the movies file

    Returns:
        dict mapping movie_name to (movie_id, genre)
    """
    res: MoviesDict = {}
    if not os.path.exists(filename):
        logging.error("movies file not found: %s", filename)
        return res
    with open(filename, newline='', encoding='utf-8', errors='replace') as f:
        reader = csv.reader(f, delimiter='|', quotechar='"')
        header = next(reader, None)
        for row_no, row in enumerate(reader, start=2):
            if len(row) < 3:
                logging.warning("movies: skipping malformed line %d: %r", row_no, row)
                continue
            genre, mid, name = row[0].strip(), row[1].strip(), row[2].strip()
            if not name:
                logging.warning("movies: empty movie name at line %d", row_no)
                continue
            try:
                mid_val = int(mid)
            except Exception:
                mid_val = mid
            res[name] = (mid_val, genre)
    logging.info("Loaded %d movies from %s", len(res), filename)
    return res


def load_ratings(filename: str) -> RatingsDict:
    """Parse a pipe-delimited ratings file and return a mapping of movie_name -> list of (user_id, rating).

    Expected header: movie_name|rating|user_id

    The function handles quoted movie names, ignores malformed lines and non-numeric ratings, and logs warnings.

    Args:
        filename: path to the ratings file

    Returns:
        dict mapping movie_name to list of (user_id, rating)
    """
    res: RatingsDict = {}
    if not os.path.exists(filename):
        logging.error("ratings file not found: %s", filename)
        return res
    with open(filename, newline='', encoding='utf-8', errors='replace') as f:
        reader = csv.reader(f, delimiter='|', quotechar='"')
        header = next(reader, None)
        for row_no, row in enumerate(reader, start=2):
            if len(row) < 3:
                logging.warning("ratings: skipping malformed line %d: %r", row_no, row)
                continue
            name, rating_str, user_id = row[0].strip(), row[1].strip(), row[2].strip()
            if not name:
                logging.warning("ratings: empty movie name at line %d", row_no)
                continue
            try:
                rating = float(rating_str)
            except Exception:
                logging.warning("ratings: bad rating at line %d: %r", row_no, rating_str)
                continue
            # Optional: enforce rating range 0-5
            if not (0.0 <= rating <= 5.0):
                logging.warning("ratings: out-of-range rating at line %d: %r", row_no, rating)
                continue
            res.setdefault(name, []).append((user_id, rating))
    total = sum(len(v) for v in res.values())
    logging.info("Loaded %d ratings for %d movies from %s", total, len(res), filename)
    return res


def top_movies(n: int, ratings: RatingsDict) -> List[str]:
    """Return the top-n movie names ranked by average rating.

    Args:
        n: number of top movies to return
        ratings: mapping movie_name -> list of (user_id, rating)

    Returns:
        list of top-n movie names (strings)
    """
    averages = {}
    for m, vals in ratings.items():
        nums = []
        for item in vals:
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
            averages[m] = sum(nums) / len(nums)
    sorted_movies = sorted(averages.items(), key=lambda x: (-x[1], x[0]))
    return [name for name, _ in sorted_movies[:n]]


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

