"""
Test for models.
"""
from django.test import TestCase
from django.contrib.auth import get_user_model
# from django.db.utils import IntegrityError


class ModelTest(TestCase):
    """Test models"""

    def test_create_user_with_email_successful(self):
        email = 'test@example.com'
        password = 'testpass123'
        user = get_user_model().objects.create_user(
            email=email,
            password=password
        )

        self.assertEqual(user.email, email)
        self.assertTrue(user.check_password(password))

    def test_user_has_normalise_email(self):
        email_checks = [
            ['test@EXAMPLE.com', 'test@example.com'],
            ['test1@example.COM', 'test1@example.com'],
            ['test2@EXAMPLE.COM', 'test2@example.com'],
            ['Test3@Example.Com', 'Test3@example.com']
        ]
        for email, expect in email_checks:
            user = get_user_model().objects.create_user(
                email=email,
                password="pass123"
                )
            self.assertEqual(user.email, expect)

    def test_input_email_is_empty(self):
        with self.assertRaises(ValueError):
            get_user_model().objects.create_user(
                email='',
                password="pass123"
            )

    def test_create_superuser(self):
        user = get_user_model().objects.create_superuser(
            email="test123@email.com",
            password="pass123"
        )
        self.assertTrue(user.is_superuser)
        self.assertTrue(user.is_staff)

    # def test_create_employee(self):
    #     owner = get_user_model().objects.create_user(
    #         email="owner123@email.com",
    #         password="pass123"
    #     )
    #     employee = Employee.objects.create(
    #         owner=owner,
    #         firstname="my firstname",
    #         lastname="my lastname",
    #         email='employee@email.com'
    #     )
    #     self.assertEqual(employee.owner, owner)
    #
    # def test_create_employee_with_unique_email(self):
    #     """test create employee with unique email"""
    #     owner = get_user_model().objects.create_user(
    #         email="owner@email.com",
    #         password="pass123"
    #     )
    #     employee = Employee.objects.create(
    #         owner=owner,
    #         firstname="my firstname",
    #         lastname="my lastname",
    #         email='employee@email.com'
    #     )
    #     with self.assertRaises(IntegrityError):
    #         Employee.objects.create(
    #             owner=owner,
    #             firstname="my firstname 1",
    #             lastname="my lastname 1",
    #             email=employee.email
    #         )
