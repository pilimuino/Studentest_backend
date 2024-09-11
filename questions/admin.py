from django.contrib import admin
from questions.models import Document, Question, Answer


admin.site.register(Document)
admin.site.register(Question)
admin.site.register(Answer)
