import sys
from dotenv import load_dotenv
from simple_term_menu import TerminalMenu
from rich.prompt import Prompt
from src.reddit import logger
from src.common.spinner import Spinner
from src.reddit.config import POST_NUMBER_BY_SUBREDDIT
from src.reddit.utils import get_top_subreddits
from src.reddit.reddit_scraper import RedditScraper

load_dotenv()


def main():
    topic = Prompt.ask(
        "[bold red]Type something you want to search or learn about ⌨️ [/bold red]"
    )

    with Spinner(text_message="Finding relevant Subreddits for your query"):
        top_subreddits, top_counts = get_top_subreddits(query=topic)

    options = [
        f"{subreddit} ({count})" for subreddit, count in zip(top_subreddits, top_counts)
    ]

    terminal_menu = TerminalMenu(
        options,
        multi_select=True,
        show_multi_select_hint=True,
        multi_select_cursor="x ",
        title="Select one or more Subreddits to load the data from: \n",
    )
    menu_entry_indices = terminal_menu.show()
    selected_subreddits = [top_subreddits[i] for i in menu_entry_indices]

    reddit_scraper = RedditScraper(
        topic,
        POST_NUMBER_BY_SUBREDDIT,
        selected_subreddits,
    )
    reddit_scraper.load_reddit_posts()

    if len(reddit_scraper.loaded_documents) == 0:
        logger.error(
            "The loaded number of documents is equal 0. Please consider changing the search query or the subreddits"
        )
        logger.info("Exiting ...")
        sys.exit()

    reddit_scraper.init_docsearch()

    while True:
        input_question = Prompt.ask("[bold red]Ask the db 💬[/bold red]")
        reddit_scraper.ask_the_db(input_question)


if __name__ == "__main__":
    main()
