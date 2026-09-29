from django.contrib import admin
from Models.spaces.models import Space, SpaceRole, PendingInvite

# Register your models here.

admin.site.register(Space)
admin.site.register(SpaceRole)


@admin.register(PendingInvite)
class PendingInviteAdmin(admin.ModelAdmin):
    list_display = ('email', 'space', 'invited_by', 'accepted', 'created_at', 'expires_at')
    list_filter = ('accepted',)
    search_fields = ('email', 'space__name', 'invited_by__username')
    readonly_fields = ('token', 'created_at', 'accepted_at')
