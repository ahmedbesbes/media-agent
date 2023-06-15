from dotenv import load_dotenv
from rich.prompt import Prompt
from src.twitter.utils.display import (
    select_number_of_tweets_per_account,
    select_topic,
    select_twitter_accounts_from_menu,
)
from src.twitter.utils.twitter_scraper import TwitterScraper

load_dotenv()


def main():
    topic = select_topic()
    twitter_accounts = select_twitter_accounts_from_menu(topic)
    number_of_tweets_per_account = select_number_of_tweets_per_account()

    twitter_scraper = TwitterScraper(
        twitter_users=twitter_accounts,
        number_tweets=number_of_tweets_per_account,
    )

    twitter_scraper.load_tweets()
    twitter_scraper.init_docsearch()

    while True:
        input_question = Prompt.ask(
            f"[bold red]Ask the db to learn about {'|'.join(twitter_accounts)} 💬[/bold red]"
        )
        twitter_scraper.ask_the_db(input_question)


if __name__ == "__main__":
    main()
