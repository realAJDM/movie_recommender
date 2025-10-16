# Implement the top_genres function
def top_genres(n: int, movies: dict, ratings: dict) -> list:
    genre_ratings = {}
    for movie_name, (movie_id, genre) in movies.items():
        if genre not in genre_ratings:
            genre_ratings[genre] = []
        if movie_name in ratings:
            genre_ratings[genre].extend([rating for user_id, rating in ratings[movie_name]])

    genre_avg_ratings = {}
    for genre, all_ratings in genre_ratings.items():
        if all_ratings:
            genre_avg_ratings[genre] = sum(all_ratings) / len(all_ratings)

    sorted_genres = sorted(genre_avg_ratings.items(), key=lambda item: item[1], reverse=True)
    return sorted_genres[:n]

# Test the top_genres function
print("\nTop 2 Genres:")
display(top_genres(2, movies_data, ratings_data)


        
# Implement the user_top_genre function
def user_top_genre(user_id: int, movies: dict, ratings: dict) -> str:
    user_ratings = {}
    for movie_name, movie_ratings in ratings.items():
        for uid, rating in movie_ratings:
            if uid == user_id:
                user_ratings[movie_name] = rating

    genre_user_ratings = {}
    for movie_name, rating in user_ratings.items():
        if movie_name in movies:
            movie_id, genre = movies[movie_name]
            if genre not in genre_user_ratings:
                genre_user_ratings[genre] = []
            genre_user_ratings[genre].append(rating)

    genre_avg_user_ratings = {}
    for genre, ratings_list in genre_user_ratings.items():
        if ratings_list:
            genre_avg_user_ratings[genre] = sum(ratings_list) / len(ratings_list)

    if not genre_avg_user_ratings:
        return "No genre preference found for this user."

    return max(genre_avg_user_ratings, key=genre_avg_user_ratings.get)
