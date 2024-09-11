from django.db import models
import fitz
from transformers import T5ForConditionalGeneration, T5Tokenizer
import torch

class DocumentManager:
    def __init__(self):
        self.model_name = "google/flan-t5-base"
        self.tokenizer = T5Tokenizer.from_pretrained(self.model_name)
        self.model = T5ForConditionalGeneration.from_pretrained(self.model_name)

    def generate_questions(self, text):
        input_text = self.create_prompt(text)
        input_ids = self.tokenizer(input_text, return_tensors="pt", max_length=1024, truncation=True).input_ids
        outputs = self.model.generate(input_ids, max_length=512, num_return_sequences=1, num_beams=4)
        generated_text = self.tokenizer.decode(outputs[0], skip_special_tokens=True)
        return self.parse_generated_text(generated_text)

    def create_prompt(self, text):
        return f"""
        Estructura un examen basado en el siguiente contenido: "{text}".
        El examen debe contener:
        1. Cinco preguntas de selección múltiple, cada una con cuatro opciones. Una de estas opciones debe ser la respuesta correcta.
        2. Cinco preguntas de verdadero o falso. Incluye también las respuestas correctas.
        
        Formato para preguntas de selección múltiple:
        Q: [Pregunta]
        A) [Opción A]
        B) [Opción B]
        C) [Opción C]
        D) [Opción D]
        Respuesta correcta: [Letra de la opción correcta]

        Formato para preguntas de verdadero o falso:
        Q: [Pregunta]
        Respuesta: [Verdadero/Falso]
        """

    def parse_generated_text(self, generated_text):
        questions = []
        current_question = None

        for line in generated_text.split('\n'):
            line = line.strip()
            if line.startswith('Q:'):
                if current_question:
                    questions.append(current_question)
                current_question = {'text': line[2:].strip(), 'answers': [], 'type': 'unknown'}
            elif line.startswith(('A)', 'B)', 'C)', 'D)')):
                current_question['type'] = 'multiple_choice'
                current_question['answers'].append({
                    'text': line[2:].strip(),
                    'is_correct': False
                })
            elif line.startswith('Respuesta correcta:'):
                correct_answer = line.split(':')[1].strip()
                for answer in current_question['answers']:
                    if answer['text'].startswith(correct_answer):
                        answer['is_correct'] = True
            elif line.startswith('Respuesta:'):
                current_question['type'] = 'true_false'
                is_true = 'verdadero' in line.lower()
                current_question['answers'] = [
                    {'text': 'Verdadero', 'is_correct': is_true},
                    {'text': 'Falso', 'is_correct': not is_true}
                ]

        if current_question:
            questions.append(current_question)

        return questions


document_manager = DocumentManager()


class Document(models.Model):
    file = models.FileField(upload_to='documents/')
    uploaded_at = models.DateTimeField(auto_now_add=True)

    def extract_text(self):
        with fitz.open(self.file.path) as doc:
            text = ""
            for page in doc:
                text += page.get_text()
        return text

    def generate_questions(self):
        text = self.extract_text()
        questions = document_manager.generate_questions(text)
        self.save_questions(questions)
        return questions

    def save_questions(self, questions):
        for q_data in questions:
            question = Question.objects.create(
                document=self,
                text=q_data['text'],
                question_type=q_data['type']
            )
            for ans_data in q_data['answers']:
                Answer.objects.create(
                    question=question,
                    text=ans_data['text'],
                    is_correct=ans_data['is_correct']
                )


class Question(models.Model):
    QUESTION_TYPES = (
        ('multiple_choice', 'Multiple Choice'),
        ('true_false', 'True/False'),
    )
    document = models.ForeignKey(Document, related_name='questions', on_delete=models.CASCADE)
    text = models.TextField()
    question_type = models.CharField(max_length=20, choices=QUESTION_TYPES)


class Answer(models.Model):
    question = models.ForeignKey(Question, related_name='answers', on_delete=models.CASCADE)
    text = models.CharField(max_length=255)
    is_correct = models.BooleanField(default=False)



