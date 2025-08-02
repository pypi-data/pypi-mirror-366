import argparse
from deckgen.decks.generator import DeckGen
from deckgen.reader.file_reader import FileReader
from deckgen.splitter.text_splitter import TextSplitter
from deckgen.pipelines.qa_pipeline import QAToolKit
from deckgen.pipelines.qa_pipeline import QAParser
from deckgen.pipelines.validate_qa import score_qa_list
from tqdm import tqdm
from typing import Optional
import os

from deckgen.utils.cli import define_generate_parser
from deckgen.utils.cli import define_env_parser

RATING_THRESHOLD = 3


def main():
    parser = argparse.ArgumentParser(
        prog="deckgen", description="Generate decks from text files."
    )

    subparsers = parser.add_subparsers(dest="command", required=True)

    generate_command = define_generate_parser(subparsers)
    env_command = define_env_parser(subparsers)

    # Parse the arguments
    args = parser.parse_args()

    if args.command == generate_command:
        print(f"Generating deck from {args.input_file} with name {args.name}")
        generate_deck_from_file(
            input_file=args.input_file,
            deck_name=args.name,
            dst=args.output,
            deck_description=None,  # Optional description can be added later
        )

    elif args.command == env_command:
        if not args.openai_api_key:
            raise ValueError("API key is required for authentication.")

        if args.openai_organization_id:
            print(f"Setting OpenAI organization ID to {args.openai_organization_id}")
            os.environ["OPENAI_API_ORGANIZATION"] = args.openai_organization_id

        if args.openai_project_id:
            print(f"Setting OpenAI project ID to {args.openai_project_id}")
            os.environ["OPENAI_API_PROJECT"] = args.openai_project_id

        print(f"Setting OpenAI API key.")
        os.environ["OPENAI_API_KEY"] = args.openai_api_key


def generate_deck_from_file(
    input_file: str,
    deck_name: str,
    dst: Optional[str] = None,
    deck_description: Optional[str] = None,
) -> None:
    """
    Generates a deck from the specified input file.

    :param input_file: Path to the input file.
    :param deck_name: Name of the deck to be generated.
    :param dst: Optional destination directory for the generated deck file.
        If not provided, the deck will be saved in the current directory.
    :param deck_description: Optional description for the deck.
    """
    reader = FileReader(input_file)
    content = reader.get_content()
    text_splitter = TextSplitter(document=content)
    chunks = text_splitter.split_text(
        method="length", chunk_overlap=100, chunk_size=500
    )

    qa_list = []
    qa_toolkit = QAToolKit()
    parser = QAParser()
    for chunk in tqdm(chunks, desc="Processing chunks"):
        content = chunk.get_content()
        topics = qa_toolkit.get_topics(content)
        qa_string = qa_toolkit.generate_qa_string(topics=topics, text=content)
        qa_list_ = parser.parse(qa_string)
        for qa in tqdm(qa_list_, desc="Processing QAs"):
            qa["chunk"] = content

        qa_list.extend(qa_list_)
    scored_list = score_qa_list(qa_list, client=qa_toolkit.openai_client)
    filtered_qa_list = [qa for qa in scored_list if qa["rating"] >= RATING_THRESHOLD]
    deck_gen = DeckGen()
    deck = deck_gen.generate_deck(
        qa_list=filtered_qa_list, deck_name=deck_name, deck_description=deck_description
    )

    print("Generated Deck:", deck.name)
    if not dst:
        dst = "output.apkg"
    deck.generate_anki_deck(dst)
