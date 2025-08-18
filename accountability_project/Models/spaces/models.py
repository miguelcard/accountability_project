import logging
from django.db import models
from Models.users.models import User
from django.core.exceptions import ValidationError

logger = logging.getLogger(__name__)

MAX_CREATED_SPACES_PER_USER = 3

class Space(models.Model):

    creator = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='owned_spaces')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    tags = models.ManyToManyField('habits.HabitTag', blank=True)
    name = models.CharField(max_length=100)
    description = models.TextField(max_length=255, blank=True, null=True)
    members = models.ManyToManyField(User, related_name='user_spaces', through='SpaceRole')
    icon_alias = models.CharField(max_length=50, blank=True, null=True, help_text=("the alias of the icon for this space, according to the frontend alias to icon mapper"))
    
    def __str__(self):
        return f'[{self.id}] {self.name}'

    class Meta:
        verbose_name = 'Space'
        verbose_name_plural = 'Spaces'
        ordering = ['-created_at']
        db_table = 'space'

    # This save method is called everytime a space is created or edited (saved)
    # Checks that the user creating one space (free tier) has not surpassed the limits of the maximum amout of spaces he can create MAX_CREATED_SPACES_PER_USER
    def save(self, *args, **kwargs):
        # number of existing spaces where the user is already a creator:
        existing_created_spaces_by_user = Space.objects.filter(creator=self.creator).count()
        if(self.creator is not None):
            logger.info(f'user "{self.creator.username}" creating or editing space with name {self.name}') # id has not been assigned at this time
        else:
            logger.info(f'space with name {self.name} being creatied or edited and has no creator')

        logger.info(f'existing_created_spaces_by_user: "{existing_created_spaces_by_user}"')
        if existing_created_spaces_by_user >= MAX_CREATED_SPACES_PER_USER:
            if(self.creator is not None):
                logger.info(f'raising error for user "{self.creator.username}" when creating space with name {self.name} because he exceeds the maximum allowed created spaces')
            raise ValidationError({
                    'creator': f'You’ve reached the limit of creating '
                              f'{MAX_CREATED_SPACES_PER_USER} spaces on the free tier.\n You can still join spaces created by other users.'
                })
        
        super(Space, self).save(*args, **kwargs)


class SpaceRole(models.Model):

    MAX_BELONGED_SPACES_PER_USER = 4
    ROLES = [
    ('admin', 'admin'),
    ('member', 'member')
    ]
    role = models.CharField(choices=ROLES, max_length=20, help_text=("Character field with the choices of 'admin' or 'member'"))
    member = models.ForeignKey(User, on_delete=models.CASCADE, related_name='spaceroles', help_text=("PK of the user"))
    space = models.ForeignKey(Space, on_delete=models.CASCADE, related_name='spaceroles', help_text=("PK of the space"))
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    # here interesting fields can be added on how users are invited to groups
    # date_joined = models.DateField()
    # invite_reason ... way = models.CharField(max_length=64)
    
    def __str__(self):
        return '[' + str(self.id) + '] ' + self.role + ' - '+ self.member.username +  ' ['+ str(self.member.id) +']' + ' - '+ self.space.name + ' ['+ str(self.space.id) +']'
    
    # Documentation...
    def clean(self):
        # Only enforce on *new* records (i.e. no self.pk / self.id yet)
        if not self.pk:
            # 1) spaces where the user is the creator:
            created_spaces_count = Space.objects.filter(creator=self.member).count()

            if created_spaces_count > MAX_CREATED_SPACES_PER_USER:
                logger.info(f'User may not be able to create more than "{MAX_CREATED_SPACES_PER_USER}" spaces, validation error is thrown')
                raise ValidationError({
                    'member': f'You’ve reached the limit of creating '
                              f'{MAX_CREATED_SPACES_PER_USER} spaces on the free tier.\n You can still join spaces created by other users.'
                })
            
            # 2) spaces where the user belongs (with any role):
            total_spaces_count = SpaceRole.objects.filter(member=self.member).count()
            if total_spaces_count >= self.MAX_BELONGED_SPACES_PER_USER:
                logger.info(f'The user you are trying to invite may not be able to belong to more than "{self.MAX_BELONGED_SPACES_PER_USER}" spaces, validation error is thrown')
                raise ValidationError({
                        'error': f'{self.member.username} already belongs to the maximum of '
                                f'{self.MAX_BELONGED_SPACES_PER_USER} spaces for the free tier.'
                    })

    #  User can have only one "SpaceRole" in each space so any previous one is overwriten if it exists
    def save(self, *args, **kwargs):
        roles_between_user_space = SpaceRole.objects.filter(member=self.member, space=self.space)
        if roles_between_user_space.exists():
            roles_between_user_space.delete()

        # full_clean() will call clean() and also check any other model‑level validators
        self.full_clean()
        super(SpaceRole, self).save(*args, **kwargs)

    class Meta:
        verbose_name = 'Space Role'
        verbose_name_plural = 'Space Roles'
        ordering = ['role']
        db_table = 'space_role'