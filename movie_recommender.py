import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np

# Load datasets
movies = ['movie_genre', 'movie_id', 'movie_name']
ratings = ['movie_name', 'rating', 'user_id']

# Load movies from file. Return dict mapping movie_name -> (movie_id, movie_genre)
def load_movies(filename: str) -> dict:

# Load ratings. Return dict mapping movie_name -> list of (user_id, rating)
def load_ratings(filename: str) -> dict:

# Movie popularity
# Return top n movies ranked by avg rating
def top_movies(n: int, ratings: dict) -> list:

# Movie popularity in genre
# Return top n movies in genre by avg rating
def top_movies_in_genre(n: int, genre: str, movies: dict, ratings: dict) -> list:

# Genre popularity
# Return top n genres ranked by avg of avg movie ratings
def top_genres(n: int, movies: dict, ratings: dict) -> list:

# User preference for genre
# Return user's most preferred genre by the avg of avg ratings by user of movies in genre
def user_top_genre(user_id: str, movies: dict, ratings: dict) -> str:

# Recommend movies
# Return 3 most popular movies from user's top genre that the user has not yet rated
def recommend_movies(user_id: str, movies: dict, ratings: dict) -> list:

    
