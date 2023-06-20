from dotenv import load_dotenv
from rich.prompt import Prompt
from src.twitter.utils.display import (
    display_intro,
    select_number_of_tweets,
    select_topic,
    select_search_queries,
)
from src.twitter.utils.twitter_agent import TwitterAgent

load_dotenv()


def main():
    display_intro()
    topic = select_topic()
    keywords, twitter_users = select_search_queries(topic)
    number_of_tweets_per_account = select_number_of_tweets()

    twitter_agent = TwitterAgent(
        twitter_users=twitter_users,
        keywords=keywords,
        number_tweets=number_of_tweets_per_account,
    )

    twitter_agent.load_tweets()
    twitter_agent.init_docsearch()
    structured_summary = twitter_agent.summarize()

    while True:
        input_question = Prompt.ask(
            f"[bold red]Ask the db to learn more about the extracted tweets  💬 (you can type q1, q2 or q3 as well)[/bold red]"
        )
        twitter_agent.ask_the_db(input_question, structured_summary)


if __name__ == "__main__":
    main()
