from django.contrib import admin
from .models import Report, Tag, Comment

# Register your models here.

admin.site.register(Comment)
admin.site.register(Report)
admin.site.register(Tag)
