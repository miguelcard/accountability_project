from django.db import models
from Models.users.models import User

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

class SpaceRole(models.Model):
  
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

    #  User can have only one "SpaceRole" in each space so any previous one is overwriten if it exists
    def save(self, *args, **kwargs):
        roles_between_user_space = SpaceRole.objects.filter(member=self.member, space=self.space)
        if roles_between_user_space.exists():
            roles_between_user_space.delete()
        super(SpaceRole, self).save(*args, **kwargs) 

    class Meta:
        verbose_name = 'Space Role'
        verbose_name_plural = 'Space Roles'
        ordering = ['role']
        db_table = 'space_role'