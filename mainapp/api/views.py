from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters, status, viewsets
from rest_framework.decorators import action
from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response

from mainapp.models import Faculty, Teacher, University
from .serializers import FacultySerializer, ResultSerializer, TeacherSerializer, UniverSerializer


class Pagination(PageNumberPagination):
    page_size = 100
    page_size_query_param = 'page_size'


class UniverViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = University.objects.all()
    serializer_class = UniverSerializer


class FacultyViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Faculty.objects.all()
    serializer_class = FacultySerializer


class TeacherViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Teacher.objects.all()
    serializer_class = TeacherSerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    pagination_class = Pagination
    filterset_fields = ['univer', 'group__faculty']
    search_fields = ['name']

    @action(detail=True)
    def result(self, request, pk=None):
        teacher = self.get_object()
        faculty_id = request.query_params.get('faculty_id', None)
        if faculty_id is None:
            return Response("Provide faculty_id query param", status=status.HTTP_400_BAD_REQUEST)
        return Response(ResultSerializer.get_result(teacher, faculty_id))

