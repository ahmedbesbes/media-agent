from pathlib import Path
import streamlit as st
from langchain.prompts import PromptTemplate
from ui import ask_for_section, display_section
from llm import get_chain, generate_answer, ask_for_refine


st.set_page_config(layout="wide")

API_KEY = st.sidebar.text_input("OpenAI Key")
chain = get_chain()
columns = st.columns(2)

chain, response = display_section(chain, 0)
