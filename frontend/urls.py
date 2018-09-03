from django.conf.urls import url
from frontend.views import test

urlpatterns = [
    url(r'^', test),
]