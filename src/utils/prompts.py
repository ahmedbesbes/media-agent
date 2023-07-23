from abc import ABC, abstractmethod
from enum import Enum


class PromptMethod(Enum):
    stuff: str = "stuff"
    retrievalqa: str = "retrievalqa"


class PromptGenerator(ABC):
    @property
    @abstractmethod
    def source(self) -> str:
        pass

    @abstractmethod
    def get_summarization_template(self, method: PromptMethod) -> str:
        pass


class TwiiterPromptGenerator(PromptGenerator):
    @property
    def source(self) -> str:
        return "twitter"

    def get_summarization_template(self, method: PromptMethod) -> str:
        if method == PromptMethod.stuff:
            ret = """\
Given the following tweets

{text}

I want you to provide a short summary and produce three questions that cover the discussed topics.
Each question should find its answer within the tweets. Don't invent questions that have no answers.
Questions should also be very different from each other and discuss topics that are not necessarily present in the summary.

Format the output as a JSON with the following keys and do not forget the curly brackets.

* summary
* q1
* q2
* q3

"""

        elif method == PromptMethod.retrievalqa:
            ret = """\
Given the following documents, I want you to provide a short summary 
and produce three questions that cover the discussed topics.

Each question should find its answer within the documents. Don't invent questions that have no answers.
Questions should also be very different from each other and discuss topics that are not necessarily present in the summary.

Format the output as a JSON with the following keys and do not forget the curly brackets.

* summary
* q1
* q2
* q3

"""
        return ret


class RedditPromptGenerator(PromptGenerator):
    @property
    def source(self) -> str:
        return "reddit"

    def get_summarization_template(self, method: PromptMethod) -> str:
        if method == PromptMethod.stuff:
            ret = """\
Given the following reddit submissions

{text}

I want you to provide a short summary and produce three questions that cover the discussed topics.
Each question should find its answer within the submissions.
Don't invent questions that have no answers.
Put emphasis on submissions with high upvotes and redditors with high karma.
Questions should also be very different from each other and discuss topics that are not necessarily present in the summary.

Format the output as a JSON with the following keys and do not forget the curly brackets.

* summary
* q1
* q2
* q3

"""

        elif method == PromptMethod.retrievalqa:
            ret = """\
Given the following documents, I want you to provide a short summary and produce three questions that cover the discussed topics.

Each question should find its answer within the documents. Don't invent questions that have no answers.
Put emphasis on submissions with high upvotes and redditors with high karma.
Questions should also be very different from each other and discuss topics that are not necessarily present in the summary.

Format the output as a JSON with the following keys and do not forget the curly brackets.

* summary
* q1
* q2
* q3

"""
        return ret
