from django.db import IntegrityError, transaction
from Models.habits.models import Goal, RecurrentHabit, RecurrentHabitConfigHistory, HabitTag, BaseHabit, CheckMark, Milestone
from rest_framework import serializers
import datetime
from rest_framework.exceptions import ParseError, APIException
from Models.spaces.models import Space
from utils.exceptionhandlers import LimitReachedException
from django.utils import timezone
# Filters the Checkmarks or Milestones by Date, by default only the ones in the last 7 days are shown
class FilteredListSerializer(serializers.ListSerializer):

    def to_representation(self, data):
        date_from = self.context['request'].GET.get('cm_from_date', None)
        date_to = self.context['request'].GET.get('cm_to_date', None)

        if isinstance(data, list):
            return super(FilteredListSerializer, self).to_representation(data)
        
        try:    
            if (date_from != None and date_to != None):
                data = data.filter(date__range=[date_from, date_to])
            elif(date_from !=None):
                data = data.filter(date__gt=date_from) 
            elif(date_to != None):
                checkmarks_to_date = datetime.datetime.strptime(date_to, '%Y-%m-%d')
                last_week = checkmarks_to_date - datetime.timedelta(days = 7)
                data = data.filter(date__range=[last_week, date_to])
            else:
                today = datetime.date.today() + datetime.timedelta(days = 1)
                last_week = datetime.date.today() - datetime.timedelta(days = 7)
                data = data.filter(date__range=[last_week, today])
        except Exception as e :
            raise ParseError(detail=('Invalid format of dates (date_to or date_from) given, or an invalid date was given ', str(e)))
        return super(FilteredListSerializer, self).to_representation(data)

class CheckMarkNestedSerializer(serializers.ModelSerializer):
    # this is only used to check the current client date.
    client_date = serializers.DateField(required=False, write_only=True)
    
    class Meta:
        list_serializer_class = FilteredListSerializer
        model = CheckMark
        fields = '__all__'
        
    def create(self, validated_data):
        # Remove clientDate from validated_data as it's not a model field
        client_date = validated_data.pop('client_date', None)
        # Create the instance
        instance = CheckMark(**validated_data)
        # Call save with the client_date parameter
        instance.save(client_date=client_date)
        
        return instance

class MilestoneNestedSerializer(serializers.ModelSerializer):
    class Meta:
        list_serializer_class = FilteredListSerializer
        model = Milestone
        fields = '__all__'

class HabitTagSerializer(serializers.ModelSerializer):
    class Meta:
        model = HabitTag
        fields = '__all__'

def _next_time_frame_period_start(today: datetime.date, new_time_frame: str) -> datetime.date:
    """
    Return the first day of the NEXT full period under `new_time_frame`.

    W→M: 1st of the following month.  If today is already the 1st, defer by
         one additional month so we never return today itself.
    M→W: The coming Monday.  If today is already a Monday, defer by one full
         week for the same reason.

    This ensures the old rule continues through the remainder of the current
    period, eliminating the dead-zone gap.
    """
    if new_time_frame == 'M':
        # Move to the 1st of next month (handle December → January rollover).
        if today.month == 12:
            first_next = datetime.date(today.year + 1, 1, 1)
        else:
            first_next = datetime.date(today.year, today.month + 1, 1)
        # If today IS already the 1st, defer one more month.
        if today.day == 1:
            if first_next.month == 12:
                first_next = datetime.date(first_next.year + 1, 1, 1)
            else:
                first_next = datetime.date(first_next.year, first_next.month + 1, 1)
        return first_next
    else:  # 'W'
        # Next Monday: days_until_monday = (7 - today.weekday()) % 7
        days_until_monday = (7 - today.weekday()) % 7
        # If today IS Monday (days_until=0), defer a full week.
        if days_until_monday == 0:
            days_until_monday = 7
        return today + datetime.timedelta(days=days_until_monday)


