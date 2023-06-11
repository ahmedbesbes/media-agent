from dotenv import load_dotenv
from rich.prompt import Prompt
from src.twitter.config import NUMBER_TWEETS
from src.twitter.twitter_scraper import TwitterScraper
from simple_term_menu import TerminalMenu
from src.twitter.utils import search_users
from src.common.spinner import Spinner

load_dotenv()


def main():
    topic = Prompt.ask(
        "[bold red]Type something you want to search or learn about in Twitter ⌨️ [/bold red]"
    )

    with Spinner(
        text_message="Finding relevant Twitter accounts that tweet about this topic"
    ):
        users = search_users(q=topic, count=10)

    options = [f"{user['screen_name']} ({user['followers_count']})" for user in users]

    terminal_menu = TerminalMenu(
        options,
        multi_select=True,
        show_multi_select_hint=True,
        multi_select_cursor="x ",
        title="Select one or more Twitter accounts to load the data from: \n",
    )

    menu_entry_indices = terminal_menu.show()
    twitter_users = [users[i]["screen_name"] for i in menu_entry_indices]

    twitter_scraper = TwitterScraper(
        twitter_users=twitter_users,
        number_tweets=NUMBER_TWEETS,
    )
    twitter_scraper.load_tweets()
    twitter_scraper.init_docsearch()

    while True:
        input_question = Prompt.ask(
            f"[bold red]Ask the db to learn about {'|'.join(twitter_users)} 💬[/bold red]"
        )
        twitter_scraper.ask_the_db(input_question)


if __name__ == "__main__":
    main()
