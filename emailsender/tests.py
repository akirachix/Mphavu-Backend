from django.test import TestCase
from .models import EmailInvite
class EmailInviteModelTests(TestCase):
    def setUp(self):
        """Create a test instance of EmailInvite."""
        self.invite = EmailInvite.objects.create(email='test@example.com')
    def test_email_invite_creation(self):
        """Test that an EmailInvite instance is created correctly."""
        self.assertEqual(self.invite.email, 'test@example.com')
        self.assertIsNotNone(self.invite.invited_at)
    def test_email_invite_string_representation(self):
        """Test the string representation of the EmailInvite model."""
        self.assertEqual(str(self.invite), 'test@example.com')
    def test_email_invite_unique_email(self):
        """Test that the email field must be unique."""
        with self.assertRaises(Exception) as context:
            EmailInvite.objects.create(email='test@example.com')
        self.assertTrue('UNIQUE constraint failed' in str(context.exception))
    def test_email_field_validation(self):
        """Test that the email field correctly validates email addresses."""
        invalid_email_invite = EmailInvite(email='invalid-email')
        with self.assertRaises(Exception):
            invalid_email_invite.full_clean()  # This should raise a ValidationError
        valid_email_invite = EmailInvite(email='valid@example.com')
        try:
            valid_email_invite.full_clean()  # Should not raise an error
        except Exception:
            self.fail("valid_email_invite.full_clean() raised Exception unexpectedly!")
# You can add more tests here as needed




