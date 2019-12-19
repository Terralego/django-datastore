import base64
import binascii
import logging

import magic
from django.core.files.base import ContentFile
from django.core.files.uploadedfile import UploadedFile
from django.db.models.fields.files import FieldFile
from rest_framework import serializers

logger = logging.getLogger(__name__)


class FileBase64Field(serializers.FileField):
    def to_representation(self, value):
        if not value:
            return None

        if not isinstance(value, FieldFile):
            raise TypeError(
                f'Expect a django FieldFile, instead get {type(value)}'
            )

        with value.open() as f:
            content = f.read()
            return (f'data:{magic.from_buffer(content, mime=True)};'
                    f'base64,{(base64.b64encode(content)).decode("utf-8")}')

    def to_internal_value(self, data):
        try:
            content_type = data.split(":", 1)[1].split(";", 1)[0]
            encoded = data.split(",", 1)[1]

        # Caught the error to log it then re-raised it
        except IndexError:
            logger.warning(
                f"cannot read document {data}"
            )
            raise serializers.ValidationError(
                'document field must be "data:<mime>;base64,<string>" format'
            )

        else:
            try:
                decoded = base64.b64decode(encoded)
                return UploadedFile(
                    ContentFile(decoded),
                    content_type=content_type
                )
            # Caught the error to log it then re-raised it
            except binascii.Error:
                logger.warning(f'{data} is not a base64 format')
                raise serializers.ValidationError(
                    f'expected a base64, get instead {type(data)}'
                )
