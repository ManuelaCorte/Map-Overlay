class CollinearityError(Exception):
    def __init__(self, message: str = "The points are collinear"):
        self.message = message
        super().__init__(self.message)

    def __str__(self) -> str:
        return self.message


class ClassComparisonError(Exception):
    def __init__(self, message: str = "The classes are different"):
        self.message = message
        super().__init__(self.message)

    def __str__(self) -> str:
        return self.message


class NotRunYetError(Exception):
    def __init__(self, message: str = "The algorithm has not been run yet"):
        self.message = message
        super().__init__(self.message)

    def __str__(self) -> str:
        return self.message


class DcelError(Exception):
    def __init__(self, message: str = "The DCEL is not valid"):
        self.message = message
        super().__init__(self.message)

    def __str__(self) -> str:
        return self.message


class OverlayError(Exception):
    def __init__(self, message: str = "The overlay is not valid"):
        self.message = message
        super().__init__(self.message)

    def __str__(self) -> str:
        return self.message
