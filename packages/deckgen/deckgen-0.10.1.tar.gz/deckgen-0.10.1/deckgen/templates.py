TOPIC_FINDER = """
You are an expert in identifying topics from text. Your task is to analyze
the provided text and extract the main topics or themes. Please return a
list of topics that best represent the content of the text. Ensure that 
the topics are concise, relevant, and reflect the core ideas presented. 
Do not include any explanations or additional information, just the list of topics.
Limit the number of topics to a maximum of 3.
Text: {{text}}
Topics:
"""

QUESTION_ASKER = """ 
You are an expert in {{expertise}}. Additionally, you are an expert in how to ask questions 
to challenge the understanding of the topic. Your task is to provide a list of questions that 
will help to ingrain the understanding of the topic, as well as providing the answer to each one of the 
questions. The questions and answers should be made from a text that is provided to you.
Do not include additional information or explanations derived from other sources. 
Additionally, do not include any questions or answers that are not related to the text provided. 
Text: {{text}}
Questions and Answers:
"""

QUESTION_ASKING = """
You are an expert in {{expertise}}. You are also an expert in how to ask questions
to challenge the understanding of the topic. The questions you ask should be designed to 
assess the understanding of the topic, and evaluate the ability of the student to recognize and 
recall information. 
Your task is to provide a list of questions with answers from the given text. 
DO NOT include any additional information or explanations derived from other sources.
Text: {{text}}

OUTPUT FORMAT:
Here is an example of the output format you should use:
1. <question 1>
   <answer 1>
2. <question 2>
   <answer 2>

"""
QUESTION_GROUNDEDNESS_CRITIQUE_PROMPT = """
You will be given a context and a question.
Your task is to provide a 'total rating' scoring how well one can answer the given question unambiguously with the given context.
Give your answer on a scale of 1 to 5, where 1 means that the question is not answerable at all given the context, and 5 means that the question is clearly and unambiguously answerable with the context.

Provide your answer as follows:

Answer:::
Evaluation: (your rationale for the rating, as a text)
Total rating: (your rating, as a number between 1 and 5)
You MUST follow the output format for the total rating exactly as shown.
Total rating must be a number between 1 and 5. DO NOT use any other format or additional text.

You MUST provide values for 'Evaluation:' and 'Total rating:' in your answer.

Now here are the question and context.

Question: {question}\n
Context: {context}\n
Answer:::"""
