from django.conf.urls import include, url
from django.contrib import admin
from django.contrib.auth import views as auth_views
from django.views.generic import RedirectView

admin.autodiscover()

models_urls = registry.register(DummyModel) + registry.register(MushroomSpot)

urlpatterns = [
    url(r'', include('datastore.urls', namespace='datastore',
                     app_name='datastore')),
    url(r'^home/$', RedirectView.as_view(url='/', permanent=True), name='home'),
    url(r'^login/$', auth_views.login, name='login'),
    url(r'^logout/$', auth_views.logout, {'next_page': '/'}, name='logout',),
]
