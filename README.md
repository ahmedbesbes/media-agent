## Media Agent 
Media Agent is scrapes Twitter and Reddit submissions, summarizes them, and chats with them in an interactive terminal.

---

![image](./assets/media_agent.png)


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
* **Praw** to connect to Reddit API
* **Rich** to build a cool terminal UX/UI
* **Poetry** to manage dependencies

### Third party services
* OpenAI (🔑 needed)
* Twitter (🔑 needed)
* Reddit (🔑 needed)

### Run the app locally

* Install dependencies with poetry

```bash
poetry install --with dev
```

* Add API credentials

Create .env file at the root of the project with the following keys:

```bash
OPENAI_API_KEY=<OPENAI KEY>
TWITTER_BEARER_TOKEN=<TWITTER BEARER TOKEN>
REDDIT_API_CLIENT_ID=<REDDIT_API_CLIENT_ID>
REDDIT_API_SECRET=<REDDIT_API_SECRET>
REDDIT_USER_AGENT=<REDDIT_USER_AGENT>
```

More info on these credentials [here](https://openai.com/), [here](https://developer.twitter.com/en/docs/apps/overview) and [here](https://www.geeksforgeeks.org/how-to-get-client_id-and-client_secret-for-python-reddit-api-registration/)


### Future features:

This is an on-going project, so feel free to contribute:

Here's what I plan in the near future:

* Add more data sources: substack, press, LinkedIN
* support open-source LLMs (Falcon?)
* support Pinecone in addition to ChromaDB
* add instructions to deployment on a cloud infrastructure
* improve the prompts to have a more engaging/enriching conversations
* add actions to open URLs and fetch content from it
