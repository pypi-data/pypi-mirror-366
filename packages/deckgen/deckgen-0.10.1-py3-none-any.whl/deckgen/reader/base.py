from abc import ABC
from abc import abstractmethod


class BaseReader(ABC):
    """
    Base class for reading content from Different Sources.
    """

    @abstractmethod
    def get_content(self):
        """
        Returns the content read from the source.
        This method should be implemented by subclasses to provide specific content retrieval logic.
        :return: The content read from the source.
        """
        pass

    def get_content_stream(self):
        """
        Returns a stream of content read from the source.
        This method should be implemented by subclasses to provide specific content streaming logic.
        :return: A stream of content read from the source.
        """
        pass
