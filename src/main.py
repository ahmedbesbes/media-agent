import os
from dotenv import load_dotenv
from rich.prompt import Prompt
from src.utils.display import (
    display_intro,
    select_number_of_posts,
    select_topic,
    select_search_queries,
    select_limit_comments_per_submission,
)
from src.utils.agent import Agent
from src.utils.document_loader import RedditSubLoader, TwitterTweetLoader
from src.utils.prompts import RedditPromptGenerator, TwitterPromptGenerator

load_dotenv()


def main():
    display_intro()
    topic = select_topic()
    platform, keywords, accounts = select_search_queries(topic)
    number_of_posts = select_number_of_posts()

    if platform == "reddit":
        limit_comments_per_submission = select_limit_comments_per_submission()
        document_loader = RedditSubLoader(
            number_submissions=number_of_posts,
            limit_comments_per_submission=limit_comments_per_submission,
            keywords=keywords,
            subreddits=accounts,
        )

        prompt_generator = RedditPromptGenerator()

    elif platform == "twitter":
        document_loader = TwitterTweetLoader.from_bearer_token(
            oauth2_bearer_token=os.environ.get("TWITTER_BEARER_TOKEN"),
            number_tweets=number_of_posts,
            twitter_users=accounts,
            keywords=keywords,
        )

        prompt_generator = TwitterPromptGenerator()

    else:
        raise ValueError(f"Platform {platform} not supported")

    agent = Agent(loader=document_loader, prompt_generator=prompt_generator)

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
