from django.urls import include, path
from rest_framework import routers

from . import views

router = routers.DefaultRouter()
router.register(r'teacher', views.TeacherViewSet)
router.register(r'university', views.UniverViewSet)
router.register(r'faculty', views.FacultyViewSet)

urlpatterns = [
    path('', include(router.urls)),
]
