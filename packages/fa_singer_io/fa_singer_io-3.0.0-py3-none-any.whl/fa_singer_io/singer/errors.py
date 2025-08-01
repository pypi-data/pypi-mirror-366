class MissingKeys(Exception):
    def __init__(self, keys: frozenset[str], at: str) -> None:
        """MissingKeys error."""
        super().__init__(f"{keys} at {at}")
