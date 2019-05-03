from django.contrib import admin
from django.urls import include, path
from django.views.generic import RedirectView

urlpatterns = [
    path(r'favicon.ico', RedirectView.as_view(url='/static/images/favicon.ico'), name='favicon'),
    path(r'admin/', admin.site.urls),
    path(r'api/', include('api.urls')),
    path(r'', include('frontend.urls'))
]

# handler404 = 'school_environ.views.handler404'
# handler500 = 'school_environ.views.handler500'
