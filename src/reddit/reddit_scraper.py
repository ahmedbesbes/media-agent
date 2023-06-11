import os
from rich.console import Console
from langchain.vectorstores import Chroma
from langchain.embeddings.openai import OpenAIEmbeddings
from langchain.chains import RetrievalQAWithSourcesChain
from langchain.chat_models import ChatOpenAI
import chromadb
from chromadb.config import Settings
from src.common.spinner import Spinner
from src.reddit import logger
from src.reddit.utils import (
    get_metadatas_from_documents,
    get_texts_from_documents,
    display_bot_answer,
)
from src.reddit.document_loader import RedditPostsLoader


class RedditScraper(object):
    def __init__(
        self,
        topic,
        num_posts,
        selected_subreddits,
        persist_db=True,
    ):
        self.topic = topic
        self.num_posts = num_posts
        self.selected_subreddits = selected_subreddits
        self.loaded_documents = []
        self.embeddings = OpenAIEmbeddings()
        self.persist_db = persist_db
        self.chain = None
        self.client = None
        self.collection = None
        self.console = Console()

    def _get_reddit_posts_loader(self):
        loader = RedditPostsLoader(
            client_id=os.environ.get("REDDIT_CLIENT_ID"),
            client_secret=os.environ.get("REDDIT_CLIENT_SECRET"),
            user_agent=os.environ.get("USER_AGENT"),
            categories=["hot"],
            mode="keyword",
            search_queries=[self.topic],
            number_posts=self.num_posts,
            searchable_subreddits=self.selected_subreddits,
        )
        return loader

    def load_reddit_posts(self):
        loader = self._get_reddit_posts_loader()
        with Spinner(text_message="Loading Reddit documents"):
            documents = loader.load()
        logger.info(f"{len(documents)} are loaded ...")
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
        self.chain = RetrievalQAWithSourcesChain.from_chain_type(
            ChatOpenAI(temperature=0),
            chain_type="stuff",
            retriever=docsearch.as_retriever(),
        )
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
