from openai import OpenAI

import config
from hardcover_client import get_reviews


if config.OPENROUTER_API_KEY:
    raise ValueError("OPENROUTER_API_KEY not set.")


def main():
    client = OpenAI(api_key=config.OPENROUTER_API_KEY,
                    base_url="https://openrouter.ai/api/v1")



if __name__ == "__main__":
    main()
