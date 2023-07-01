import os
from dotenv import load_dotenv
from rich.prompt import Prompt
from src.utils.display import (
    display_intro,
    select_number_of_posts,
    select_topic,
    select_search_queries,
)
from src.utils.agent import Agent
from src.utils.document_loader import RedditSubLoader, TwitterTweetLoader

load_dotenv()


def main():
    display_intro()
    topic = select_topic()
    platform, keywords, accounts = select_search_queries(topic)
    number_of_posts = select_number_of_posts()

    if platform == "reddit":
        document_loader = RedditSubLoader(
            number_submissions=number_of_posts,
            keywords=keywords,
            subreddits=accounts,
        )
    elif platform == "twitter":
        document_loader = TwitterTweetLoader.from_bearer_token(
            oauth2_bearer_token=os.environ.get("TWITTER_BEARER_TOKEN"),
            number_tweets=number_of_posts,
            twitter_users=accounts,
            keywords=keywords,
        )
    else:
        raise ValueError(f"Platform {platform} not supported")

    agent = Agent(loader=document_loader)

    agent.load_documents()
    agent.init_docsearch()
    structured_summary = agent.summarize()

    while True:
        input_question = Prompt.ask(
            f"[bold red]Ask the db to learn more about the extracted tweets  💬 (you can type q1, q2 or q3 as well) or type `q` to quit[/bold red]"
        )
        agent.ask_the_db(input_question, structured_summary)


if __name__ == "__main__":
    main()
