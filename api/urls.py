from django.urls import include, path
from rest_framework import routers
from api import views

router = routers.DefaultRouter()
router.register('users', views.UserViewSet)
router.register('teachers', views.TeacherViewSet)
router.register('classes', views.ClassViewSet)
router.register('students', views.StudentViewSet)

urlpatterns = [
    path('summary/', include('api.summary.urls')),
    path('', include(router.urls)),
    path('auth/', include('rest_framework.urls', namespace='rest_framework'))
]
