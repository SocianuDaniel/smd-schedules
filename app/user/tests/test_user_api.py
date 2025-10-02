"""
Test for the user API
"""
from django.test import TestCase
from django.contrib.auth import get_user_model
from django.urls import reverse

from rest_framework.test import APIClient
from rest_framework import status


CREATE_USER_URL = reverse('user:create')
TOKEN_URL = reverse('user:token')


def create_user(**params):
    """Create and return a new user"""
    return get_user_model().objects.create_user(**params)


class PublicUserApiTests(TestCase):
    """Test the public features of the user API """

    def setUp(self):
        self.client = APIClient()

    def test_create_user_success(self):
        """Test creating a user is successful"""
        payload = {
            'email': 'test@example.com',
            'password': 'testpass123',
            'name': 'Test Name'
        }
        res = self.client.post(CREATE_USER_URL, payload)

        # check if request of creating user has completed successfuly
        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        # --------------------------------------------------------------

        # retrive user with email
        user = get_user_model().objects.get(email=payload['email'])
        # --------------------------------------------------------------

        # check if the user has been created with the password given
        self.assertTrue(user.check_password(payload['password']))
        # --------------------------------------------------------------

        # check if the retrned data not contain the password
        self.assertNotIn('password', res.data)
        # --------------------------------------------------------------

    def test_use_with_email_exists_return_error(self):
        """test error returned if user with email exists"""
        payload = {
            'email': 'test@example.com',
            'password': 'testpass123',
            'name': 'Test Name'
        }

        # create a user
        create_user(**payload)
        # --------------------------------------------------------------

        # make a request to create a user
        res = self.client.post(CREATE_USER_URL, payload)
        # --------------------------------------------------------------

        # check  return 400 BAD REQUEST if email exists
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)
        # --------------------------------------------------------------

    def test_password_too_short_error(self):
        """Test if error is returned if create user with too short password"""

        payload = {
            'email': 'test@example.com',
            'password': 'pw',
            'name': 'Test Name'
        }
        res = self.client.post(CREATE_USER_URL, payload)

        # test if returned a 400 BAD REQUEST for a very short password
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)
        # --------------------------------------------------------------

        user_exists = get_user_model().objects.filter(
            email=payload['email']
            ).exists()

        # test that the user with email does not exists
        self.assertFalse(user_exists)
        # --------------------------------------------------------------

    def test_create_token_for_user(self):
        """Test create token for user with valid credentials"""
        user_details = {
            'email': 'test@example.com',
            'password': 'testpass123',
            'name': 'test User'
        }
        create_user(**user_details)
        payload = {
            'email': 'test@example.com',
            'password': 'testpass123'
        }
        res = self.client.post(TOKEN_URL, payload)
        self.assertIn('token', res.data)
        self.assertEqual(res.status_code, status.HTTP_200_OK)

    def test_create_token_bad_credentials(self):
        """test  doestn't create token with bad password"""
        create_user(email="test@example.com", password='goodpass')
        payload = {
            'email': 'test@example.com',
            'passord': 'baddpass'
        }
        res = self.client.post(TOKEN_URL, payload)
        self.assertNotIn('token', res.data)
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_token_blank_password(self):
        """Test create token with blank password return error"""
        payload = {'email': 'test#example.com', 'password': ''}
        res = self.client.post(TOKEN_URL, payload)

        self.assertNotIn('token', res.data)
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)
