from typing import List
from typing import Optional
from langchain_text_splitters import CharacterTextSplitter
from langchain_text_splitters import RecursiveCharacterTextSplitter


class SimpleSplitter:
    """
    A simple splitter that splits text into chunks based on a specified size.
    """

    def split_by_length(
        self,
        text: str,
        chunk_size: Optional[int] = 1000,
        chunk_overlap: Optional[int] = 200,
    ) -> List[str]:
        """
        Splits the input text into chunks of the specified length.
        This is based on the CharacterTextSplitter from langchain.
        The split is done by characters, and it allows for overlap between chunks.

        :param text: The text to be split.
        :param chunk_size: The maximum length of each chunk. Default is 1000 characters.
        :param chunk_overlap: The number of characters to overlap between chunks. Default is 200 characters.
        :raises ValueError: If the chunk size is less than or equal to zero.
        :return: A list of text chunks.
        """
        text_splitter = CharacterTextSplitter(
            separator="\n\n",
            chunk_size=chunk_size,
            chunk_overlap=chunk_overlap,
            length_function=len,
            is_separator_regex=False,
        )
        return text_splitter.split_text(text)

    def split_by_delimiter(self, text: str, delimiter: str = "\n") -> List[str]:
        """
        Splits the input text into chunks based on the specified delimiter.

        :param text: The text to be split.
        :param delimiter: The delimiter to use for splitting. Default is newline character.
        :return: A list of text chunks.
        """
        return [line.strip() for line in text.split(delimiter) if line.strip()]

    def split_by_token(
        self,
        text: str,
        chunk_size: Optional[int] = 1000,
        chunk_overlap: Optional[int] = 200,
    ) -> List[str]:
        """
        Splits the input text into chunks based on the specified token size.
        This is a placeholder for future implementation.

        :param text: The text to be split.
        :param token_size: The maximum number of tokens in each chunk. Default is 1000 tokens.
        :return: A list of text chunks.
        """
        text_splitter = CharacterTextSplitter.from_tiktoken_encoder(
            encoding_name="cl100k_base",
            chunk_size=chunk_size,
            chunk_overlap=chunk_overlap,
        )
        texts = text_splitter.split_text(text)
        if texts:
            return texts
        else:
            return []

    def split_by_text_structure(
        self,
        text: str,
        chunk_size: Optional[int] = 1000,
        chunk_overlap: Optional[int] = 500,
    ) -> List[str]:
        """
        Splits the input text into chunks based on the structure of the text.

        :param text: The text to be split.
        :param chunk_size: The maximum length of each chunk. Default is 1000 characters.
        :param chunk_overlap: The number of characters to overlap between chunks. Default is 500 characters.
        :return: A list of text chunks.
        """
        text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=chunk_size,
            chunk_overlap=chunk_overlap,
        )
        texts = text_splitter.split_text(text)
        return texts

    def get_chunks(self, text: str, method: str = "length", **kwargs) -> List[str]:
        """
        Splits the text based on the specified method.

        :param text: The text to be split.
        :param method: The method to use for splitting ('length' or 'delimiter').
        :return: A list of text chunks.
        :raises ValueError: If the method is not supported.
        """
        if method == "length":
            return self.split_by_length(
                text,
                chunk_size=kwargs.get("chunk_size", 1000),
                chunk_overlap=kwargs.get("chunk_overlap", 200),
            )
        elif method == "delimiter":
            return self.split_by_delimiter(
                text, delimiter=kwargs.get("delimiter", "\n")
            )
        elif method == "token":
            return self.split_by_token(
                text,
                chunk_size=kwargs.get("chunk_size", 1000),
                chunk_overlap=kwargs.get("chunk_overlap", 200),
            )
        elif method == "text_structure":
            return self.split_by_text_structure(
                text,
                chunk_size=kwargs.get("chunk_size", 1000),
                chunk_overlap=kwargs.get("chunk_overlap", 500),
            )
        else:
            raise ValueError(f"Unsupported splitting method: {method}")
