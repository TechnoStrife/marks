from django.urls import path

from frontend.views import test

urlpatterns = [
    path(r'', test),
]
