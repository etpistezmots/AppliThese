from django.contrib import admin
from .models import FastTextRExplo, GloveRExplo, Word2VecRExplo

# Register your models here.

admin.site.register(Word2VecRExplo)
admin.site.register(GloveRExplo)
admin.site.register(FastTextRExplo)