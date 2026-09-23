import strawberry
from tmdb_client import get_popular_movies, get_movie_detail, get_genre_map


@strawberry.type
class Genre:
    id: int
    name: str


@strawberry.type
class Movie:
    id: int
    title: str
    overview: str
    poster_path: str
    release_date: str
    genre_ids: strawberry.Private[list[int]]  # dato interno, no expuesto directo

    @strawberry.field
    def genres(self) -> list[Genre]:
        genre_map = get_genre_map()
        return [
            Genre(id=gid, name=genre_map[gid])
            for gid in self.genre_ids
            if gid in genre_map
        ]


def _extract_genre_ids(data: dict) -> list[int]:
    if "genres" in data:
        # formato del detalle: [{"id": ..., "name": ...}, ...]
        return [g["id"] for g in data["genres"]]
    # formato de la lista popular: [id, id, id]
    return data.get("genre_ids", [])
    

def _map_to_movie(data: dict) -> Movie:
    return Movie(
        id=data["id"],
        title=data["title"],
        overview=data["overview"],
        poster_path=data["poster_path"],
        release_date=data["release_date"],
        genre_ids=_extract_genre_ids(data),
    )


@strawberry.type
class Query:
    @strawberry.field
    def popular_movies(self, page: int = 1) -> list[Movie]:
        raw_movies = get_popular_movies(page)
        return [_map_to_movie(m) for m in raw_movies]

    @strawberry.field
    def movie_detail(self, movie_id: int) -> Movie:
        raw_movie = get_movie_detail(movie_id)
        return _map_to_movie(raw_movie)


schema = strawberry.Schema(query=Query)