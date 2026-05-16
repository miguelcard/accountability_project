from django.contrib import admin
from Models.habits.models import BaseHabitSpace, RecurrentHabit, RecurrentHabitConfigHistory, Goal, CheckMark, Milestone, HabitTag, UserXPLedger

# Register your models here.
admin.site.register(RecurrentHabit)
admin.site.register(Goal)
admin.site.register(CheckMark)
admin.site.register(Milestone)
admin.site.register(HabitTag)
admin.site.register(BaseHabitSpace)


@admin.register(UserXPLedger)
class UserXPLedgerAdmin(admin.ModelAdmin):
    list_display  = ('user', 'habit_title_snap', 'period_start', 'xp_awarded', 'multiplier', 'streak_at_award', 'reason', 'habit')
    list_filter   = ('reason', 'period_start')
    search_fields = ('user__username', 'habit_title_snap')
    readonly_fields = ('awarded_at',)
    ordering = ('-period_start',)
