# Standalone program, that saves all the required data in the database.
import os

import httpx
import asyncio

from httpx import Response

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

            # TODO: insertion logic

            page += 1

if __name__ == "__main__":
    asyncio.run(crawl_api())