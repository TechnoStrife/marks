from django.urls import include, path
from rest_framework import routers

from api.summary import views

router = routers.DefaultRouter()
router.register('classes', views.ClassAvgMarkViewSet)
router.register('subjects', views.SubjectAvgMarkViewSet)
router.register('teachers', views.TeacherAvgMarkViewSet)

urlpatterns = [
    path('', include(router.urls)),
]