class RecurrentHabitSerializerToWrite(serializers.ModelSerializer):
    spaces = serializers.PrimaryKeyRelatedField(
        many=True, 
        queryset=Space.objects.all(),  # Add queryset for validation
        required=False,
    )
    class Meta:
        model = RecurrentHabit
        fields = '__all__'
        read_only_fields = (
            "owner",
        )
    
    # Method that catches the DB uniqueness/constraint failure (an IntegrityError) and handles it gracefully for the client
    # This ensures that for now one habit can only belong to one space, while still having a join table between them. 
    # It wraps the  creation + join table modifications in transaction.atomic() so a failed add() rolls back the created habit.
    def create(self, validated_data):
        spaces = validated_data.pop('spaces', [])
        request = self.context.get('request')
        owner = self.get_habit_owner(request)
        # spaces pks in that habit
        space_pks = [s.pk for s in spaces]

        # all inside runs in a DB transaction
        try:
            with transaction.atomic():
                # Lock + pre-check
                self.check_habits_created_per_user_per_space_not_exceed_max(space_pks, owner, request)
                    
                habit = RecurrentHabit.objects.create(**validated_data) # creates habit row inside transaction
                if spaces:
                    try:
                        habit.spaces.add(*spaces)  # attempts to create rows in the M2M join table. If the DB unique constraint is violated, the DB raises IntegrityError.
                    except IntegrityError:
                        # we may not know current count here
                        # we may also not be 100% sure that the constraint violated is that 1 habit must only belong to 1 space (unique base_habit), so this exception could potentially e missleading.
                        raise LimitReachedException ( # this is not the right exception to be here but KISS (we would need a new one)
                            code="FREE_HABIT_CREATE_LIMIT_REACHED", # maps with the frontend messages
                            current=None,
                            limit=BaseHabit.MAX_HABITS_PER_USER_PER_SPACE,
                            detail=f"Each habit can be assigned to at most one space.",
                            instance=(request.path if request is not None else None),
                            status_code=400
                )
            return habit
        except ParseError:
            # re-raise so DRF handles it as a 400
            raise
        except (serializers.ValidationError, APIException):
        # re-raise so DRF returns the field-aware 400 you raised in the check
            raise
        except Exception as exc:
            # Optional: be conservative and convert unexpected DB integrity issues to a generic ValidationError
            raise ParseError("Could not create habit.")


    def get_habit_owner(self, request):
        owner = getattr(request, 'user', None)
        if owner is None or getattr(owner, 'is_anonymous', False):
            raise ParseError('Owner could not be determined from request.')
        return owner
    
    def check_habits_created_per_user_per_space_not_exceed_max(self, space_pks,owner, request):
        if space_pks:
            # lock space rows to serialize concurrent creators for those spaces
            Space.objects.filter(pk__in=space_pks).select_for_update()
        # Pre-check counts for each space (avoid hitting DB constraint where possible)
        for space_pk in space_pks:
            existing_habits_count = BaseHabit.objects.filter(owner=owner, spaces__pk=space_pk).count()
            if existing_habits_count >= BaseHabit.MAX_HABITS_PER_USER_PER_SPACE:
                # choose an instance id (use request.path or auto-generated in exception)
                instance = request.path if request is not None else None
                # thorw custom exception that frontend can handle well
                raise LimitReachedException(
                    code="FREE_HABIT_CREATE_LIMIT_REACHED", # maps with the frontend messages
                    current=existing_habits_count,
                    limit=BaseHabit.MAX_HABITS_PER_USER_PER_SPACE,
                    detail=f"User already has {existing_habits_count} habits in space {space_pk} (max {BaseHabit.MAX_HABITS_PER_USER_PER_SPACE}).",
                    instance=instance,
                    status_code=403
                )
            
    
    def update(self, instance, validated_data):
        """
        Override DRF's default update to:
        1. Detect changes to `times` or `time_frame`.
        2. If either changes: settle all un-awarded past periods under the OLD
           config *before* saving the new values, then record a new
           RecurrentHabitConfigHistory row so future XP evaluation knows when
           the config changed.
        All of this runs inside a single atomic transaction.
        """
        from Models.habits.xp_utils import settle_habit_xp_before_config_change, period_start_for

        spaces = validated_data.pop('spaces', None)

        old_times      = instance.times
        old_time_frame = instance.time_frame
        new_times      = validated_data.get('times', old_times)
        new_time_frame = validated_data.get('time_frame', old_time_frame)

        config_changed    = (new_times != old_times) or (new_time_frame != old_time_frame)
        time_frame_changed = new_time_frame != old_time_frame

        try:
            with transaction.atomic():
                if config_changed:
                    # Settle un-awarded past periods under the OLD config first
                    settle_habit_xp_before_config_change(instance, old_times, old_time_frame)

                # Apply field updates to the instance
                for attr, value in validated_data.items():
                    setattr(instance, attr, value)
                instance.save()

                if config_changed:
                    today = datetime.date.today()

                    # When `time_frame` changes, we normally defer effective_from
                    # to the first day of the NEXT full period under the new frame
                    # to avoid a dead-zone gap (old rule continues earning XP
                    # through the remainder of the current period).
                    #
                    # EXCEPTION — "immediate revert": if the currently-active
                    # config (the last history entry whose effective_from <= today)
                    # already shares the same time_frame as the new value, the
                    # user is cancelling a pending future transition that hasn't
                    # kicked in yet (e.g. W→M was saved yesterday, new entry is
                    # sitting at June 1, but today is still W — changing back to
                    # W,2x should apply immediately to the current week, not defer
                    # another week).  In that case treat it like a times-only
                    # change and apply immediately to the current period.
                    if time_frame_changed:
                        # Walk history (ascending effective_from) to find what's
                        # genuinely running today.
                        history_entries = sorted(
                            instance.config_history.all(),
                            key=lambda e: e.effective_from,
                        )
                        active_time_frame = old_time_frame  # fallback
                        for entry in history_entries:
                            if entry.effective_from <= today:
                                active_time_frame = entry.time_frame
                            else:
                                break
                        # Revert = the currently-active frame already equals the
                        # new target frame (pending future entry will be overwritten).
                        is_revert = (active_time_frame == new_time_frame)
                    else:
                        is_revert = False

                    # apply_deferred: True  → create future transition entry
                    #                 False → apply to current period immediately
                    apply_deferred = time_frame_changed and not is_revert

                    if not apply_deferred:
                        # Immediate path (times-only change OR revert of a pending
                        # future transition).
                        period_start = period_start_for(today, new_time_frame)
                        # Reuse the most recent within-period entry's date so we
                        # don't create a second row that might be overridden.
                        recent_in_period = (
                            RecurrentHabitConfigHistory.objects
                            .filter(
                                habit=instance,
                                effective_from__gte=period_start,
                                effective_from__lte=today,
                            )
                            .order_by('-effective_from')
                            .first()
                        )
                        effective_from = (
                            recent_in_period.effective_from
                            if recent_in_period
                            else period_start
                        )
                    else:
                        # Deferred path — applies from the next clean period.
                        effective_from = _next_time_frame_period_start(today, new_time_frame)
                        period_start = effective_from  # only used for pruning below
                        # Stash transition data for to_representation() to expose.
                        instance._config_transition = {
                            'old_time_frame': old_time_frame,
                            'new_time_frame': new_time_frame,
                            'new_effective_from': effective_from.isoformat(),
                        }

                    RecurrentHabitConfigHistory.objects.update_or_create(
                        habit          = instance,
                        effective_from = effective_from,
                        defaults       = dict(times=new_times, time_frame=new_time_frame),
                    )

                    # Prune superseded within-period entries that predate the row
                    # we just wrote (e.g. a leftover May-1 entry after a W→M
                    # change created a May-23 entry that we just updated above).
                    if not apply_deferred:
                        RecurrentHabitConfigHistory.objects.filter(
                            habit=instance,
                            effective_from__gte=period_start,
                            effective_from__lt=effective_from,
                        ).delete()

                    # For a revert, also delete any pending future entries that
                    # were part of the transition we just cancelled (e.g. the
                    # W→M June 1 entry when the user reverts M→W today).
                    if is_revert:
                        RecurrentHabitConfigHistory.objects.filter(
                            habit=instance,
                            effective_from__gt=today,
                        ).delete()

                if spaces is not None:
                    try:
                        instance.spaces.set(spaces)
                    except IntegrityError:
                        raise ParseError('Each habit can be assigned to at most one space.')

            return instance
        except ParseError:
            raise
        except (serializers.ValidationError, APIException):
            raise
        except Exception:
            raise ParseError('Could not update habit.')



    def to_representation(self, instance):
        serializer = RecurrentHabitSerializerToRead(instance, context=self.context)
        data = serializer.data
        # Inject config_transition when a time_frame change was just made.
        # The update() method stashes it as a transient attribute on the instance.
        config_transition = getattr(instance, '_config_transition', None)
        if config_transition is not None:
            data['config_transition'] = config_transition
        return data
    
