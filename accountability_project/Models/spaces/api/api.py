from django.db.models import Count
from rest_framework import generics, serializers
from Models.spaces.models import Space, SpaceRole
from Models.spaces.api.serializers import SpaceSerializer, SpaceRoleSerializer
from django.db.models import Q
from Models.spaces.api.pagination import SpacesPagination
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import OrderingFilter, SearchFilter

""" ---------views for Spaces--------"""

# GET & POST
class SpacesApiView(generics.ListCreateAPIView):
    """
    Lists Spaces where current user belongs and Creates Spaces with current user as creator
    """
    serializer_class = SpaceSerializer
    pagination_class = SpacesPagination
    filter_backends = [DjangoFilterBackend, OrderingFilter, SearchFilter]
    filter_fields = ['creator__username', 'creator__name', 'name', 'description', 'members__username', 'tags__name', 'spaceroles__member__username', 'spaceroles__role']  # members_username is the same as spacerole__member__username
    ordering_fields = ['id', 'creator__username', 'creator__name', 'name', 'created_at', 'updated_at', 'tags__name', 'size'] 
    search_fields = ['name', 'tags__name', 'creator__username', 'tags__name', 'description', 'members__username', 'members__name']

    def get_queryset(self):
        return Space.objects.annotate(size=Count('members')).filter(Q(creator= self.request.user) | Q(members = self.request.user)).prefetch_related('members')

    def perform_create(self, serializer):
        # adds logged in user as creator of the space
        space = serializer.save(creator=self.request.user)
        # creates a role connection of the user and space as admin
        SpaceRole.objects.create(role='admin', member=self.request.user, space=space)
        