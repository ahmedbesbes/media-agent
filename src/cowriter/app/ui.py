from pathlib import Path
import streamlit as st
from langchain.prompts import PromptTemplate
from llm import generate_answer, ask_for_refine


def get_introduction_prompt(path, topic):
    prompt_introduction = PromptTemplate(
        input_variables=["topic"],
        template=Path(path).read_text(),
    )
    input_request = prompt_introduction.format(topic=topic)
    return input_request


def ask_for_section(key):
    input_request = st.text_input(
        "Provide more details on the next section",
        key=key,
    )
    return input_request


def display_section(chain, key):
    if key == 0:
        label = "What topic are you interested in?"
        header = "Introduction"
    else:
        label = "Prompt the bot to write the next section"
        header = f"Section {key}"

    columns = st.columns(2)

    with columns[0]:
        input_request = st.text_input(label, key=key)

    with columns[1]:
        st.markdown(f"### {header}")
        if input_request.strip() != "":
            if key == 0:
                with st.spinner(f"Generating an introduction on **{input_request}**"):
                    response, total_cost = generate_answer(chain, input_request)
            else:
                with st.spinner(f"Generating the following section"):
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

            while ok == "no":
                ok, key, refined_response = ask_for_refine(key, chain)
                response = refined_response

            if ok == "yes":
                write_to_file = st.selectbox(
                    "Do you want to write it to a file",
                    options=["", "yes", "no"],
                )

                if write_to_file == "yes":
                    with open(f"answers/output.md", "a") as f:
                        f.write(response)

    add_section = st.button("Add section", key=f"add_section_{key}")
    if add_section:
        display_section(chain, key + 1)

    return response, chain
