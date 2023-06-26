summarization_template = """Given the following tweets

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

summarization_question_template = """Given the following documents, I want you to provide a short summary 
and produce three questions that cover the discussed topics.

Each question should find its answer within the documents. Don't invent questions that have no answers.
Questions should also be very different from each other and discuss topics that are not necessarily present in the summary.

Format the output as a JSON with the following keys and do not forget the curly brackets.

* summary
* q1
* q2
* q3

"""
