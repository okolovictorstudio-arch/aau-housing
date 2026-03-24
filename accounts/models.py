from django.db import models
from django.contrib.auth.models import User
import random
from django.utils import timezone
from datetime import timedelta

class PasswordResetCode(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    code = models.CharField(max_length=6)
    created_at = models.DateTimeField(auto_now_add=True)

    def is_valid(self):
        # Code is valid for 15 minutes
        return timezone.now() < self.created_at + timedelta(minutes=15)

    @classmethod
    def generate_code(cls, user):
        code = str(random.randint(100000, 999999))
        cls.objects.filter(user=user).delete() # remove old codes
        return cls.objects.create(user=user, code=code)
