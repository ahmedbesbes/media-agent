from rich.console import Console
from rich.prompt import Prompt
from simple_term_menu import TerminalMenu
from src.twitter.utils.search import search_users

console = Console()


def display_intro():
    message = """
_____________________________________________________________________________________________________________ 

 _____        _ _   _               ___                   _   
|_   _|      (_| | | |             / _ \                 | |  
  | __      ___| |_| |_ ___ _ __  / /_\ \ __ _  ___ _ __ | |_ 
  | \ \ /\ / | | __| __/ _ | '__| |  _  |/ _` |/ _ | '_ \| __|
  | |\ V  V /| | |_| ||  __| |    | | | | (_| |  __| | | | |_ 
  \_/ \_/\_/ |_|\__|\__\___|_|    \_| |_/\__, |\___|_| |_|\__|
                                          __/ |               
                                         |___/                
_____________________________________________________________________________________________________________   
    """
    console.print(message, style="red bold")

    console.print(
        """
Twitter Agent scrapes data from Twitter and leverages the power of [red]Large Language Models (LLMs)[/red] 
to interactively chat with the extracted tweets 💬, summarize them 📝 and provide conversation ideas 💡.

Twitter Agent helps you quickly gather insights on real-time events such as news, build a technical knowledge
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

*************************************************************************************************************

Let's start :rocket:
    """,
    )


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


def select_topic():
    topic = Prompt.ask(
        "[bold red]Type something you want to search or learn about in Twitter ⌨️ [/bold red]"
    )
    return topic


def select_search_queries(topic):
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


def select_number_of_tweets():
    default_tweet_number = 10
    error = True
    i = 0
    while error:
        if i != 0:
            console.print("[red]Please enter an integer ⚠️[/red]")
        number_of_tweets = Prompt.ask(
            f"Enter the number of tweets to fetch per account ({default_tweet_number})",
            default=default_tweet_number,
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
