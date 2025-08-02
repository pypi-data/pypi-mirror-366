class Document:
    """
    A document object that represents a document with additional functionality if needed.
    """

    def __init__(self, content: str):
        """
        Initializes the Document with content.

        :param content: The content of the document.
        """
        self.content = content

    def get_content(self) -> str:
        """
        Returns the content of the document.

        :return: The content of the document.
        """
        return self.content
