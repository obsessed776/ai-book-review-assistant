from hardcover_client import get_reviews


if not config.OPENROUTER_API_KEY:
    raise ValueError("OPENROUTER_API_KEY not set.")


def encode_image_to_base64(image_path: str) -> str:
    with open(image_path, "rb") as image_file:
        return base64.b64encode(image_file.read()).decode("utf-8")


def main():
    model = ChatOpenAI(
        api_key=config.OPENROUTER_API_KEY,
        base_url="https://openrouter.ai/api/v1",
        model="openrouter/free")
    agent = create_agent(model, tools=[get_reviews,])
    message = HumanMessage(
        content=[
            {
                "type": "text",
                "text": "Определи название книги и автора. Если получилось — вызови get_reviews.",
            },
            {
                "type": "image_url",
                "image_url": {
                    "url": f"data:image/jpeg;base64,{encode_image_to_base64("clean_code.webp")}",
                },
            },
        ]
    )

    result = agent.invoke({"messages": [message]}) # type: ignore
    print(result)


if __name__ == "__main__":
    main()
