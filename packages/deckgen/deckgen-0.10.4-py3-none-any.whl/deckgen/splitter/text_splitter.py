from typing import List
from typing import Optional
from deckgen.splitter.document import Document
from deckgen.splitter.splitters import SimpleSplitter


class TextSplitter:
    """
    A splitter that splits text documents into smaller parts.
    This class extends the BaseSplitter and implements the split method.
    """

    def __init__(self, document):
        """
        Initializes the TextSplitter with the provided document.

        :param document: The document to be split.
        """
        # NOTE: Implement the case when the document is a stream
        self.document = document

    def split_text(
        self,
        method: Optional[str] = "length",
        chunk_size: Optional[int] = 100,
        chunk_overlap: Optional[int] = 0,
        delimiter: Optional[str] = "\n\n",
    ) -> List[Document]:
        """
        Splits the document into smaller parts based on a specified logic.
        For now, it returns the document as a single part.

        :return: A list containing the original document.
        :raises ValueError: If the method is not supported.
        """
        # factory method to get the splitter
        splitter = TextSplitterFactory.get_splitter(method)
        # if the splitter is None, raise an error
        if splitter is None:
            raise ValueError(f"Splitter method '{method}' is not supported.")

        # get a list of strings based on the method
        documents = splitter.get_chunks(
            text=self.document,
            method=method,
            chunk_size=chunk_size,
            chunk_overlap=chunk_overlap,
            delimiter=delimiter,
        )

        # convert the list of strings to a list of Document objects
        documents = [Document(content=doc) for doc in documents]
        return documents


class TextSplitterFactory:
    """
    Factory class to create instances of TextSplitter based on the method.
    """

    @classmethod
    def get_splitter(cls, method: str) -> Optional[TextSplitter]:
        """
        Returns an instance of TextSplitter based on the specified method.

        :param method: The method to be used for splitting.
        :return: An instance of TextSplitter or None if the method is not supported.
        """
        if (
            method == "length"
            or method == "delimiter"
            or method == "token"
            or method == "text_structure"
        ):
            return SimpleSplitter()
        # Add more methods as needed
        return None
