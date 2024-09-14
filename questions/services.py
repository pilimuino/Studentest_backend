import fitz
from transformers import T5ForConditionalGeneration, T5Tokenizer
import logging
from .models import Question, Answer
import random
logger = logging.getLogger(__name__)


class QuestionGenerationService:
    def __init__(self, document):
        self.document = document

    def extract_text(self):
        try:
            logger.info(f"Extrayendo texto de {self.document.file.path}")
            with fitz.open(self.document.file.path) as doc:
                text = ""
                for page in doc:
                    text += page.get_text()
            logger.info(f"Texto extraído, longitud: {len(text)}")
            return text
        except Exception as e:
            logger.error(f"Error al extraer texto: {str(e)}")
            raise

    def generate_questions(self, num_questions=10):
        model_name = "google/flan-t5-base"
        tokenizer = T5Tokenizer.from_pretrained(model_name)
        model = T5ForConditionalGeneration.from_pretrained(model_name)

        text = self.extract_text()
        sentences = [s.strip() for s in text.split('.') if len(s.strip()) > 20]
        questions = []

        for sentence in sentences:
            if len(questions) >= num_questions:
                break

            sentence = sentence.strip()
            if len(sentence) < 10:
                continue

            input_text = f"generate question: {sentence}"
            input_ids = tokenizer(input_text, return_tensors="pt", max_length=512, truncation=True).input_ids
            outputs = model.generate(input_ids, max_length=64, num_return_sequences=1, num_beams=4)
            question_text = tokenizer.decode(outputs[0], skip_special_tokens=True)

            if len(questions) % 2 == 0:
                question_type = 'multiple_choice'
                answers = self.generate_multiple_choice_answers(sentence)
            else:
                question_type = 'true_false'
                is_true = self.validate_true_false_question(sentence)  # Nueva función de validación
                answers = [
                    {'text': 'Verdadero', 'is_correct': is_true},
                    {'text': 'Falso', 'is_correct': not is_true}
                ]

            question = Question.objects.create(
                document=self.document,
                text=question_text,
                question_type=question_type
            )

            for answer in answers:
                Answer.objects.create(
                    question=question,
                    text=answer['text'],
                    is_correct=answer['is_correct']
                )

            questions.append(question)

        return questions
    def validate_true_false_question(self, sentence):
        # Puedes implementar una validación más sofisticada aquí
        return random.choice([True, False])

    def generate_multiple_choice_answers(self, context):
        words = context.split()
        correct_answer = random.choice(words)
        incorrect_options = random.sample([w for w in words if w != correct_answer], min(3, len(words) - 1))

        answers = [{'text': correct_answer, 'is_correct': True}]
        for option in incorrect_options:
            answers.append({'text': option, 'is_correct': False})

        random.shuffle(answers)
        return answers
    def parse_generated_text(self, generated_text):
        questions = []
        current_question = None
        lines = generated_text.split('\n')

        for line in lines:
            line = line.strip()
            if line and line[0].isdigit():  # Nueva pregunta
                if current_question:
                    questions.append(current_question)

                question_type = "multiple_choice" if any(line.startswith(f"{line[0]}.") for line in lines[lines.index(
                    line) + 1:lines.index(line) + 5]) else "true_false"
                current_question = {
                    'text': line[line.index('.') + 1:].strip(),
                    'type': question_type,
                    'answers': []
                }
            elif line.lower().startswith(("a)", "b)", "c)", "d)")):
                if current_question and current_question['type'] == "multiple_choice":
                    current_question['answers'].append({
                        'text': line[2:].strip(),
                        'is_correct': False
                    })
            elif line.lower().startswith("respuesta:"):
                if current_question:
                    correct_answer = line.split(':', 1)[1].strip()
                    if current_question['type'] == "multiple_choice":
                        for answer in current_question['answers']:
                            if answer['text'].lower().startswith(correct_answer.lower()):
                                answer['is_correct'] = True
                                break
                    else:  # true_false
                        is_true = "verdadero" in correct_answer.lower()
                        current_question['answers'] = [
                            {'text': 'Verdadero', 'is_correct': is_true},
                            {'text': 'Falso', 'is_correct': not is_true}
                        ]

        if current_question:
            questions.append(current_question)

        logger.info(f"Número de preguntas parseadas: {len(questions)}")
        for i, q in enumerate(questions):
            logger.info(f"Pregunta {i + 1}: {q['text']}")
            logger.info(f"Tipo: {q['type']}")
            logger.info(f"Respuestas: {q['answers']}")
            logger.info("---")

        return questions, None
    def save_questions(self, questions):
        saved_questions = []
        for q_data in questions:
            question = Question.objects.create(
                document=self.document,
                text=q_data['text'],
                question_type=q_data['type']
            )
            for ans_data in q_data['answers']:
                Answer.objects.create(
                    question=question,
                    text=ans_data['text'],
                    is_correct=ans_data['is_correct']
                )
            saved_questions.append(question)
        return saved_questions
