from rich.console import Console
from rich.prompt import Prompt
from simple_term_menu import TerminalMenu
from src.utils.search import search_users, search_subreddits

console = Console()


def display_intro():
    message = """
_____________________________________________________________________________________________________________ 

╭━━━━╮╱╱╱╱╭╮╱╭╮╱╱╱╱╱╭━━━╮╱╱╱╱╭╮╱╭╮╭╮╭━━━╮╱╱╱╱╱╱╱╱╭╮
┃╭╮╭╮┃╱╱╱╭╯╰┳╯╰╮╱╱╱╱┃╭━╮┃╱╱╱╱┃┃╱┃┣╯╰┫╭━╮┃╱╱╱╱╱╱╱╭╯╰╮
╰╯┃┃┣┫╭╮╭╋╮╭┻╮╭╋━━┳━┫╰━╯┣━━┳━╯┣━╯┣╮╭┫┃╱┃┣━━┳━━┳━╋╮╭╯
╱╱┃┃┃╰╯╰╯┣┫┃╱┃┃┃┃━┫╭┫╭╮╭┫┃━┫╭╮┃╭╮┣┫┃┃╰━╯┃╭╮┃┃━┫╭╮┫┃
╱╱┃┃╰╮╭╮╭┫┃╰╮┃╰┫┃━┫┃┃┃┃╰┫┃━┫╰╯┃╰╯┃┃╰┫╭━╮┃╰╯┃┃━┫┃┃┃╰╮
╱╱╰╯╱╰╯╰╯╰┻━╯╰━┻━━┻╯╰╯╰━┻━━┻━━┻━━┻┻━┻╯╱╰┻━╮┣━━┻╯╰┻━╯
╱╱╱╱╱╱╱╱╱╱╱╱╱╱╱╱╱╱╱╱╱╱╱╱╱╱╱╱╱╱╱╱╱╱╱╱╱╱╱╱╭━╯┃
╱╱╱╱╱╱╱╱╱╱╱╱╱╱╱╱╱╱╱╱╱╱╱╱╱╱╱╱╱╱╱╱╱╱╱╱╱╱╱╱╰━━╯

_____________________________________________________________________________________________________________   
    """
    console.print(message, style="red bold")

    console.print(
        """
Twitter Reddit Agent scrapes data from Twitter/Reddit and leverages the power of [red]Large Language Models (LLMs)[/red] 
to interactively chat with the extracted tweets 💬, summarize them 📝 and provide conversation ideas 💡.

Twitter Reddit Agent helps you quickly gather insights on real-time events such as news, build a technical knowledge
on your favourite programming language or research any topic that interests you. 

Tools and libraries used: 
    * [bold]Langchain 🦜[/bold] to build and compose LLMs
    * [bold]ChromaDB[/bold] to store vectors (a.k.a [italic]embeddings[/italic]) and query them to build conversational bots
    * [bold]Tweepy[/bold] to connect to your the Twitter API and extract Tweets and metadata
    * [bold]Rich[/bold] to build a cool terminal UX/UI
    * [bold]Poetry[/bold] to manage dependencies

Third party services:   
    * [bold]OpenAI[/bold] (🔑 needed)
    * [bold]Twitter[/bold] (🔑 needed)
    * [bold]Reddit[/bold] (🔑 needed)

*************************************************************************************************************

Let's start :rocket:
    """,
    )


def display_bot_answer(result, collection, history, user_input):
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
            include=["metadatas", "documents"],
        )

    console.print("These are sources I used to create my answer:")
    metadatas = output["metadatas"]
    documents = output["documents"]

    if len(metadatas) == 0 or len(documents) == 0:
        console.print(
            "No data is available to answer this question. Please review your query."
        )
    else:
        for i, (document, metadata) in enumerate(zip(documents, metadatas)):
            console.rule(f"Source {i+1}", style="red")
            console.print("Document :\n", style="blue bold underline")
            console.print(document)
            console.print("\n")
            console.print("metadatas :\n", style="blue bold underline")
            console.print(metadata)
            console.print(f"\n {'-'*50} \n")

    history["history"].append(
        {
            "question": user_input,
            "answer": result,
            "sources": [
                {"document": document, "metadata": metadata}
                for document, metadata in zip(documents, metadatas)
            ],
        }
    )


def select_topic() -> str:
    topic = Prompt.ask(
        "[bold red]Type something you want to search or learn about ⌨️ [/bold red]"
    )
    return topic


def select_search_queries(topic: str):
    platform = Prompt.ask(
        "Select a platform to search on",
        choices=["twitter", "reddit"],
        default="reddit",
    )

    if platform == "reddit":
        keywords, accounts = select_search_queries_reddit(topic)
    elif platform == "twitter":
        keywords, accounts = select_search_queries_twitter(topic)
    else:
        raise ValueError(f"Service {platform} is not supported")

    return platform, keywords, accounts


def select_search_queries_reddit(topic: str):
    search_type = Prompt.ask(
        "Enter a search type",
        choices=["keywords", "subreddits"],
        default="keywords",
    )

    if search_type == "subreddits":
        with console.status(
            "Finding relevant subreddits about this topic \n",
            spinner="aesthetic",
            speed=1.5,
            spinner_style="red",
        ):
            subreddits = search_subreddits(q=topic, count=10)

        options = [f"{sr.display_name} ({sr.subscribers})" for sr in subreddits]

        terminal_menu = TerminalMenu(
            options,
            multi_select=True,
            show_multi_select_hint=True,
            multi_select_cursor="x ",
            title="Select one or more subreddits to load the data from: \n",
        )

        menu_entry_indices = terminal_menu.show()
        subreddit_display_names = [
            subreddits[i].display_name for i in menu_entry_indices
        ]
        keywords = None

    elif search_type == "keywords":
        subreddit_display_names = None
        keywords = topic

    return keywords, subreddit_display_names


def select_search_queries_twitter(topic: str):
    search_type = Prompt.ask(
        "Enter a search type",
        choices=["keywords", "accounts"],
        default="keywords",
    )

    if search_type == "accounts":
        with console.status(
            "Finding relevant Twitter accounts that tweet about this topic \n",
            spinner="aesthetic",
            speed=1.5,
            spinner_style="red",
        ):
            users = search_users(q=topic, count=10)

        options = [
            f"{user['screen_name']} ({user['followers_count']})" for user in users
        ]

        terminal_menu = TerminalMenu(
            options,
            multi_select=True,
            show_multi_select_hint=True,
            multi_select_cursor="x ",
            title="Select one or more Twitter accounts to load the data from: \n",
        )

        menu_entry_indices = terminal_menu.show()
        twitter_users = [users[i]["screen_name"] for i in menu_entry_indices]
        keywords = None

    elif search_type == "keywords":
        twitter_users = None
        keywords = topic

    return keywords, twitter_users


def select_number_of_posts():
    default_post_number = 10
    error = True
    i = 0
    while error:
        if i != 0:
            console.print("[red]Please enter an integer ⚠️[/red]")
        number_of_tweets = Prompt.ask(
            f"Enter the number of posts to fetch per account ({default_post_number})",
            default=default_post_number,
        )
        try:
            number_of_tweets = int(number_of_tweets)
            error = False
        except ValueError:
            error = True

        i += 1

    return number_of_tweets


def display_summary_and_questions(summary, q1, q2, q3):
    console.print("Summary 📝 \n", style="red bold underline")
    console.print(summary + "\n ")
    console.print("Questions to start the chat 🔮 \n", style="red bold underline")
    console.print(f"q1: {q1} \n")
    console.print(f"q2: {q2} \n")
    console.print(f"q3: {q3} \n")
