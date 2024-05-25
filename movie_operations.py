import os
import typing as tp

import aiohttp
from data_classes import Movie
from googlesearch import search
from utils import (choose_apropriate_description, choose_apropriate_picture,
                   normalize)

headers = {"X-API-KEY": os.environ["KP_API_TOKEN"]}


async def get_movie_info_by_name(
    session: aiohttp.ClientSession, name: str
) -> tp.Optional[Movie]:
    """
    Retrieve movie information by name
    using an asynchronous HTTP request to the Kinopoisk API
    :param name: The name of the movie to search for
    :return: A Movie object containing information
    about the movie if found, or None if not found
    """

    query = normalize(name)
    params = {"query": query}
    async with session.get(
        "https://api.kinopoisk.dev/v1.4/movie/search",
        headers=headers,
        params=params,
    ) as response:
        if response.status == 200:
            data = await response.json()
            # if data['statusCode'] != 200:
            #     return None
            try:
                required_info = data["docs"][0]
                return (
                    Movie(
                        name=required_info["name"],
                        eng_name=required_info["alternativeName"],
                        genres=[genre["name"]
                                for genre in required_info["genres"]],
                        rating=required_info["rating"]["kp"],
                        description=choose_apropriate_description(
                            required_info["shortDescription"],
                            required_info["description"],
                        ),
                        picture_url=await choose_apropriate_picture(
                            session,
                            required_info["poster"]["url"],
                            required_info["backdrop"]["url"],
                        ),
                        crafted_link=f"https://vavada-qqq.com/#{required_info['id']}",
                        google_link="Ссылка пока не найдена",
                    )
                    if required_info["name"]
                    else None
                )
            except IndexError:
                try:
                    if data['statusCode'] == 403:
                        pass
                except Exception:
                    pass
                return None
        else:
            return None


async def get_movie_google_link_by_name(
    session: aiohttp.ClientSession, name: str
) -> str:
    """
    Get the Google search link for watching
    a movie online by its name.

    This function performs a Google search with
    the specified movie name to find a link
    for watching the movie online.

    :param session: An aiohttp ClientSession for making HTTP requests.
    :param name: The name of the movie to search for.
    :return: A first Google search result link for watching the movie online.
    """

    return await search(session, f"{name} +смотреть"
                        + "+онлайн", num_results=1).__anext__()
