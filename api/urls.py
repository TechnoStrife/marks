from django.conf.urls import url
from django.urls import include

urlpatterns = [
    url(r'^summary/', include('api.summary.urls'))
    # url(r'^', ),
]
