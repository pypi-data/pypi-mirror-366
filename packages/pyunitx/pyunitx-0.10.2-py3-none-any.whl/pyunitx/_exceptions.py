class UnitException(Exception):
    pass


class OperationError(UnitException, TypeError):
    def __init__(self, operation, left, right):
        self.operation = operation
        self.left = left
        self.right = right

    def __repr__(self):
        return f"Cannot {self.operation} {self.left} and {self.right}"


class ImplicitConversionError(UnitException, TypeError):
    def __init__(self, source, dest):
        self.source = source
        self.dest = dest

    def __repr__(self):
        return f"Will not implicitly convert {self.source} to {self.dest}"
