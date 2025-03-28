# Standalone program, that saves all the required data in the database.
import os

import httpx
import asyncio
from dotenv import load_dotenv
from httpx import Response

from models.movie import Movie

load_dotenv()

BEARER_TOKEN = os.environ["BEARER_TOKEN"]
MAX_REQUESTS_PER_SECOND = 40

rate_limiter = asyncio.Semaphore(MAX_REQUESTS_PER_SECOND)

async def ratelimit_wrapper(client: httpx.AsyncClient, url: str) -> Response:
    async with rate_limiter:
        response = await client.get(url, headers={
            "Authorization": f"Bearer {BEARER_TOKEN}", "accept": "application/json"
        })
        await asyncio.sleep(1 / MAX_REQUESTS_PER_SECOND)  # Enforce rate limit
        return response

async def crawl_api():
    page = 1

    async with httpx.AsyncClient() as client:
        while True:
            url = f"https://api.themoviedb.org/3/movie/popular?language=en-US&page={page}"

            try:
                response = await ratelimit_wrapper(client, url)
                response.raise_for_status()
            except httpx.HTTPError as _:
                # TODO: proper handling for when the API returns an error
                return

            data = response.json()

            if not data or len(data) == 0:
                break

            for movie in data["results"]:
                serialized_movie = Movie.from_api(movie)
                print(serialized_movie.__dict__)

                # TODO: Get movie cast

            page += 1

if __name__ == "__main__":
    asyncio.run(crawl_api())