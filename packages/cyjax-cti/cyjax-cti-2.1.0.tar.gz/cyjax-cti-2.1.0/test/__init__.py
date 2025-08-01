
api_responses = {
    401: {'reason': 'Unauthorized',
          'message': 'Unauthenticated',
          'code': 401},
    403: {'reason': 'Forbidden',
          'message': 'Forbidden',
          'code': 403},
    404: {'reason': 'Not Found',
          'message': 'Not found',
          'code': 404},
    422: {'reason': 'Validation error',
          'message': 'Validation error: Missing login param',
          'code': 422},
    429: {'reason': 'Too Many Requests',
          'message': 'Too Many Requests',
          'code': 429}
}
