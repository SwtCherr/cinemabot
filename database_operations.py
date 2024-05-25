import sqlite3

from data_classes import UserHistory, UserStats


def add_request_to_database(
    connection: sqlite3.Connection, cursor: sqlite3.Cursor,
    user_id: int, movie: str, date: int
) -> None:
    """
    Add a user's search request to the database
    :param user_id: The user's unique ID
    :param movie: The name of the movie being searched
    :param date: The timestamp of the request date
    """

    cursor.execute(
        "INSERT INTO Bebrabot_users (user_id, movie, date) VALUES (?, ?, ?)",
        (user_id, movie, date),
    )
    connection.commit()


def get_stats_by_user_id(cursor: sqlite3.Cursor, user_id: int) -> UserStats:
    """
    Retrieve statistics about a user's search requests,
    including the number of requests,
    requested movies, and favorite movie
    :param cursor: The database cursor
    :param user_id: The user's unique ID
    :return: UserStats object containing the user's statistics
    """

    cursor.execute(
        "SELECT movie, \
        COUNT(*) AS request_count \
        FROM Bebrabot_users \
        WHERE user_id=:user_id GROUP BY movie",
        {"user_id": user_id},
    )
    result = cursor.fetchall()
    num_requests = 0
    requested_movies = {}
    favourite_movie = ""
    favourite_movie_amount_of_requests = 0
    if result is not None:
        for row in result:
            requested_movies[row[0]] = row[1]
            num_requests += row[1]
            if row[1] > favourite_movie_amount_of_requests:
                favourite_movie_amount_of_requests = row[1]
                favourite_movie = row[0]
    return UserStats(
        num_requests=num_requests,
        requested_movies=requested_movies,
        favourite_movie=favourite_movie,
    )


def get_history_by_user_id(cursor: sqlite3.Cursor, user_id: int) -> UserHistory:
    """
    Retrieve the search history of a user,
    including requested movies and request dates.
    :param cursor: The database cursor.
    :param user_id: The user's unique ID.
    :return: UserHistory object containing the user's search history.
    """

    cursor.execute(
        "SELECT movie, date FROM Bebrabot_users WHERE user_id=:user_id",
        {"user_id": user_id},
    )
    result = cursor.fetchall()
    requests = []
    num_requests = 0
    if result is not None:
        for row in result:
            requests.append((row[1], row[0]))
            num_requests += 1
    return UserHistory(requests=requests, num_requests=num_requests)
