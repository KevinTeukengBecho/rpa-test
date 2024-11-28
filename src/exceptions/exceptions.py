"""Module for custom exceptions"""


class ScrapeException(Exception):
    def __init__(self, message):
        super().__init__(message)
        self.message = message


class SearchPhraseContainsNoResultsException(ScrapeException):
    pass


class NewsCategoryNotFoundException(ScrapeException):
    def __init__(self, category):
        self.message = f"Selected news category '{category}' does not exist. Please specify a valid category."
        super().__init__(self.message)


class UnexpectedEndOfNavigationException(ScrapeException):
    def __init__(self):
        self.message = (
            "An unexpected website error occurred while trying to fetch more news."
        )
        super().__init__(self.message)


class MissingArgumentException(ScrapeException):
    def __init__(self, argument):
        self.message = f"Please specify the argument {argument} through work items on the Robocorp cloud."
        super().__init__(self.message)


class InvalidArgumentException(ScrapeException):
    def __init__(self, argument, value):
        self.message = f"Argument {argument}  has an invalid value {value}"
        super().__init__(self.message)
