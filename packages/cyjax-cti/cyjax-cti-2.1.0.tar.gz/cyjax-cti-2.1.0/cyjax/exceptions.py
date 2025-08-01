from requests import RequestException


class ResponseErrorException(Exception):
    def __init__(self, status_code, msg):
        self.status_code = status_code
        self.msg = msg


class UnauthorizedException(RequestException):
    def __init__(self):
        super(UnauthorizedException, self).__init__('You are unauthorized to perform this request.')


class ForbiddenException(RequestException):
    def __init__(self):
        super(ForbiddenException, self).__init__('You do not have enough permission to access this resource.')


class NotFoundException(RequestException):
    def __init__(self):
        super(NotFoundException, self).__init__('Not found.')


class TooManyRequestsException(RequestException):
    def __init__(self):
        super(TooManyRequestsException, self).__init__('Too many requests sent.')


class ValidationException(RequestException):
    def __init__(self, json):
        error = json.get('message') if 'message' in json else 'Validation error'
        super(ValidationException, self).__init__(error)


class ApiKeyNotFoundException(Exception):
    def __init__(self):
        super(ApiKeyNotFoundException, self).__init__('API key not found. Please set API key.')


class InvalidDateFormatException(Exception):
    def __init__(self, msg):
        self.msg = msg
