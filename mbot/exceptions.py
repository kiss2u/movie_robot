class MovieBotException(Exception):
    pass


class IllegalAccessException(MovieBotException):
    pass


class IPLimitException(MovieBotException):
    pass


class MediaServerError(MovieBotException):
    pass

class RateLimitException(MovieBotException):
    pass