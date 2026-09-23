import os
import httpx
import time
from dotenv import load_dotenv

load_dotenv()

TMDB_TOKEN = os.getenv("TMDB_TOKEN")
TMDB_BASE_URL = os.getenv("TMDB_BASE_URL")

HEADERS = {
    "Authorization": f"Bearer {TMDB_TOKEN}",
    "accept": "application/json",
}


_genre_cache: dict[int, str] | None = None
_genre_cache_timestamp: float = 0
CACHE_TTL_SECONDS = 3600


def get_popular_movies(page: int = 1) -> list[dict]:
    response = httpx.get(
        f"{TMDB_BASE_URL}/movie/popular",
        headers=HEADERS,
        params={"page": page},
    )
    response.raise_for_status()
    return response.json()["results"]


def get_movie_detail(movie_id: int) -> dict:
    response = httpx.get(
        f"{TMDB_BASE_URL}/movie/{movie_id}",
        headers=HEADERS,
    )
    response.raise_for_status()
    return response.json()

def get_genre_map() -> dict[int, str]:
    global _genre_cache, _genre_cache_timestamp

    now = time.time()
    if _genre_cache is not None and (now - _genre_cache_timestamp) < CACHE_TTL_SECONDS:
        print("🟢 CACHE HIT — usando géneros ya guardados, sin llamar a TMDB")  # TEMP
        return _genre_cache

    print("🔴 CACHE MISS — llamando a TMDB por los géneros")  # TEMP

    response = httpx.get(
        f"{TMDB_BASE_URL}/genre/movie/list",
        headers=HEADERS,
    )
    response.raise_for_status()
    genres = response.json()["genres"]

    _genre_cache = {g["id"]: g["name"] for g in genres}
    _genre_cache_timestamp = now
    return _genre_cache