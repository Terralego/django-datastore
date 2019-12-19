from rest_framework.permissions import SAFE_METHODS, IsAuthenticated

from .models import DataStorePermission


class IsAuthenticatedAndDataStoreAllowed(IsAuthenticated):
    def has_object_permission(self, request, view, obj):
        permissions = ['can_readwrite_datastore', ]

        if request.method in SAFE_METHODS:
            permissions.append('can_read_datastore')

        perms = DataStorePermission.objects.filter(
            permission__codename__in=permissions,
            group__in=request.user.groups.all()
        )

        return any([obj.key.startswith(perm.prefix) for perm in perms])
