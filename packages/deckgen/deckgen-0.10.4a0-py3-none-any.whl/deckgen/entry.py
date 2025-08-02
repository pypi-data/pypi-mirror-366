from deckgen.decks.generator import DeckGen

# from deckgen.pipelines.qa_pipeline import QAToolKit
from deckgen.reader.file_reader import FileReader

# from prompteng.prompts.parser import QAParser
from dotenv import load_dotenv
from typing import List
import os

import genanki


def main():
    """
    Main function to run the DeckGen application.
    """
    # Load environment variables from .env file
    load_dotenv()
    reader = FileReader("test.txt")
    content = reader.get_content()
    print("Content read from file:", content)
    deck_gen = DeckGen(input_text=content)
    deck = deck_gen.generate_deck(
        deck_name="Test Deck", deck_description="This is a test deck."
    )
    print("Generated Deck:", deck.name)
    print(deck.list_cards())
    # deck.generate_anki_deck("azure_functions.apkg")
