import os
from rich.console import Console
from functools import lru_cache
import praw
from langchain.document_loaders import RedditPostsLoader
from src.common.spinner import Spinner
from src.reddit import logger

console = Console()


@lru_cache()
def get_reddit_client():
    reddit = praw.Reddit(
        client_id=os.environ.get("REDDIT_CLIENT_ID"),
        client_secret=os.environ.get("REDDIT_CLIENT_SECRET"),
        user_agent=os.environ.get("USER_AGENT"),
    )
    return reddit


def get_top_subreddits(
    query,
    top_k=20,
    min_sub_count=-1,
):
    """Get subreddits that correspond to a specific query (e.g. Bitcoin) and have at least min_sub_count subs"""
    reddit = get_reddit_client()

    subreddits = reddit.subreddits.search(query=query, limit=top_k)
    subreddits_with_subs_counts = [
        (subreddit.display_name, subreddit.subscribers) for subreddit in subreddits
    ]

    subreddits_with_subs_counts = [
        (c[0], c[1]) for c in subreddits_with_subs_counts if c[1] is not None
    ]

    subreddits_with_subs_counts = sorted(
        subreddits_with_subs_counts,
        key=lambda t: t[1],
        reverse=True,
    )
    subreddits_with_subs_counts = [
        c for c in subreddits_with_subs_counts if c[1] > min_sub_count
    ]
    subreddits = [c[0] for c in subreddits_with_subs_counts]
    counts = [c[1] for c in subreddits_with_subs_counts]
    return subreddits, counts


def load_reddit_posts(display_names, number_posts=10):
    loader = RedditPostsLoader(
        client_id=os.environ.get("REDDIT_CLIENT_ID"),
        client_secret=os.environ.get("REDDIT_CLIENT_SECRET"),
        user_agent=os.environ.get("USER_AGENT"),
        categories=["hot"],
        mode="subreddit",
        search_queries=display_names,
        number_posts=number_posts,
    )

    with Spinner(text_message="Loading Reddit documents"):
        documents = loader.load()

    logger.info({"msg": f"{len(documents)} are loaded ..."})
    return documents


def get_document_text(doc):
    post_title = doc.metadata["post_title"]
    page_content = doc.page_content
    document_text = post_title + "\n\n" + page_content
    return document_text


def get_metadatas_from_documents(documents):
    metadatas = [document.metadata for document in documents]
    for metadata in metadatas:
        metadata["source"] = metadata["post_id"]

    for metadata in metadatas:
        metadata["post_author"] = str(metadata["post_author"])
    return metadatas


def get_texts_from_documents(documents):
    texts = [get_document_text(document) for document in documents]
    return texts


def display_bot_answer(result, collection):
    console.print("Answer :", style="red bold underline")
    console.print(result["answer"], style="yellow")

    sources = result["sources"]
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
