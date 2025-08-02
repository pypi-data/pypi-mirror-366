from typing import Optional
from typing import List
from typing import Dict

from deckgen.decks.base import Deck
from deckgen.decks.base import Card


class DeckGen:
    def __init__(self):
        """
        Initializes the DeckGen class.
        """
        pass

    def generate_deck(
        self,
        qa_list: List[Dict[str, str]],
        deck_name: Optional[str],
        deck_description: Optional[str] = None,
    ) -> List[Dict[str, str]]:
        """
        Generates a deck based on the input text.
        :return: List of generated cards. Each card is a dictionary with 'front' and 'back' keys.
        """
        deck = Deck(name=deck_name, description=deck_description)
        for qa in qa_list:
            card = Card(front=qa["question"], back=qa["answer"])
            deck.add_card(card)

        return deck
