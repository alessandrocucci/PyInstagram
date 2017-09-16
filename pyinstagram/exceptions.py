class PyInstagramException(Exception):
    pass


class OAuthException(PyInstagramException):
    def __init__(self, message):
        self.message = message
        super().__init__(message)
