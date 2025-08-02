from typing import List
from typing import Dict
import re
from deckgen.templates import QUESTION_GROUNDEDNESS_CRITIQUE_PROMPT
from tqdm import tqdm


def extract_rating(text: str) -> dict:
    """
    Extracts the rating value from the provided text and returns it as a dictionary.

    :param text: The text containing the rating information.
    :return: A dictionary with the rating value as an integer.
    :raises ValueError: If the rating value is not found or is invalid.
    """
    print("Extracting rating from text...")
    print(text)
    match = re.search(r"Total rating:\s*(\d+)", text)
    if match:
        rating = int(match.group(1))
        return {"rating": rating}
    else:
        raise ValueError("Rating value not found in the text.")


def score_qa_list(qa_list: List[Dict[str, str]], client) -> List[Dict[str, str]]:
    """
    Scores the QA list based on a provided scoring function.
    This function evaluates each question-answer pair in the list using the OpenAI client
    :param qa_list: List of dictionaries containing questions and answers.
    :param client: An instance of OpenAIClient to call the LLM for scoring.
    :raises ValueError: If the QA list is empty or if any QA entry is missing
    :return: Filtered list of questions and answers.
    """
    qa_list = (
        qa_list.copy()
    )  # Create a copy of the list to avoid modifying the original
    for qa in tqdm(qa_list, desc="Processing QAs"):
        # Assuming each qa has 'question', 'answer', and 'chunk' keys
        if not all(key in qa for key in ["question", "answer", "chunk"]):
            raise ValueError(
                "Each QA entry must contain 'question', 'answer', and 'chunk' keys."
            )
        # Call the OpenAI client to evaluate the groundedness of the question-answer pair
        response = client.call_llm(
            model_name="gpt-4o-mini",
            prompt=QUESTION_GROUNDEDNESS_CRITIQUE_PROMPT.format(
                question=qa["question"], answer=qa["answer"], context=qa["chunk"]
            ),
        )

        rating = extract_rating(response["output"][0]["content"][0]["text"])
        qa["rating"] = rating["rating"]
    return qa_list
