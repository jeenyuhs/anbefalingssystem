# Standalone program, that saves all the required data in the database.
import os
from typing import Any

import httpx
import asyncio
from dotenv import load_dotenv
from httpx import Response

from constants.genres import Genres
from sqlalchemy.orm import sessionmaker, Session
from constants.providers import Providers
from models.cast import Actor, Cast
from models.movie import Movie
import settings
import state

load_dotenv()

BEARER_TOKEN = os.environ["BEARER_TOKEN"]
MAX_REQUESTS_PER_SECOND = 40

rate_limiter = asyncio.Semaphore(MAX_REQUESTS_PER_SECOND)


def determine_movie_genres(description: str, title: str) -> list[str]:
    """Use Claude AI to determine movie genres based on description and title."""
    message = state.claude.messages.create(
        model="claude-3-7-sonnet-20250219",
        max_tokens=500,
        temperature=1,
        system=(
            "You're an avid movie enjoyer and have the ability to precisely determine the genres of the movie. "
            "You can determine the genres of a movie, by its description and its title. \n"
            "The user will start by writing the description of a movie and then a new line with the movie title. "
            "It's your job to return the names of the primary genres and seperate them with \",\" and nothing else, "
            "so no space inbetween the seperators. Return a minimum of 4 genres, but there are no maximum limit of genres."
        ),
        messages=[
            {
                "role": "user",
                "content": [
                    {
                        "type": "text",
                        "text": f"{description}\n{title}"
                    }
                ]
            }
        ]
    )
    genres = message.content[0].text.split(",")
    return Genres.from_names(genres)


async def ratelimit_wrapper(client: httpx.AsyncClient, url: str) -> Response:
    """Rate limit wrapper for API requests."""
    async with rate_limiter:
        response = await client.get(
            url, 
            headers={"Authorization": f"Bearer {BEARER_TOKEN}", "accept": "application/json"}
        )
        await asyncio.sleep(1 / MAX_REQUESTS_PER_SECOND)
        return response


async def save_poster(client: httpx.AsyncClient, movie_id: int, path: str) -> None:
    """Save the movie poster to the local directory."""
    file_location = f"{settings.POSTER_DIRECTORY}/{movie_id}.png"

    if os.path.exists(file_location):
        print(f"Poster for movie {movie_id} already exists, skipping...")
        return

    path = f"https://image.tmdb.org/t/p/w220_and_h330_face/{path}"
    resp = await client.get(path)
    
    with open(file_location, "wb+") as f:
        f.write(resp.content)

    print(f"Saved poster for movie {movie_id}")


async def process_movie_providers(providers_data: dict[str, Any], movie: Movie) -> None:
    """Process and add streaming provider data to movie object."""
    if "DK" not in providers_data:
        return
        
    dk_providers = providers_data["DK"]
    provider_names = []

    # Flatten the providers dictionary and remove duplicates
    for category in ["buy", "rent", "flatrate", "free"]:
        if category in dk_providers:
            for provider in dk_providers[category]:
                provider_name = provider["provider_name"]
                
                # Add unique provider names
                if provider_name not in provider_names:
                    provider_names.append(provider_name)

    movie.available_on = Providers.from_names(provider_names)

async def process_movie_cast(
    client: httpx.AsyncClient, 
    session: Session, 
    movie_id_api: int, 
    movie_id_db: int
) -> None:
    """Process and add acting department information to the database."""
    actors_response = await ratelimit_wrapper(
        client, 
        f"https://api.themoviedb.org/3/movie/{movie_id_api}/credits"
    )
    actors_data = actors_response.json()
    
    for actor_data in actors_data["cast"]:
        if actor_data["known_for_department"] != "Acting":
            continue

        actor = session.query(Actor).filter(Actor.name == actor_data["name"]).first()
        if not actor:
            actor = Actor(name=actor_data["name"])
            session.add(actor)
            session.commit()

        existing_cast = (
            session.query(Cast)
            .filter(Cast.movie_id == movie_id_db)
            .filter(Cast.actor_id == actor.id)
            .first()
        )
        
        if not existing_cast:
            cast = Cast(
                movie_id=movie_id_db, 
                actor_id=actor.id, 
                character_name=actor_data["character"]
            )
            session.add(cast)
            session.commit()

async def process_new_movie(
    client: httpx.AsyncClient, 
    session: Session, 
    movie_data: dict[str, Any]
) -> Movie:
    """Process and add a new movie to the database."""
    # Get detailed movie information
    details_response = await ratelimit_wrapper(
        client, 
        f"https://api.themoviedb.org/3/movie/{movie_data['id']}"
    )
    details = details_response.json()

    try:
        movie = Movie.from_api(details)
    except Exception as e:
        print(f"Error creating movie from API: {e}")
        raise

    # Add genre information from AI analysis
    movie.genres = determine_movie_genres(
        description=movie.description,
        title=movie.title
    )

    # Find YouTube trailer
    videos_response = await ratelimit_wrapper(
        client,
        f"https://api.themoviedb.org/3/movie/{details['id']}/videos"
    )
    videos = videos_response.json()

    prioritized_id = ""
    for video in videos["results"]:
        if video["site"] != "YouTube":
            continue

        prioritized_id = video["key"]

        # Always prioritize the official trailer
        if video["official"]:
            break

    movie.youtube_trailer_id = prioritized_id

    # Get streaming providers
    providers_response = await ratelimit_wrapper(
        client,
        f"https://api.themoviedb.org/3/movie/{details['id']}/watch/providers"
    )
    await process_movie_providers(providers_response.json()["results"], movie)

    # Save to database
    session.add(movie)
    session.commit()

    # save poster in the background
    asyncio.create_task(save_poster(client, movie.id, details["poster_path"]))
    
    return movie

async def crawl_api():
    page = 1
    Session = sessionmaker(bind=state.engine)

    with Session() as session:
        async with httpx.AsyncClient() as client:
            # start with movies
            while True:
                MOVIES_ENDPOINT = f"https://api.themoviedb.org/3/movie/popular?language=en-US&page={page}"

                try:
                    response = await ratelimit_wrapper(client, MOVIES_ENDPOINT)
                    response.raise_for_status()
                except httpx.HTTPError as e:
                    # TODO: proper handling for when the API returns an error
                    print(e, "response failure")
                    break

                data = response.json()
                if not data or "results" not in data or len(data["results"]) == 0:
                    print("No data left.")
                    return

                for movie_data in data["results"]:
                    movie = (
                        session.query(Movie)
                        .filter(Movie.description == movie_data["overview"])
                        .filter(Movie.title == movie_data["title"])
                        .first()
                    )
                    # if the movie already exists in the database, use that
                    # and skip all of the details
                    if not movie:
                        try:
                            movie = await process_new_movie(client, session, movie_data)
                        except Exception as e:
                            print(f"Error processing new movie: {e}")
                            continue
                    else:
                        print("Movie already exists in the database, checking cast information...")
                
                    await process_movie_cast(
                        client,
                        session,
                        movie_data["id"],
                        movie.id
                    )

                page += 1

if __name__ == "__main__":
    asyncio.run(crawl_api())