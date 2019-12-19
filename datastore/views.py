from rest_framework import viewsets
from rest_framework.renderers import JSONRenderer
from rest_framework.response import Response
from rest_framework.status import HTTP_409_CONFLICT

from .models import DataStore
from .permissions import IsAuthenticatedAndDataStoreAllowed
from .serializers import DataStoreSerializer


class DataStoreViewSet(viewsets.ModelViewSet):
    renderer_classes = (JSONRenderer, )

    permission_classes = (IsAuthenticatedAndDataStoreAllowed, )
    serializer_class = DataStoreSerializer
    lookup_field = 'key'
    lookup_value_regex = '[^/]+'

    def get_queryset(self):
        return DataStore.objects.get_datastores_for_user(self.request.user)

    def update(self, request, key=None, *args, **kwargs):
        obj = self.get_object()

        serializer = self.get_serializer(obj, data={'value': request.data})

        serializer.is_valid(raise_exception=True)
        serializer.save()

        return Response(serializer.data.get('value'))

    def post(self, request, *args, **kwargs):
        attrs = {self.lookup_field: kwargs.get(self.lookup_field)}

        obj = DataStore(**attrs)
        serializer = self.get_serializer(obj, data={'value': request.data})
        self.check_object_permissions(request, obj)

        if DataStore.objects.filter(**attrs).exists():
            return Response(status=HTTP_409_CONFLICT)

        serializer.is_valid(raise_exception=True)
        serializer.save()

        return Response(serializer.data.get('value'))
