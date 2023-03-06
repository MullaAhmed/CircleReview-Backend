import typing


class CohesiveError(Exception):
    def __init__(self, message: typing.Union[str, None], http_status: typing.Union[int, None], http_body: typing.Union[str, None], http_headers: typing.Union[typing.Dict[str, str], None]):
        super(CohesiveError, self).__init__(message)

        self._message = message
        self.http_body = http_body
        self.http_status = http_status
        self.http_headers = http_headers or {}

    def __str__(self):
        msg = self._message or "<empty message>"
        if self.http_status:
            return f'{self.http_status}: {msg}'
        else:
            return msg


class IdempotencyError(CohesiveError):
    pass


class APIError(CohesiveError):
    pass


class APIConnectionError(CohesiveError):
    pass


class AuthenticationError(CohesiveError):
    pass