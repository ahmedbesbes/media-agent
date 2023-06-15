from langchain.chains import RetrievalQAWithSourcesChain
from langchain.chat_models import ChatOpenAI


def get_retrieval_qa_chain(retriever):
    chain = RetrievalQAWithSourcesChain.from_chain_type(
        ChatOpenAI(temperature=0),
        chain_type="stuff",
        retriever=retriever,
    )
    return chain
