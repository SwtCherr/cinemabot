from dataclasses import dataclass


@dataclass
class Movie:
    """
    A data class representing movie information
    """

    name: str
    eng_name: str
    genres: list[str]
    rating: float
    description: str
    picture_url: str
    crafted_link: str
    google_link: str


@dataclass
class UserHistory:
    """
    A data class representing the history of user's movie requests
    """

    requests: list[tuple[str, int]]
    num_requests: int


@dataclass
class UserStats:
    """
    A data class representing statistics for a user's movie requests
    """

    num_requests: int
    requested_movies: dict[str, int]
    favourite_movie: str
