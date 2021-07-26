from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters, routers, viewsets, serializers, decorators, pagination, response

from mainapp.models import Faculty, Teacher, University


class Pagination(pagination.PageNumberPagination):
    page_size = 100
    page_size_query_param = 'page_size'


class UniverViewSet(viewsets.ReadOnlyModelViewSet):
    class UniverSerializer(serializers.ModelSerializer):
        class Meta:
            model = University
            fields = ['id', 'name']

    queryset = University.objects.all()
    serializer_class = UniverSerializer


class FacultyViewSet(viewsets.ReadOnlyModelViewSet):
    class FacultySerializer(serializers.ModelSerializer):
        class Meta:
            model = Faculty
            fields = ['id', 'name']

    queryset = Faculty.objects.all()
    serializer_class = FacultySerializer


class TeacherViewSet(viewsets.ReadOnlyModelViewSet):
    class TeacherSerializer(serializers.ModelSerializer):
        class Meta:
            model = Teacher
            fields = ['name', 'slug']
            lookup_field = 'slug'

    queryset = Teacher.objects.all()
    serializer_class = TeacherSerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    pagination_class = Pagination
    filterset_fields = ['univer', 'group__faculty']
    search_fields = ['name']
    lookup_field = 'slug'

    @decorators.action(detail=True)
    def result(self, request, pk=None):
        return response.Response(self.get_object().get_results())


router = routers.DefaultRouter()
router.register(r'teacher', TeacherViewSet)
router.register(r'university', UniverViewSet)
router.register(r'faculty', FacultyViewSet)