# Overwrites the Serializer to write to make the fields not required for the PATCH methods
class RecurrentHabitSerializerToPatch(RecurrentHabitSerializerToWrite):
    # Set the fields with required=False by default
    times = serializers.IntegerField(required=False)
    time_frame = serializers.CharField(required=False)
    title = serializers.CharField(required=False)


def _compute_streak(habit: RecurrentHabit) -> dict:
    """
    Returns {"count": <int>, "unit": "W"|"M"} for a RecurrentHabit.

    Each past period is evaluated against the `times` and `time_frame` that were
    in effect during that period (resolved from the prefetched `config_history`),
    not the current live values. This ensures that changing `times` does not
    retroactively inflate or deflate the streak.

    Algorithm:
        1. Start from the current period.
        2. If the current period is complete (checkmarks >= historical target), count it.
        3. If the current period is NOT yet complete, skip it and check the previous one.
        4. Continue backwards until a period is not complete — streak ends.
    """
    today = timezone.now().date()

    # Use pre-fetched done_checkmarks when available (set via Prefetch to_attr in get_queryset)
    # to avoid an extra DB query per habit (N+1). Falls back to a live query when the
    # serializer is called outside of a prefetch context.
    if hasattr(habit, 'done_checkmarks'):
        done_dates = {cm.date for cm in habit.done_checkmarks}
    else:
        done_dates = set(
            habit.checkmarks.filter(status='DONE').values_list('date', flat=True)
        )

    # Build a sorted list of config snapshots from the prefetched config_history relation.
    # Each entry has effective_from, times, time_frame.
    config_entries = sorted(
        habit.config_history.all(),
        key=lambda c: c.effective_from,
    )

    def get_config_for_period(period_start: datetime.date):
        """
        Return (times, time_frame) that was in effect on `period_start`.
        Finds the latest config entry whose effective_from <= period_start.
        Falls back to current live values if no matching entry exists.
        """
        result = None
        for entry in config_entries:
            if entry.effective_from <= period_start:
                result = entry
            else:
                break
        if result is not None:
            return result.times, result.time_frame
        return habit.times, habit.time_frame

    def week_bounds(d: datetime.date):
        """Return (monday, sunday) for the week containing d."""
        monday = d - datetime.timedelta(days=d.weekday())
        sunday = monday + datetime.timedelta(days=6)
        return monday, sunday

    def month_bounds(d: datetime.date):
        """Return (first_day, last_day) for the month containing d."""
        first = d.replace(day=1)
        if d.month == 12:
            last = datetime.date(d.year + 1, 1, 1) - datetime.timedelta(days=1)
        else:
            last = datetime.date(d.year, d.month + 1, 1) - datetime.timedelta(days=1)
        return first, last

    def prev_period_start(start: datetime.date) -> datetime.date:
        """Return a date that falls inside the period immediately before the one starting at start."""
        return start - datetime.timedelta(days=1)

    def period_done_count(start: datetime.date, end: datetime.date) -> int:
        return sum(1 for d in done_dates if start <= d <= end)

    streak = 0
    anchor = today
    first_period = True
    # Tracks the time_frame of the most recently completed streak period so the
    # unit reflects the historical config that was actually counted, not the
    # current live config (which may have changed since those periods ran).
    streak_unit: str | None = None

    while True:
        # Resolve the historically-correct config for this period's start date.
        required, time_frame = get_config_for_period(anchor)

        # Stop counting if we cross into a different time_frame phase.
        # e.g. habit changed W→M: once streak_unit='M' is established, do not
        # continue counting old 'W' periods behind the change date (and vice
        # versa). streak_unit is None until the first period is counted, so the
        # skip-incomplete-first-period path is unaffected.
        if streak_unit is not None and time_frame != streak_unit:
            break

        if time_frame == 'W':
            start, end = week_bounds(anchor)
        else:  # 'M'
            start, end = month_bounds(anchor)

        count = period_done_count(start, end)
        is_complete = count >= required

        if first_period:
            first_period = False
            if is_complete:
                streak += 1
                streak_unit = time_frame
            else:
                # Current period incomplete — check previous period
                anchor = prev_period_start(start)
                continue
        else:
            if is_complete:
                streak += 1
                streak_unit = time_frame
            else:
                break  # streak broken

        anchor = prev_period_start(start)

    # Fall back to the current config's time_frame when no period was completed.
    if streak_unit is None:
        _, streak_unit = get_config_for_period(today)
    return {"count": streak, "unit": streak_unit}


