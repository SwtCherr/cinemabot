import asyncio
import logging
import os
import sqlite3
import sys

import aiohttp
from aiogram import Bot, Dispatcher, types
from aiogram.enums import ParseMode
from aiogram.filters.command import Command
from database_operations import (add_request_to_database,
                                 get_history_by_user_id, get_stats_by_user_id)
from movie_operations import (get_movie_google_link_by_name,
                              get_movie_info_by_name)
from utils import (get_functions_string, get_movie_string,
                   get_user_history_string, get_user_stats_string, say_hello,
                   search_failed)

connection = None
cursor = None
session = None
dp = Dispatcher()


@dp.message(Command("start"))
async def send_welcome(message: types.Message) -> None:
    """
    Send a welcome message to the user when they start the conversation
    :param message: The message object representing the user's command
    """

    await message.reply(say_hello() +
                        get_functions_string(), parse_mode="Markdown")


@dp.message(Command("help"))
async def send_help(message: types.Message) -> None:
    """
    Send a message containing information
    about available commands and functionality
    :param message: The message object representing the user's command
    """

    await message.reply(get_functions_string(), parse_mode="Markdown")


@dp.message(Command("stats"))
async def send_stats(message: types.Message) -> None:
    """
    Send statistics about the user's search requests,
    including the number of requests,
    requested movies, and favorite movie
    :param message: The message object representing the user's command
    """
    if message.from_user is not None:
        user_stats = get_stats_by_user_id(cursor=cursor,
                                          user_id=message.from_user.id)
        await message.reply(get_user_stats_string(user_stats),
                            parse_mode="Markdown")


@dp.message(Command("history"))
async def send_history(message: types.Message) -> None:
    """
    Send the user's search history, including the list
    of requested movies and the number of requests
    :param message: The message object representing the user's command
    """

    if message.from_user is not None:
        user_history = get_history_by_user_id(cursor=cursor,
                                              user_id=message.from_user.id)
        await message.reply(get_user_history_string(user_history),
                            parse_mode="Markdown")


@dp.message()
async def send_cinema(message: types.Message) -> None:
    """
    Handle user requests to search for movie information
    and reply with movie details or a search failed message
    :param message: The message object representing the name of movie
    """
    if message.from_user is not None:
        movie = await get_movie_info_by_name(session=session, name=message.text)
        if movie is not None:
            movie.google_link = await get_movie_google_link_by_name(
                session=session, name=movie.eng_name
            )
        if movie is not None and movie.picture_url:
            add_request_to_database(
                connection=connection,
                cursor=cursor,
                user_id=message.from_user.id,
                movie=movie.name,
                date=message.date,
            )
            await message.reply_photo(
                types.URLInputFile(movie.picture_url),
                caption=get_movie_string(movie),
            )
        else:
            await message.reply(search_failed())


async def main() -> None:
    """
    The main entry point for the Bebrabot Telegram bot.
    This function initializes the SQLite database,
    creates the necessary table if it doesn't exist,
    sets up an aiohttp ClientSession for HTTP requests,
    and starts the bot's polling loop
    """
    global session, connection, cursor

    connection = sqlite3.connect("bot_users_database.db")
    cursor = connection.cursor()

    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS Bebrabot_users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER NOT NULL,
        movie TEXT NOT NULL,
        date INTEGER NOT NULL
        )
        """
    )
    connection.commit()

    async with aiohttp.ClientSession() as http_session:
        session = http_session
        bot = Bot(os.environ["BOT_TOKEN"], parse_mode=ParseMode.MARKDOWN)
        await dp.start_polling(bot)


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, stream=sys.stdout)
    asyncio.run(main())
    if cursor is not None:
        cursor.close()
    if connection is not None:
        connection.close()
