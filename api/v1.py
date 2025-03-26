from fastapi import APIRouter, Depends, HTTPException

from typing import Annotated

from sqlalchemy import select
from sqlalchemy.orm import Session

from models import get_session
from models.movie import Movie
from models.review import Review
from models.users import User
from models.cast import Cast, Actor

router = APIRouter()

@router.get("/movie/{movie_id}")
async def movie_by_id(movie_id: int, session: Annotated[Session, Depends(get_session)]):
    stmt = select(Movie)\
        .filter(Movie.id == movie_id)

    movie = session.execute(stmt).first()

    if not movie:
        raise HTTPException(status_code=404, detail="Movie not found")

    movie = movie[0]

    cast_stmt = select(Cast.character_name, Actor)\
        .join(Actor, Cast.actor_id == Actor.id)\
        .filter(Cast.movie_id == movie_id)

    cast = session.execute(cast_stmt).all()

    return {
        **movie.as_dict(),
        "cast": [
            {
                "character": character,
                **actor.as_dict()
            }
            for character, actor in cast
        ]
    }

@router.get("/movie/{movie_id}/reviews")
async def movie_reviews(movie_id: int, session: Annotated[Session, Depends(get_session)]):
    stmt = select(Review, User)\
        .join(User, Review.user_id == User.id)\
        .filter(Review.movie_id == movie_id)

    reviews = session.execute(stmt).all()

    if not reviews:
        raise HTTPException(status_code=404, detail="Either the movie doesn't exist or there aren't any reviews.")

    return [
        {
            **review.as_dict(),
            "user": user.as_dict()
        }
        for review, user in reviews
    ]

@router.get("/movie/{movie_id}/cast")
async def movie_cast(movie_id: int, session: Annotated[Session, Depends(get_session)]):
    stmt = select(Cast, Actor)\
        .join(Actor, Cast.actor_id == Actor.id)\
        .filter(Cast.movie_id == movie_id)

    cast = session.execute(stmt).all()

    if not cast:
        raise HTTPException(status_code=404, detail="Either the movie could not be found or there are no cast members")

    return [
        {
            "character": character,
            **actor.as_dict()
        }
        for character, actor in cast
    ]
