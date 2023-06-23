* Install dependencies

poetry install --with dev

* Add credentials

Create .env file at the root of the project with the following keys:

```
OPENAI_API_KEY=<OPENAI KEY>
TWITTER_API_KEY=<TWITTER API KEY>
TWITTER_API_KEY_SECRET=<TWITTER API KEY SECRET>
TWITTER_BEARER_TOKEN=<TWITTER BEARER TOKEN>
```

More info on these credentials [here](https://openai.com/) and [here](https://developer.twitter.com/en/docs/apps/overview).


* Run the app locally

```shell
make run-twitter-agent

________________________________________________________________________

 _____        _ _   _               ___                   _   
|_   _|      (_| | | |             / _ \                 | |  
  | __      ___| |_| |_ ___ _ __  / /_\ \ __ _  ___ _ __ | |_ 
  | \ \ /\ / | | __| __/ _ | '__| |  _  |/ _` |/ _ | '_ \| __|
  | |\ V  V /| | |_| ||  __| |    | | | | (_| |  __| | | | |_ 
  \_/ \_/\_/ |_|\__|\__\___|_|    \_| |_/\__, |\___|_| |_|\__|
                                          __/ |               
                                         |___/                
________________________________________________________________________   


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
```