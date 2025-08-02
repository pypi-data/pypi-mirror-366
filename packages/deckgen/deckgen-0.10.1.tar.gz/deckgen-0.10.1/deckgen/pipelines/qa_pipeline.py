from deckgen.generation.openai_client import OpenAIClient
from deckgen.templates import TOPIC_FINDER
from deckgen.templates import QUESTION_ASKING
from typing import Optional
from typing import List
from typing import Dict
import json
import re


class QAParser:

    def __init__(self) -> None:
        """
        Initializes the QAParser
        """

    def parse(self, text: str) -> List[Dict[str, str]]:
        """
        Parses the provided text to extract questions and answers.

        :param text: The text to parse.
        :return: A list of dictionaries containing questions and their corresponding answers.
        :raises ValueError: If no text is provided for parsing.
        :raises ValueError: If no valid question-answer pairs are found in the text.
        """
        if not text:
            raise ValueError("No text provided for parsing.")

        # Regex pattern to match question-answer pairs (question ends with '?', answer follows)
        pattern = r"(?P<question>.*?\?)\s+(?P<answer>.*?)(?=\n\d+\.|\Z)"

        matches = re.finditer(pattern, text, re.DOTALL)
        qa_list = [
            {
                "question": m.group("question").strip(),
                "answer": m.group("answer").strip(),
            }
            for m in matches
        ]

        # Remove leading index (e.g., "1. ", "2. ") from each question in qa_list
        for qa in qa_list:
            qa["question"] = (
                qa["question"].lstrip().split(" ", 1)[-1]
                if qa["question"].lstrip()[0].isdigit() and "." in qa["question"]
                else qa["question"]
            )
            qa["answer"] = qa["answer"].strip()
        # Ensure that each question and answer is stripped of leading/trailing whitespace
        qa_list = [
            {"question": qa["question"].strip(), "answer": qa["answer"].strip()}
            for qa in qa_list
        ]
        # Ensure that the list is not empty
        if not qa_list:
            raise ValueError("No valid question-answer pairs found in the text.")
        return qa_list


class QAToolKit:
    def __init__(self, openai_api_key: Optional[str] = None):
        self.openai_client = OpenAIClient(api_key=openai_api_key)

    def get_topics(self, text: str) -> str:
        """
        Extracts topics from the input text.
        This is a placeholder for topic extraction logic.
        """
        if not text:
            raise ValueError("No text provided for topic extraction.")

        topic_response = self.openai_client.request(
            method="POST",
            endpoint="responses",
            data=json.dumps(
                {
                    "model": "gpt-3.5-turbo",
                    "input": TOPIC_FINDER.replace("{{", "{")
                    .replace("}}", "}")
                    .format(text=text),
                }
            ),
        )

        if topic_response.status_code != 200:
            raise ValueError(f"Failed to extract topics: {topic_response.text}")

        topics = topic_response.json()["output"][0]["content"][0]["text"]
        return topics

    def generate_qa_string(self, topics: str, text: str) -> str:
        """
        Generates a question-answer string based on the input text and identified topics.
        :param topics: A string containing the identified topics.
        :param text: The input text to generate questions and answers from.
        :return: A string containing the generated questions and answers.
        :raises ValueError: If no input text is provided for question generation.
        """
        if not text:
            raise ValueError("No input text provided for question generation.")
        if not topics:
            raise ValueError("No topics provided for question generation.")
        qa_response = self.openai_client.request(
            method="POST",
            endpoint="responses",
            data=json.dumps(
                {
                    "model": "gpt-4o-mini",
                    "input": QUESTION_ASKING.replace("{{", "{")
                    .replace("}}", "}")
                    .format(expertise=topics, text=text),
                }
            ),
        )

        qa_string = qa_response.json()["output"][0]["content"][0]["text"]
        return qa_string
