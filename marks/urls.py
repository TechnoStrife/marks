import django
from django.contrib import admin
from django.contrib.staticfiles.urls import staticfiles_urlpatterns
from django.urls import include, path, re_path
from django.views.generic import RedirectView
from django.contrib.staticfiles.views import serve as serve_static

from marks import settings
from frontend.views import test

urlpatterns = [
    path(r'favicon.ico', RedirectView.as_view(url='/static/images/favicon.ico'), name='favicon'),
    path(r'admin/', admin.site.urls),
    path(r'api/', include('api.urls')),
    # path(r'', include('frontend.urls')),
    path(r'', test),
    re_path(r'^(?!static)(?P<url>.*)$', test),
]

# handler404 = 'school_environ.views.handler404'
# handler500 = 'school_environ.views.handler500'
