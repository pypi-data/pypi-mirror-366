import genanki
from typing import List
from deckgen.utils.files import read_yaml
from deckgen.utils.files import get_root_directory
import random 
def get_anki_model(model_name: str) -> genanki.Model:
    """
    Gets a genanki Model for question-answer pairs.
    This model can be used to create Anki notes with questions and answers.

    :param model_name: The name of the model to retrieve.
    :return: A genanki.Model object.
    :raises ValueError: If the model name is not found in the configuration.
    """

    root_dir = get_root_directory()
    model_path = root_dir / "configs" / "anki" / "models.yaml"

    model_config = read_yaml(model_path)
    models = model_config.get("models", {})
    if model_name not in models.keys():
        raise ValueError(f"Model '{model_name}' not found in {model_path}.")

    model_id = models[model_name]["model_id"]
    model = genanki.Model(
        model_id,
        models[model_name]["name"],
        fields=models[model_name]["fields"],
        templates=models[model_name]["templates"]
    )

    return model

def generate_note(question: str, answer: str, model: genanki.Model) -> genanki.Note:
    """
    Generates a genanki Note object from a question and answer.

    :param question: The question text.
    :param answer: The answer text.
    :param model: The genanki Model to use for the note.
    :return: A genanki.Note object.
    """
    return genanki.Note(model=model, fields=[question, answer])


def generate_deck(
    notes: List[genanki.Note], deck_name: str
) -> genanki.Deck:
    """
    Generates a genanki Deck from a list of notes.

    :param notes: A list of genanki.Note objects.
    :param deck_name: The name of the deck.
    :return: A genanki.Deck object containing the notes.
    """
    deck_id = random.randint(1 << 30, 1 << 31)
    deck = genanki.Deck(deck_id, deck_name)
    for note in notes:
        deck.add_note(note)
    return deck
