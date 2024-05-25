import re
import typing as tp

import aiohttp
from data_classes import Movie, UserHistory, UserStats


def normalize(data: str) -> str:
    """
    Normalize a string by converting it to lowercase,
    removing special characters, and collapsing whitespaces
    :param data: The input string to be normalized
    :return: normalized string
    """
    data = data.lower()
    data = re.sub(r"[^\w\s_]", "", data)
    data = data.strip()
    data = re.sub(r"[\s_]+", " ", data)
    return data


def say_hello() -> str:
    """
    Generate a greeting message.
    :return: A greeting message.
    """

    return "Привет, я Бэбработ! 👋 \n\n"


def search_failed() -> str:
    """
    Generate a message indicating a failed movie search
    :return: A message indicating that the movie search failed
    """

    return "Не удалось найти киношку 💔"


def no_requests_were_made() -> str:
    """
    Generate a message indicating that no movie requests have been made
    :return: A message indicating that no movie requests have been made
    """

    return (
        "Запросов по поиску фильмов пока не было 👺\n"
        + "\nДавай что-нибудь подберём 🔍"
    )


def get_functions_string() -> str:
    """
    Generate a message listing the functions of the bot
    :return: A message listing the functions of the bot
    """

    return (
        "🤓 Бэбработ умеет\n\n"
        + "👉 искать информацию о киношках по названию\n"
        + "👉 /start приступать к работе\n"
        + "👉 /help показывать свои способности\n"
        + "👉 /stats показывать статистику по поисковым запросам\n"
        + "👉 /history показывать историю поисковых запросов"
    )


def decline_stat_answer(num_request: int) -> str:
    """
    Generate a message based on the number of requests
    :param num_request: The number of requests
    :return: A message based on the number of requests
    """

    if num_request == 1:
        return f"Был выполнен всего {num_request} запрос 😢\n"
    if 2 <= num_request <= 4:
        return f"Всего было выполнено {num_request} поисковых запроса 😉\n"
    else:
        return f"Всего было выполнено {num_request} поисковых запросов 🤯\n"


def get_user_stats_string(user_stats: UserStats) -> str:
    """
    Generate a message displaying user statistics
    :param user_stats: User statistics data
    :return: A message displaying user statistics
    """

    if user_stats.num_requests:
        return (
            decline_stat_answer(user_stats.num_requests)
            + "\n_Искомые киношки:_\n"
            + "\n".join(
                [
                    f"🎬 {movie} {amount}"
                    for movie, amount
                    in list(user_stats.requested_movies.items())[-80:]
                ]
            )
            + f"\n\nПохоже, тебе нравится {user_stats.favourite_movie} 💫"
        )
    else:
        return no_requests_were_made()


def get_user_history_string(user_history: UserHistory) -> str:
    """
    Generate a message displaying user search history
    :param user_history: User search history data
    :return: A message displaying user search history
    """

    if user_history.num_requests:
        return (
            decline_stat_answer(user_history.num_requests)
            + "\n_Искомые киношки:_\n"
            + "\n".join(
                [
                    f"🎞 {request[0]} {request[1]}"
                    for request in user_history.requests[-80:]
                ]
            )
        )
    else:
        return no_requests_were_made()


def get_movie_string(movie: Movie) -> str:
    """
    Generate a message displaying movie information
    :param movie: Movie information data
    :return: A message displaying movie information
    """

    return (
        f"🍿 {movie.name} \n"
        + "\n👉 Жанр: "
        + ", ".join([f"{genre}" for genre in movie.genres])
        + "\n👉 Рейтинг на Кинопоиске: "
        + f"{movie.rating:.1f}"
        + "\n👉 Описание: "
        + f"{movie.description}"
        + f"\n👉 Ссылка на просмотр: {movie.crafted_link}"
        + f"\n👉 Ещё одна: {movie.google_link}"
    )


def choose_apropriate_description(short_description: str,
                                  full_description: str) -> str:
    """
    Choose an appropriate movie description to fit
    within the character limit of a Telegram message

    This function first checks if a short description
    is provided. If it's available and within the character limit,
    it's returned. Otherwise, it considers the full description
    and truncates it to fit within the character limit
    without splitting words

    :param short_description: A short movie description
    :param full_description: A full movie description
    :return: An appropriate movie description that fits
    within the character limit
    """

    if short_description:
        returned_description = short_description
    else:
        returned_description = full_description
    if len(returned_description) < 800:
        return returned_description
    else:
        last_space_index = returned_description.find(". ", 500, 800)
        return returned_description[:last_space_index] + "..."


async def choose_apropriate_picture(
    session: aiohttp.ClientSession, poster_url: str, backdrop_url: str
) -> tp.Optional[str]:
    """
    Choose an appropriate picture URL between
    the poster and backdrop URLs based on their file size

    This function checks the content length of
    both URLs and returns the poster URL
    if its file size is smaller than or
    equal to 7,345,728 bytes (7 MB). Otherwise, it returns
    the backdrop URL

    :param poster_url: The URL of the movie's poster image
    :param backdrop_url: The URL of the movie's backdrop image
    :return: The selected image URL (poster or backdrop) based on file size
    """

    async with session.head(poster_url) as response:
        content_length = response.headers.get("Content-Length")
        if content_length is not None:
            if int(content_length) <= 7345728:
                return poster_url
            else:
                return backdrop_url
        else:
            return None
