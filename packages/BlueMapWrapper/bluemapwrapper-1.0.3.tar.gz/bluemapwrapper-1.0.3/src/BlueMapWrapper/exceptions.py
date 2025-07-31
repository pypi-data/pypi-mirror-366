class MultipleMatches(Exception):
    """If multiple matches occur when there should not be"""
    def __init__(self, key: str, message:str="Multiple matches found"):
        self.message = f"{key}: {message}"
        super().__init__(self.message)