from accountability_project.Models.users.models import Tag
from django.contrib import admin
from Models.users.models import User, Language

admin.site.register(User)
admin.site.register(Language)
admin.site.register(Tag)
