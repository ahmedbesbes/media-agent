import os
import struct
import sys
import json
from rich.console import Console
from langchain.vectorstores import Chroma
from langchain.embeddings.openai import OpenAIEmbeddings
import chromadb
from chromadb.config import Settings
from src.common.spinner import Spinner
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
        with Spinner(text_message="Loading Tweets"):
            documents = loader.load()
        logger.info(f"{len(documents)} tweets are loaded ...")
        self.loaded_documents = documents

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
            with Spinner(text_message="Generating a summary of the loaded tweets"):
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
        return structured_summary

    def ask_the_db(self, user_input, structured_summary):
        if user_input in structured_summary:
            user_input = structured_summary[user_input]
            self.console.print(
                f"[bold purple]You picked this question : {user_input}[/bold purple]"
            )

        with Spinner():
            result = self.chain(
                {"question": user_input},
                return_only_outputs=True,
            )
        display_bot_answer(result, self.collection)
