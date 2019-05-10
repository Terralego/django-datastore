from rest_framework import routers

from .views import DataStoreViewSet

app_name = 'datastore'

router = routers.SimpleRouter()

router.register(r'datastore', DataStoreViewSet, base_name='datastore')

urlpatterns = router.urls
