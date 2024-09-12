from django.db import transaction
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from .models import Document, Question, Answer
from .serializers import DocumentSerializer, QuestionSerializer
import logging

logger = logging.getLogger(__name__)


class DocumentViewSet(viewsets.ModelViewSet):
    queryset = Document.objects.all()
    serializer_class = DocumentSerializer

    @action(detail=True, methods=['post'], url_path='generate_test')
    @transaction.atomic
    def generate_test(self, request, pk=None):
        try:
            document = self.get_object()
            logger.info(f"Generando test para documento {document.id}")

            questions = document.generate_questions()
            logger.info(f"Número de preguntas generadas: {len(questions)}")

            # Verificar si las preguntas se guardaron en la base de datos
            db_questions = Question.objects.filter(document=document)
            logger.info(f"Número de preguntas en la base de datos: {db_questions.count()}")

            question_serializer = QuestionSerializer(db_questions, many=True)
            return Response({'questions': question_serializer.data}, status=status.HTTP_200_OK)
        except Exception as e:
            logger.error(f"Error al generar test: {str(e)}")
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def get_queryset(self):
        return Document.objects.prefetch_related('questions', 'questions__answers').all()



