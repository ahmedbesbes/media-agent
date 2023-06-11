import os
from functools import lru_cache
import tweepy
from rich.console import Console

console = Console()


@lru_cache(maxsize=None)
def get_api():
    auth = tweepy.OAuth2BearerHandler(os.environ.get("TWITTER_BEARER_TOKEN"))
    api = tweepy.API(auth, parser=tweepy.parsers.JSONParser())
    return api


def get_document_text(doc):
    document_text = doc.page_content
    return document_text


def get_metadatas_from_documents(documents):
    metadatas = [document.metadata for document in documents]

    sources = []
    for metadata in metadatas:
        metadata["source"] = metadata["tweet_id"]
        metadata.pop("user_info")
        metadata.pop("tweet_id")
        sources.append(metadata["source"])

    return metadatas


def get_texts_from_documents(documents):
    texts = [get_document_text(document) for document in documents]
    return texts


def display_bot_answer(result, collection):
    console.print("Answer :", style="red bold underline")
    console.print(result["answer"], style="yellow")

    sources = result["sources"]

    print("sources : ")
    console.print(sources)

    sources = sources.split(",")
    sources = [source.strip() for source in sources]

    if len(sources) == 1:
        output = collection.get(
            where={"source": sources[0]},
            include=["metadatas", "documents"],
        )
    else:
        output = collection.get(
            where={"$or": [{"source": {"$eq": source}} for source in sources]},
            include=["metadatas"],
        )

    console.print("These are sources I used to create my answer:")
    console.print(output["metadatas"])


def search_users(q, count):
    api = get_api()
    users = api.search_users(q=q, count=count)
    extracted_users = []

    for user in users:
        screen_name = user["screen_name"]
        followers_count = user["followers_count"]
        statuses_count = user["statuses_count"]
        description = user["description"]
        profile_url = f"https://twitter/{screen_name}"
        lang = user["lang"]

        extracted_user = dict(
            screen_name=screen_name,
            profile_url=profile_url,
            description=description,
            followers_count=followers_count,
            statuses_count=statuses_count,
            lang=lang,
        )
        extracted_users.append(extracted_user)

    return extracted_users
