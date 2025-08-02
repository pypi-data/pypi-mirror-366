from deckgen.reader.base import BaseReader
from deckgen.reader.validations import validate_filepath
from pathlib import Path
from typing import List
from typing import Optional
from langchain_community.document_loaders import PyPDFLoader
from langchain_community.document_loaders import TextLoader
from langchain_core.documents.base import Document


class FileReader(BaseReader):
    """
    A reader that reads content from a file.
    For now, it reads the entire content of the file into memory.
    This is suitable for small files. For larger files, consider implementing a streaming approach.
    It allows only reading text files with a .txt extension.
    """

    def __init__(self, file_path: str):
        """
        Initializes the FileReader with the provided file path.

        :param file_path: The path to the file to be read.
        """
        self.file_path = file_path if isinstance(file_path, Path) else Path(file_path)
        validate_filepath(self.file_path)
        self.file_extension = self.file_path.suffix
        self.content = None

    def get_content(self, n_documents: Optional[int] = -1) -> str:
        """
        Returns the content read from the file.

        :param n_documents: The number of documents to read. Default is -1 (all documents).
        :raises ValueError: If the file is not a valid text file.
        :return: The content read from the file.
        """
        documents = self.get_documents()
        if not documents:
            raise ValueError("No documents found in the file.")
        if n_documents == -1 or n_documents > len(documents):
            n_documents = len(documents)
        self.content = self._join_documents(documents[:n_documents])
        return self.content

    def get_documents(self) -> List[Document]:
        """
        Returns the documents read from the file.

        :return: A list of documents read from the file.
        """
        loader = self.__get_loader()
        documents = []
        for page in loader.load():
            documents.append(page)

        return documents

    def __get_loader(self):
        """
        Returns the appropriate loader based on the file type.

        :return: A loader instance for the file type.
        """
        if self.file_extension == ".pdf":
            return PyPDFLoader(self.file_path)
        elif self.file_extension == ".txt":
            return TextLoader(self.file_path)

    def _join_documents(self, documents: List[Document]) -> str:
        """
        Joins the content of the documents into a single string.

        :param documents: A list of Document objects.
        :return: A string containing the joined content of the documents.
        """
        return "\n".join([doc.page_content for doc in documents]) if documents else ""
