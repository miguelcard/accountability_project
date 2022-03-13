from django.db import models
from Models.users.models import User

class Space(models.Model):

    creator = models.ForeignKey(User, on_delete=models.PROTECT, related_name='owned_spaces') #  offered me one of the group members to take over as an admin.
    # creator = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)  # use Protect if the creator has higher rights as the admin, else set to SET_NULL and handle rest in bussiness logic
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    tags = models.ManyToManyField('habits.HabitTag', blank=True)
    name = models.CharField(max_length=100)
    description = models.TextField(max_length=255, blank=True, null=True)
    members = models.ManyToManyField(User, related_name='user_spaces', through='SpaceRole')
    
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
    role = models.CharField(choices=ROLES, max_length=20)
    member = models.ForeignKey(User, on_delete=models.CASCADE, related_name='spaceroles')
    space = models.ForeignKey(Space, on_delete=models.CASCADE, related_name='spaceroles')
    # here interesting fields can be added on how users are invited to groups
    # date_joined = models.DateField()
    # invite_reason = models.CharField(max_length=64)
    
    def __str__(self):
        return self.role + ' - '+ self.member.username + ' - '+ self.space.name + ' ['+ str(self.space.id) +']'

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