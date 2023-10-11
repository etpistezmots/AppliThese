from django.contrib import admin
from .models import  GloveRCluster, Word2VecRCluster,  FastTextRCluster

# Register your models here.

admin.site.register(GloveRCluster)
admin.site.register(Word2VecRCluster)
admin.site.register(FastTextRCluster)
