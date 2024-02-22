class CollinearityError(Exception):
    def __init__(self, message: str = "The points are collinear"):
        self.message = message
        super().__init__(self.message)

    def __str__(self) -> str:
        return self.message


class ClassesComparisonError(Exception):
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
