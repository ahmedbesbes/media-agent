from langchain.chains import RetrievalQAWithSourcesChain
from langchain.chat_models import ChatOpenAI
from langchain.chains.summarize import load_summarize_chain
from langchain.prompts import PromptTemplate
from langchain.docstore.document import Document
from src.utils.prompts import summarization_template


def get_retrieval_qa_chain(retriever):
    chain = RetrievalQAWithSourcesChain.from_chain_type(
        ChatOpenAI(temperature=0),
        chain_type="stuff",
        retriever=retriever,
    )
    return chain


### Summarization


def get_summarization_chain(prompt):
    llm = ChatOpenAI(temperature=0)
    chain = load_summarize_chain(
        llm,
        chain_type="stuff",
        prompt=prompt,
    )
    return chain


def summarize_tweets(docs):
    prompt = PromptTemplate(template=summarization_template, input_variables=["text"])
    chain = get_summarization_chain(prompt)
    summary = chain.run(docs)
    return summary
