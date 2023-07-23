import atexit
import sys
import json
from rich.console import Console
from langchain.vectorstores import Chroma
from langchain.embeddings.openai import OpenAIEmbeddings
import chromadb
from chromadb.config import Settings
import tiktoken
from src import logger
from src.utils.chains import (
    get_retrieval_qa_chain,
    summarize_tweets,
)
from src.utils.display import display_bot_answer, display_summary_and_questions

from src.utils.prompts import PromptGenerator, PromptMethod
from src.utils.document_loader import DocumentLoader
from langchain.text_splitter import CharacterTextSplitter


class Agent(object):
    def __init__(
        self,
        loader: DocumentLoader,
        prompt_generator: PromptGenerator,
        persist_db: bool = True,
    ):
        self.loader = loader
        self.prompt_generator = prompt_generator
        self.loaded_documents = []
        self.embeddings = OpenAIEmbeddings()
        self.persist_db = persist_db
        self.chain = None
        self.retriever = None
        self.client = None
        self.collection = None
        self.console = Console()
        self.history = {"history": []}

        def save_history():
            self.console.log(
                "Saving conversation history with sources and metadata ..."
            )
            with open("outputs/history.json", "w") as f:
                json.dump(self.history, f)

        atexit.register(save_history)

    def _get_number_of_tokens(self):
        encoding = tiktoken.encoding_for_model("gpt-3.5-turbo")
        texts = [doc.page_content for doc in self.loaded_documents]
        text = "\n".join(texts)
        summarization_template = self.prompt_generator.get_summarization_template(
            method=PromptMethod.stuff
        )
        formatted_summary_template = summarization_template.format(text=text)
        num_tokens = len(encoding.encode(formatted_summary_template))
        return num_tokens

    def load_documents(self):
        text_splitter = CharacterTextSplitter(chunk_size=2000)

        self.loaded_documents = text_splitter.split_documents(
            self.loader.load(console=self.console, history=self.history)
        )

    def init_docsearch(self):
        self.docsearch = Chroma.from_documents(
            documents=self.loaded_documents,
            embedding=self.embeddings,
            persist_directory="db",
        )
        self.retriever = self.docsearch.as_retriever()

        if self.persist_db:
            self.docsearch.persist()
        self.chain = get_retrieval_qa_chain(self.retriever)
        self.client = chromadb.Client(
            Settings(
                chroma_db_impl="duckdb+parquet",
                persist_directory="db",
            )
        )
        self.collection = self.client.get_collection("langchain")

    def summarize(self):
        if self.loaded_documents is None:
            raise ValueError("Document are not loaded yet. Run `load` first.")

        num_tokens = self._get_number_of_tokens()

        if num_tokens <= 4097:
            method = PromptMethod.stuff
        else:
            method = PromptMethod.retrievalqa

        with self.console.status(
            "Generating a summary of the loaded tweets ... ⌛ \n",
            spinner="aesthetic",
            speed=1.5,
            spinner_style="red",
        ):
            summary = summarize_tweets(
                docs=self.loaded_documents,
                retriever=self.retriever,
                method=method,
                prompt_generator=self.prompt_generator,
            )

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
