from django.db.models.signals import m2m_changed
from django.dispatch import receiver
from rest_framework.exceptions import ParseError
from django.db.models.signals import post_save
from Models.habits.models import BaseHabit
from utils.exceptionhandlers import LimitReachedException


# Enforces the max habits per user per spece rule at model level (DB)
# This method is a listener for Djangos "m2m_changed" signal, for the join table between habits and spaces
# The string that tells you what operation on the M2M relation is happening
# Model-level guard (signal) to check that user does not surpass the max amount of habits that he can create per space
# sender is the through table for BaseHabit.spaces
# This protects additions that happen outside your serializer (e.g. admin, management commands).
# It does not by itself solve race conditions — that’s why serializer-level select_for_update() + transaction is recommended for request-time creates. Use both for robust protection.
@receiver(m2m_changed, sender=BaseHabit.spaces.through)
def enforce_max_habits_per_space(sender, instance, action, pk_set, **kwargs):
    # only care when items are being added
    if action != 'pre_add':
        return

    owner_id = instance.owner_id
    if not owner_id:
        # if owner not set yet, can't validate here
        return

    for space_pk in pk_set:
        existing_habits_count = BaseHabit.objects.filter(owner_id=owner_id, spaces__pk=space_pk).exclude(pk=instance.pk).count()
        if existing_habits_count >= BaseHabit.MAX_HABITS_PER_USER_PER_SPACE:
            # raising Exception aborts the add
            raise LimitReachedException (
                code="FREE_HABIT_CREATE_LIMIT_REACHED", # maps with the frontend messages
                current=existing_habits_count,
                limit=BaseHabit.MAX_HABITS_PER_USER_PER_SPACE,
                detail=f"User already has {existing_habits_count} habits in space {space_pk} (max {BaseHabit.MAX_HABITS_PER_USER_PER_SPACE}).",
                # instance=instance, # cannot serialize a model instance
                status_code=403
            )

# If the Django admin GUI is creating/editing the through table directly, m2m_changed will not be emitted, thats why we need this check for this case.
# we keep the m2m_changed to catch programmatic .add()/.set() hat covers your API and most programmatic paths.
# DEPRECATED -> logic moved to BaseHabitSpace model, clean() method, there we can enforce the check for both creating and updating. (apparenty this signal is ugly and just happens after the DB  has already thrown an error, not very proactive...)
# @receiver(post_save, sender=BaseHabit.spaces.through)
# def through_post_save(sender, instance, created, **kwargs):
#     if not created:
#         return
#     # instance.basehabit, instance.space available — validate owner counts
#     owner = instance.basehabit.owner
#     space_pk = instance.space_id
#     existing_habits_count = BaseHabit.objects.filter(owner=owner, spaces__pk=space_pk).exclude(pk=instance.basehabit_id).count()
#     if existing_habits_count >= BaseHabit.MAX_HABITS_PER_USER_PER_SPACE:
#         instance.delete()
#         # This returns an ugly 500 error to the django admin, but thats ok for now
#         raise LimitReachedException (
#             code="FREE_HABIT_CREATE_LIMIT_REACHED", # maps with the frontend messages
#             current=existing_habits_count,
#             limit=BaseHabit.MAX_HABITS_PER_USER_PER_SPACE,
#             detail=f"User already has {existing_habits_count} habits in space {space_pk} (max {BaseHabit.MAX_HABITS_PER_USER_PER_SPACE}).",
#             instance=instance,
#             status_code=403
#         )