from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django.db import transaction
from .models import Document
from .serializers import DocumentSerializer, QuestionSerializer
from .services import QuestionGenerationService
import logging

logger = logging.getLogger(__name__)


class DocumentViewSet(viewsets.ModelViewSet):
    queryset = Document.objects.all()
    serializer_class = DocumentSerializer

    @action(detail=True, methods=['post'], url_path='generate_test')
    def generate_test(self, request, pk=None):
        try:
            document = self.get_object()
            logger.info(f"Generating test for document {document.id}")

            question_service = QuestionGenerationService(document)
            saved_questions = question_service.generate_questions()

            question_serializer = QuestionSerializer(saved_questions, many=True)
            return Response({'questions': question_serializer.data}, status=status.HTTP_200_OK)

        except ValueError as ve:
            logger.error(f"Value error in test generation: {str(ve)}")
            return Response({'error': str(ve)}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            logger.error(f"Unexpected error in test generation: {str(e)}")
            return Response({'error': 'An unexpected error occurred'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def get_queryset(self):
        return Document.objects.prefetch_related('questions', 'questions__answers').all()

