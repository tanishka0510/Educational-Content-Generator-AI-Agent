"""
Base Loader

Every document loader must inherit from this class.

Each loader must implement the load() method.
"""

from abc import ABC, abstractmethod


class BaseLoader(ABC):
    """
    Abstract base class for all document loaders.
    """

# Why use an Abstract Base Class?
#Suppose you accidentally write:  class PDFLoader:
#                                  pass
#There is no load() function.
#Your project will fail later.
#With an abstract class:   Python forces you to implement:
#Otherwise you'll immediately get an error. This prevents bugs.


    @abstractmethod
    def load(self, file_path: str) -> str:
        """
        Extract text from the given source.

        Parameters
        ----------
        file_path : str
            Path of the file or source.

        Returns
        -------
        str
            Extracted raw text.
        """
        pass