from django.test import TestCase
from .models import User

class UserCase(TestCase):
    def setUp(self):
        User.objects.create(id="111")
        User.objects.create(id="231")
