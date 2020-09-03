from pathlib import Path

from django.contrib.auth.models import Group, Permission
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
try:
    from django.db.models import JSONField
except ImportError:  # TODO Remove when dropping Django releases < 3.1
    from django.contrib.postgres.fields.jsonb import JSONField
from django.db import models
from django.db.models.manager import BaseManager

from .managers import DataStoreQuerySet


class DataStore(models.Model):
    key = models.CharField(max_length=255, primary_key=True, )
    value = JSONField(default=dict, blank=False)

    objects = BaseManager.from_queryset(DataStoreQuerySet)()

    class Meta:
        ordering = ['key']


class DataStorePermission(models.Model):
    group = models.ForeignKey(Group, on_delete=models.CASCADE)
    prefix = models.CharField(max_length=255, blank=False, null=False)
    permission = models.ForeignKey(Permission, on_delete=models.CASCADE)

    class Meta:
        ordering = ['prefix']
        permissions = (
            ('can_read_datastore', "Is able to read all datastore's elements"),
            ('can_readwrite_datastore', 'Is able to write in datastore'),
        )


def related_document_path(instance, filename):
    filename = Path(filename)
    return (f'documents/'
            f'{instance.content_type.app_label}_{instance.content_type.model}/'
            f'{instance.object_id}/{instance.key}{filename.suffix}')


class RelatedDocument(models.Model):
    key = models.CharField(max_length=255, blank=False)
    content_type = models.ForeignKey(ContentType, on_delete=models.PROTECT)
    object_id = models.PositiveIntegerField()
    linked_object = GenericForeignKey('content_type', 'object_id')
    document = models.FileField(upload_to=related_document_path, null=False)
    properties = JSONField(default=dict)

    class Meta:
        ordering = ['key']
        unique_together = ('key', 'content_type', 'object_id')
