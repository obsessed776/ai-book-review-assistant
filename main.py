from hardcover_client import get_reviews


def main():
    book_input = {
        "title": "Clean Code: A Handbook of Agile Software Craftsmanship",
        "authors": ["Robert C. Martin",]
    }
    reviews = get_reviews(**book_input)
    print(reviews)


if __name__ == "__main__":
    main()
