from rest_framework.views import exception_handler
from rest_framework.response import Response
from rest_framework import status


def standard_exception_handler(exc, context):
    response = exception_handler(exc, context)
    if response is not None:
        response.data = {
            "success": False,
            "error": {
                "code": getattr(exc, "code", "error"),
                "message": str(exc),
            },
        }
    return response