class RecurrentHabitSerializerToRead(serializers.ModelSerializer):
    tags = HabitTagSerializer(many=True, read_only=True)
    checkmarks = CheckMarkNestedSerializer(many=True, read_only=True)
    streak = serializers.SerializerMethodField()
    config_history = serializers.SerializerMethodField()

    class Meta:
        model = RecurrentHabit
        fields = '__all__'
        read_only_fields = (
            "owner",
        )

    def get_streak(self, obj):
        return _compute_streak(obj)

    def get_config_history(self, obj):
        """
        Returns a list of config snapshots sorted ascending by effective_from.
        Each entry: { effective_from (ISO date string), times (int), time_frame (str) }
        Consumed by the frontend to resolve the historically-correct `times` denominator
        for progress bar calculations on past weeks/months.
        """
        entries = obj.config_history.all().order_by('effective_from')
        return [
            {
                'effective_from': entry.effective_from.isoformat(),
                'times': entry.times,
                'time_frame': entry.time_frame,
            }
            for entry in entries
        ]
    
class GoalSerializerToWrite(serializers.ModelSerializer):
    class Meta:
        model = Goal
        fields = '__all__'
        read_only_fields = (
            "owner",
        )

    def to_representation(self, instance):
        serializer = GoalSerializerToRead(instance, context=self.context)
        return serializer.data

class GoalSerializerToRead(serializers.ModelSerializer):
    tags = HabitTagSerializer(many=True, read_only=True)
    checkmarks = CheckMarkNestedSerializer(many=True, read_only=True)
    milestones = MilestoneNestedSerializer(many=True, read_only=True)

    class Meta:
        model = Goal
        fields = '__all__'
        read_only_fields = (
            "owner",
        )

