## Twitter Reddit Agent 
Twitter Reddit Agent is CLI that scrapes tweets/reddit submissions, summarizes them, and chats with them in an interactive terminal.

---

![image](https://github.com/syltruong/twitter-reddit-agent/assets/24707558/b4885c0a-b5b4-48c0-9590-ba8bb809c724)


### Functionalities

- Scrapes tweets/submissions on your behalf either from a list of 
user accounts or a list of keywords.
- Embeds the tweets/submissions using OpenAI 
- Indexes the embeddings (i.e. *vectors*) in ChromaDB
- Enriches the index with additional metadata
- Creates a summary of the tweets/submissions and provides potential questions to answer
- Opens a chat session on top of the tweets
- Saves the conversation with its metadata
- A rich terminal UI and logging features


### Tools and libraries used

* **Langchain** 🦜 to build and compose LLMs
* **ChromaDB** to store vectors (a.k.a embeddings) and query them to build conversational bots
* **Tweepy** to connect to your the Twitter API and extract Tweets and metadata
* **Rich** to build a cool terminal UX/UI
* **Poetry** to manage dependencies

### Third party services
* OpenAI (🔑 needed)
* Twitter (🔑 needed)
* Reddit (🔑 needed)

### Run the app locally

* Install dependencies with poetry

poetry install --with dev

* Add API credentials

Create .env file at the root of the project with the following keys:

```
OPENAI_API_KEY=<OPENAI KEY>
TWITTER_BEARER_TOKEN=<TWITTER BEARER TOKEN>
REDDIT_API_CLIENT_ID=<REDDIT_API_CLIENT_ID>
REDDIT_API_SECRET=<REDDIT_API_SECRET>
REDDIT_USER_AGENT=<REDDIT_USER_AGENT>
```

More info on these credentials [here](https://openai.com/) and [here](https://developer.twitter.com/en/docs/apps/overview).


### Future features:

This is an on-going project, so feel free to contribute:

Here's what I plan in the near future:

* support other LLMs (Falcon?)
* support Pinecone as an alternative to ChromaDB
* support Twint as an alternative to Tweepy (in case the Twitter API reaches its limit in terms of calls)
* add instructions to deployment on a cloud infrastructure
* improve the prompts to have a more engaging/enriching conversations
* add actions to open URLs and fetch content from it
