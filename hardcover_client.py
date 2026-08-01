import os
from typing import Any
from dataclasses import dataclass
from datetime import date

import requests

import config

if not config.HARDCOVER_API_KEY:
    raise ValueError("HARDCOVER_API_KEY not set.")

HARDCOVER_BASE_URL = "https://api.hardcover.app/v1/graphql"
HARDCOVER_HEADERS = {
    "Content-Type": "application/json",
    "Authorization": f"Bearer {config.HARDCOVER_API_KEY}",
}


class HardcoverAPIException(Exception):
    pass


@dataclass
class Review:
    reviewed_at: date
    text: str
    rating: float


DEFAULT_LIMIT = 10


def get_reviews(title: str, authors: list[str]) -> list[Review]:
    """Returns reviews for a book by its title and authors."""
    with requests.Session() as session:
        session.headers.update(HARDCOVER_HEADERS)
        book_id = _get_book_id(title, authors, session)
        return _get_book_reviews_by_id(book_id, session)


def _get_book_reviews_by_id(book_id: int, session: requests.Session) -> list[Review]:
    query = """
    query BookReviews($bookId: Int!, $limit: Int!) {
        user_books(
        where: {
            book_id: {_eq: $bookId}
            has_review: {_eq: true}
        }
        limit: $limit
        ) {
            review
            rating
            reviewed_at
            user {
                username
            }
        }
    }
    """
    data = _graphql_request(query=query, variables={"bookId": book_id, "limit": DEFAULT_LIMIT}, session=session)
    return [
        Review(
            text=item["review"],
            rating=item["rating"],
            reviewed_at=_parse_date(item["reviewed_at"])
        )
        for item in data["user_books"]
    ]


def _get_book_id(title: str, authors: list[str], session: requests.Session) -> int:
    query = """
    query BookId($title: String!,  $authors: [String!]!) {
        books(
            where: {
                title: {_eq: $title}
                contributions: {
                author: {
                    name: {_in: $authors}
                }
            }
        }
            limit: 1
            order_by: {users_count: desc}
        ) {
            id
        }
    }
    """
    book_data = _graphql_request(
        query,
        {"title": title,
         "authors": authors
         },
        session
    )
    books = book_data["books"]

    if not books:
        raise HardcoverAPIException(f"Book not found: {title=} {authors=}")

    return int(books[0]["id"])


def _graphql_request(query: str, variables: dict[str, Any], session: requests.Session) -> dict[str, Any]:
    response = session.post(
        HARDCOVER_BASE_URL,
        json={
            "query": query,
            "variables": variables,
        },
    )
    response.raise_for_status()
    result = response.json()

    if errors := result.get("errors"):
        raise HardcoverAPIException(
            f"GraphQL error: {errors}"
        )

    return result["data"]


def _parse_date(value: str | None) -> date | None:
    if not value:
        return None

    return date.fromisoformat(value[:10])
