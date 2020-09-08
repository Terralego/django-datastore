import logging

from rest_framework import serializers

from .fields import FileBase64Field, FileBase64UrlField
from .models import DataStore, RelatedDocument

logger = logging.getLogger(__name__)


class DataStoreSerializer(serializers.ModelSerializer):
    class Meta:
        model = DataStore
        fields = '__all__'
        read_only_fields = ('key', )


class RelatedDocumentSerializer(serializers.ModelSerializer):
    document = FileBase64Field()

    class Meta:
        model = RelatedDocument
        fields = ('key', 'document', 'properties')


class RelatedDocumentUrlSerializer(RelatedDocumentSerializer):
    document = FileBase64UrlField()


class RelatedDocumentPDFSerializer(RelatedDocumentSerializer):
    document = serializers.FileField(use_url=False)


class RelatedDocumentFileSerializer(RelatedDocumentSerializer):
    document = serializers.FileField()
