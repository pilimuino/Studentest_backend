from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from .models import Document, Question, Answer
from .serializers import DocumentSerializer, QuestionSerializer



class DocumentViewSet(viewsets.ModelViewSet):
    queryset = Document.objects.all()
    serializer_class = DocumentSerializer

    @action(detail=True, methods=['post'], url_path='generate_test')
    def generate_test(self, request, pk=None, serializer=None):
        document = self.get_object()
        questions = document.generate_questions()
        question_serializer = QuestionSerializer(questions, many=True)
        return Response({'questions': question_serializer.data}, status=status.HTTP_200_OK)

    def get_queryset(self):
        return Document.objects.prefetch_related('questions', 'questions__answers').all()

