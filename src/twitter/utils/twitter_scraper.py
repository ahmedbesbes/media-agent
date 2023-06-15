import os
from rich.console import Console
from langchain.vectorstores import Chroma
from langchain.embeddings.openai import OpenAIEmbeddings
import chromadb
from chromadb.config import Settings
from src.common.spinner import Spinner
from src.twitter import logger
from src.twitter.utils.chains import get_retrieval_qa_chain
from src.twitter.utils.data_processing import (
    get_texts_from_documents,
    get_metadatas_from_documents,
)
from src.twitter.utils.display import display_bot_answer
from src.twitter.utils.document_loader import TwitterTweetLoader


class TwitterScraper(object):
    def __init__(
        self,
        twitter_users,
        number_tweets,
        persist_db=True,
    ):
        self.twitter_users = twitter_users
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

    def ask_the_db(self, user_input):
        with Spinner():
            result = self.chain(
                {"question": user_input},
                return_only_outputs=True,
            )
        display_bot_answer(result, self.collection)
