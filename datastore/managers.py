from django.db.models import Q, QuerySet

from . import models as ds_models


class DataStoreQuerySet(QuerySet):
    def get_datastores_for_user(self, user, perms=None):
        prefixes = self._get_user_prefixes_query(user, perms)

        return self.filter(prefixes)

    @staticmethod
    def _get_user_prefixes_query(user, perms=None):
        prefixes_query = Q()
        query_args = {
            'group__in': user.groups.all(),
        }
        if perms:
            query_args['permission__in'] = perms

        permissions = ds_models.DataStorePermission.objects.filter(
            **query_args
        )
        if not permissions:
            return Q(key=None)

        for ds_perm in permissions:
            prefixes_query |= Q(key__startswith=ds_perm.prefix)

        return prefixes_query
