from typing import List
from langchain.chains import RetrievalQAWithSourcesChain
from langchain.schema import Document
from langchain.chat_models import ChatOpenAI
from langchain.chains.summarize import load_summarize_chain
from langchain.vectorstores.base import VectorStoreRetriever
from langchain.prompts import PromptTemplate
from src.utils.prompts import PromptGenerator, PromptMethod


def get_retrieval_qa_chain(retriever):
    chain = RetrievalQAWithSourcesChain.from_chain_type(
        ChatOpenAI(temperature=0),
        chain_type="stuff",
        retriever=retriever,
    )
    return chain


def get_summarization_chain(prompt):
    llm = ChatOpenAI(temperature=0)
    chain = load_summarize_chain(
        llm,
        chain_type="stuff",
        prompt=prompt,
    )
    return chain


def summarize_tweets(
    docs: List[Document],
    retriever: VectorStoreRetriever,
    method: PromptMethod,
    prompt_generator: PromptGenerator,
):
    template = prompt_generator.get_summarization_template(method=method)

    if method == PromptMethod.stuff:
        prompt = PromptTemplate(template=template, input_variables=["text"])
        chain = get_summarization_chain(prompt)
        summary = chain.run(docs)
        return summary

    if method == PromptMethod.retrievalqa:
        chain = get_retrieval_qa_chain(retriever=retriever)
        response = chain(
            {
                "question": template,
            },
        )
        summary = response["answer"]
        return summary

    raise ValueError(f"Unknown method: {method}")
