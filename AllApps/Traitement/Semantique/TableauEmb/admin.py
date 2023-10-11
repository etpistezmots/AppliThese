from django.contrib import admin
from .models import FastText, FastTextR, Glove, GloveR, Word2Vec, Word2VecR

# Register your models here.

admin.site.register(Word2Vec)
admin.site.register(Word2VecR)
admin.site.register(Glove)
admin.site.register(GloveR)
admin.site.register(FastText)
admin.site.register(FastTextR)