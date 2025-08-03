class ParserError(Exception):
    pass


class ExtractExpressionError(Exception):
    pass


class ConnectTimeout(Exception):
    pass


class MaxRetryError(Exception):
    pass


class ConnectError(Exception):
    pass
