from pathlib import Path
from datetime import datetime
from langchain.chat_models import ChatOpenAI
from langchain.callbacks import get_openai_callback
from langchain.chains import ConversationChain
from langchain.prompts import (
    PromptTemplate,
    MessagesPlaceholder,
    HumanMessagePromptTemplate,
    SystemMessagePromptTemplate,
    ChatPromptTemplate,
)
from langchain.memory import ConversationBufferWindowMemory
from langchain.callbacks.streaming_stdout import StreamingStdOutCallbackHandler
from dotenv import load_dotenv
from spinner import Spinner
from utils import print_ai_message, RED, YELLOW, print_slow

load_dotenv()

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
    # callbacks=[StreamingStdOutCallbackHandler()],
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

prompt_introduction = PromptTemplate(
    input_variables=["topic"],
    template=Path("prompts/introduction.prompt").read_text(),
)


def main():
    TOTAL_COST = 0

    topic = print_slow(f"What topic are you interested to write about: ")
    topic = input()
    file_name = f"./answers/{topic}_{str(datetime.now().replace(microsecond=0))}.md"

    input_request = prompt_introduction.format(topic=topic)
    input_text = input_request
    while True:
        with get_openai_callback() as cb:
            with Spinner():
                response = chain.run(input_text)
                print_ai_message(response)
                TOTAL_COST += cb.total_cost

        response = "\n" + response + "\n"
        is_happy = "no"
        is_happy = input(
            f"\nAre you happy with this answer? (yes/no) [yes] (Total cost so far: {TOTAL_COST}) :"
        )
        if not is_happy:
            is_happy = "yes"

        while is_happy == "no":
            input_text = input("(you) [q to quit] > :")
            if input_text == "q":
                break

            with get_openai_callback() as cb:
                with Spinner():
                    response = chain.run(input_text)
                    print_ai_message(response)
                    TOTAL_COST += cb.total_cost

            response = "\n" + response + "\n"
            print(f"(AI) > {response}")

            is_happy = input(
                f"\nAre you happy with this answer? (yes/no) [yes] (Total cost so far: {TOTAL_COST}) :"
            )
            if not is_happy:
                is_happy = "yes"

        if input_text == "q":
            break

        save = input(
            "Great, would you like to save this answer to a file? (yes/no) [yes]"
        )
        if not save:
            save = "yes"

        if save == "yes":
            with open(file_name, "a") as f:
                f.write(response)

        input_text = input("(you) [q to quit] > ")
        if input_text == "q":
            break


if __name__ == "__main__":
    main()
