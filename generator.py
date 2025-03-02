import os
import time
from typing import Any

import pandas as pd
import requests as req


BEARER_TOKEN = os.environ["BEARER_TOKEN"]

def authenticated_request(url: str) -> req.Response:
    return req.get(f"https://api.themoviedb.org/{url}", headers={"Authorization": f"Bearer {BEARER_TOKEN}", "accept": "application/json"})

def response_to_dataframe(data: dict[str, Any]) -> pd.DataFrame:
    return pd.DataFrame({
        "id": data["id"],
        "title": data["title"],
        "genre": [data["genre_ids"]],
        "rating": data["vote_average"],
        "ratings": data["vote_count"],
        "overview": data["overview"]
    })

def process_response(df: pd.DataFrame, response: req.Response) -> pd.DataFrame:
    data = response.json()
    try:
        results = data["results"]
    except Exception as e:
        print(e)
        print("somehting is wrong. waiting 30 seconds before continuing")
        print(response.text)
        time.sleep(30)
        return df
    
    for result in results:
        df = pd.concat([df, response_to_dataframe(result)])

    df.drop_duplicates(subset=["id"], inplace=True)

    return df

def run_generator() -> None:
    _initial_request = authenticated_request("3/movie/popular?language=en-US&page=1")
    df = process_response(pd.DataFrame({}, columns=["id", "title", "genre", "ratings", "rating"]), _initial_request)

    initial_request = _initial_request.json()
    total_pages = initial_request["total_pages"]
    
    # the api has a ratelimit of around 50 requests per second.
    ratelimit_timer = 0.2

    # the api has a max page on 500.
    for page in range(2, min(500, total_pages)):
        next_page_results = authenticated_request(f"3/movie/top_rated?language=en-US&page={page}")

        df = process_response(df, next_page_results)

        time.sleep(ratelimit_timer)

        if len(df) % 100 >= 80:
            print(df)

    df.to_csv("data/top_rated_movies_10000.csv")
    print("done")

if __name__ == "__main__":
    run_generator()