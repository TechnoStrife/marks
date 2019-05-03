from django.urls import include, path
from rest_framework import routers
from rest_framework.schemas import get_schema_view

from api import views

router = routers.DefaultRouter()
router.register('user', views.UserViewSet)
router.register('period', views.PeriodViewSet)
router.register('teacher', views.TeacherViewSet)
router.register('class', views.ClassViewSet)
router.register('subject-type', views.SubjectTypeViewSet)
router.register('subject', views.SubjectViewSet)
router.register('student', views.StudentViewSet)
router.register('lesson', views.LessonViewSet)
# router.register('mark', views.MarkViewSet)

schema_view = get_schema_view(title='Marks API')

urlpatterns = [
    path('summary/', include('api.summary.urls')),
    path('auth/', include('rest_framework.urls', namespace='rest_framework')),
    path('schema/', schema_view),
    path('', include(router.urls)),
]
