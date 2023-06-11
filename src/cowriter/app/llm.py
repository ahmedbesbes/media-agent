from pathlib import Path
from dotenv import load_dotenv
import streamlit as st
from langchain.chat_models import ChatOpenAI
from langchain.callbacks import get_openai_callback
from langchain.chains import ConversationChain
from langchain.prompts import (
    MessagesPlaceholder,
    HumanMessagePromptTemplate,
    SystemMessagePromptTemplate,
    ChatPromptTemplate,
)
from langchain.memory import ConversationBufferWindowMemory


load_dotenv()


@st.cache_resource()
def get_chain():
    chat_prompt = ChatPromptTemplate.from_messages(
        [
            SystemMessagePromptTemplate.from_template(
                Path("prompts/system.prompt").read_text()
            ),
            MessagesPlaceholder(variable_name="history"),
            HumanMessagePromptTemplate.from_template("{input}"),
        ]
    )

    llm = ChatOpenAI(
        temperature=0.8,
        streaming=False,
    )

    memory = ConversationBufferWindowMemory(
        k=5,
        return_messages=True,
    )

    chain = ConversationChain(
        llm=llm,
        memory=memory,
        prompt=chat_prompt,
    )
    return chain


def ask_for_refine(key, chain):
    key += 1
    input_request = st.text_input(
        "Refine your query",
        key=f"refine_{key}",
    )

    if input_request.strip() != "":
        with st.spinner("Refining answer"):
            response, total_cost = generate_answer(chain, input_request)

    else:
        response = ""

    if response != "":
        st.markdown(response)

        ok = st.selectbox(
            "Are you happy with the answer",
            options=["", "yes", "no"],
            key=f"ok_{key}",
        )
    else:
        ok = ""
    return ok, key, response


@st.cache_data(show_spinner=False)
def generate_answer(_chain, input_request):
    # with get_openai_callback() as cb:
    #     response = _chain.run(input_request)
    # return response, cb.total_cost

    response = Path("examples/introduction.md").read_text()
    return response, 0
