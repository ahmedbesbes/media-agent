import atexit
import os
import sys
import json
from rich.console import Console
from langchain.vectorstores import Chroma
from langchain.embeddings.openai import OpenAIEmbeddings
import chromadb
from chromadb.config import Settings
from src.twitter import logger
from src.twitter.utils.chains import get_retrieval_qa_chain, summarize_tweets
from src.twitter.utils.data_processing import (
    get_texts_from_documents,
    get_metadatas_from_documents,
)
from src.twitter.utils.display import display_bot_answer, display_summary_and_questions
from src.twitter.utils.document_loader import TwitterTweetLoader


class TwitterAgent(object):
    def __init__(
        self,
        twitter_users,
        keywords,
        number_tweets,
        persist_db=True,
    ):
        self.twitter_users = twitter_users
        self.keywords = keywords
        self.number_tweets = number_tweets
        self.loaded_documents = []
        self.embeddings = OpenAIEmbeddings()
        self.persist_db = persist_db
        self.chain = None
        self.client = None
        self.collection = None
        self.console = Console()
        self.history = {"history": []}

        def save_history():
            self.console.log(
                "Saving conversation history with sources and metadata ..."
            )
            with open("history.json", "w") as f:
                json.dump(self.history, f)

        atexit.register(save_history)

    def _get_tweets_loader(self):
        loader = TwitterTweetLoader.from_bearer_token(
            oauth2_bearer_token=os.environ.get("TWITTER_BEARER_TOKEN"),
            number_tweets=self.number_tweets,
            twitter_users=self.twitter_users,
            keywords=self.keywords,
        )
        return loader

    def load_tweets(self):
        loader = self._get_tweets_loader()
        with self.console.status(
            "Loading Tweets",
            spinner="aesthetic",
            speed=1.5,
            spinner_style="red",
        ):
            documents = loader.load()
        logger.info(f"{len(documents)} tweets are loaded ...")
        self.loaded_documents = documents

        self.history["search_type"] = (
            "keywords" if self.keywords is not None else "twitter_accounts"
        )
        self.history["input_query"] = (
            self.keywords if self.keywords is not None else self.twitter_users
        )
        self.history["num_tweets"] = len(documents)

    def init_docsearch(self):
        texts = get_texts_from_documents(self.loaded_documents)
        metadatas = get_metadatas_from_documents(self.loaded_documents)

        docsearch = Chroma.from_texts(
            texts,
            self.embeddings,
            metadatas=metadatas,
            persist_directory="db",
        )
        if self.persist_db:
            docsearch.persist()
        self.chain = get_retrieval_qa_chain(docsearch.as_retriever())
        self.client = chromadb.Client(
            Settings(
                chroma_db_impl="duckdb+parquet",
                persist_directory="db",
            )
        )
        self.collection = self.client.get_collection("langchain")

    def summarize(self):
        if self.loaded_documents is not None:
            with self.console.status(
                "Generating a summary of the loaded tweets ... ⌛ \n",
                spinner="aesthetic",
                speed=1.5,
                spinner_style="red",
            ):
                summary = summarize_tweets(self.loaded_documents)
        else:
            raise ValueError("Document are not loaded yet. Run `load_tweets` first.")

        try:
            structured_summary = json.loads(summary)
        except Exception as e:
            logger.error(str(e))
            sys.exit()

        summary = structured_summary.get("summary")
        q1 = structured_summary.get("q1")
        q2 = structured_summary.get("q2")
        q3 = structured_summary.get("q3")
        display_summary_and_questions(summary, q1, q2, q3)
        self.history["summary_metadata"] = {}
        self.history["summary_metadata"]["summary"] = summary
        self.history["summary_metadata"]["q1"] = q1
        self.history["summary_metadata"]["q2"] = q2
        self.history["summary_metadata"]["q3"] = q3
        return structured_summary

    def ask_the_db(self, user_input, structured_summary):
        if user_input.lower() == "q":
            self.console.log("Exiting program. Bye :wave:")
            sys.exit()

        if user_input in structured_summary:
            user_input = structured_summary[user_input]
            self.console.print(f"[bold purple]{user_input}[/bold purple] \n")

        with self.console.status(
            "Generating answer with relevant sources \n",
            spinner="aesthetic",
            speed=1.5,
            spinner_style="red",
        ):
            result = self.chain(
                {"question": user_input},
                return_only_outputs=True,
            )
        display_bot_answer(
            result,
            self.collection,
            self.history,
            user_input,
        )
