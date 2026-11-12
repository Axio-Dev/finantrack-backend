from django.core.exceptions import ValidationError as DjangoValidationError
from rest_framework.exceptions import NotFound
from rest_framework.exceptions import ValidationError as ApiValidationError
from rest_framework.serializers import as_serializer_error
from rest_framework.views import exception_handler as drf_exception_handler

from common.exceptions import ResourceNotFound


def api_exception_handler(exc, context):
    if isinstance(exc, ResourceNotFound):
        exc = NotFound(detail=str(exc))

    elif isinstance(exc, DjangoValidationError):
        exc = ApiValidationError(detail=as_serializer_error(exc))

    return drf_exception_handler(exc, context)
