from django.contrib import admin
from Models.users.models import User, Language, Tag

admin.site.register(User)
admin.site.register(Language)
admin.site.register(Tag)
