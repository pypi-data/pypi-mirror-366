import abc
from typing import Generic, TypeVar

Source = TypeVar("Source")
Target = TypeVar("Target")


class TranslationError(Exception):
    """Base exception for errors occurring during translation."""


class Translator(abc.ABC, Generic[Source, Target]):
    """
    Abstract base class for a Translator.
    A Translator is responsible for converting an object of a source type
    to an object of a target type.
    """

    @abc.abstractmethod
    def translate(self, source: Source) -> Target:
        """
        Translates a source object into a target object.

        Args:
            source: The object to translate.

        Returns:
            The translated object of the target type.

        Raises:
            TranslationError: If an error occurs during translation.
        """
        raise NotImplementedError

    async def translate_async(self, source: Source) -> Target:
        """
        Asynchronously translates a source object into a target object.
        By default, this calls the synchronous translate method.
        Subclasses can override this for genuine async translation logic.

        Args:
            source: The object to translate.

        Returns:
            The translated object of the target type.

        Raises:
            TranslationError: If an error occurs during translation.
        """
        # Default implementation for convenience if the translation is inherently sync
        # but needs to be called in an async context.
        # For true async I/O bound translations, this should be overridden.
        try:
            return self.translate(source)
        except TranslationError:
            raise
        except Exception as e:
            # Wrap other exceptions to conform to the expected error type
            raise TranslationError(f"Unhandled error during translation: {e}") from e
