from django.test import TestCase
from django.core.exceptions import ValidationError
from Models.users.models import User
from .models import Space, MAX_CREATED_SPACES_PER_USER

class SpaceCreationLimitTests(TestCase):
    def setUp(self):
        # Create a test user
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123',
            name='Dummy'
        )

    def test_space_creation_limit(self):
        # Create spaces up to the limit
        spaces = []
        for i in range(MAX_CREATED_SPACES_PER_USER):
            space = Space.objects.create(
                creator=self.user,
                name=f'Test Space {i+1}'
            )
            spaces.append(space)

        # Attempt to create one more space (should raise ValidationError)
        with self.assertRaises(ValidationError) as context:
            Space.objects.create(
                creator=self.user,
                name='One Space Too Many'
            )
        
        self.assertIn('creator', context.exception.message_dict)

    
    def test_space_editing_no_limit(self):
        # Create a space
        space = Space.objects.create(
            creator=self.user,
            name='Original Space Name'
        )

        # Should be able to edit the space even if user is at their limit
        # First, create remaining spaces up to the limit
        for i in range(MAX_CREATED_SPACES_PER_USER - 1):
            Space.objects.create(
                creator=self.user,
                name=f'Additional Space {i+1}'
            )

        # Now edit the original space (should not raise ValidationError)
        try:
            space.name = 'Updated Space Name'
            space.save()
        except ValidationError:
            self.fail("ValidationError was raised when editing an existing space")

        # Verify the change was saved
        updated_space = Space.objects.get(pk=space.pk)
        self.assertEqual(updated_space.name, 'Updated Space Name')
