import base64
from dataclasses import dataclass

from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage

import config
from hardcover_client import get_reviews, HardcoverAPIException


if not config.OPENROUTER_API_KEY:
    raise ValueError("OPENROUTER_API_KEY not set.")


@dataclass
class Book:
    title: str
    authors: list[str]


def encode_image_to_base64(image_path: str) -> str:
    with open(image_path, "rb") as image_file:
        return base64.b64encode(image_file.read()).decode("utf-8")


def main():
    photo_path = input(str("Enter the path of the image: ")).strip('"')
    model = ChatOpenAI(
        api_key=config.OPENROUTER_API_KEY,
        base_url="https://openrouter.ai/api/v1",
        model="openrouter/free")
    book_model = model.with_structured_output(Book)
    message = HumanMessage(
        content=[
            {
                "type": "text",
                "text": (
                    "Identify the book from the image. "
                    "Return only the full title and authors."
                ),
            },
            {
                "type": "image_url",
                "image_url": {
                    "url": f"data:image/jpeg;base64,{encode_image_to_base64(photo_path)}",
                },
            },
        ]
    )
    book = Book(**book_model.invoke([message]))
    try:
        reviews = get_reviews(
            title=book.title,
            authors=book.authors,
        )
    except HardcoverAPIException:
        print("Sorry, I couldn't identify the book from this image.")
        exit(1)

    prompt = f"""
    Book:
    Title: {book.title}
    Authors: {", ".join(book.authors)}

    Reviews:
    {reviews}

    Analyze the reviews and write:
    - strengths;
    - weaknesses;
    - who should read this book.
    """

    response = model.invoke(prompt)
    print(response.content)


if __name__ == "__main__":
    main()
