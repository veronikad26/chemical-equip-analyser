from django.db import models
from django.contrib.auth.hashers import make_password, check_password
import uuid
from datetime import datetime, timezone


class AppUser(models.Model):
    id = models.CharField(max_length=36, primary_key=True, default=uuid.uuid4)
    username = models.CharField(max_length=255, unique=True)
    email = models.EmailField(unique=True)
    password = models.CharField(max_length=255)
    created_at = models.DateTimeField(default=datetime.now)

    def set_password(self, password):
        self.password = make_password(password)

    def check_password(self, password):
        return check_password(password, self.password)

    class Meta:
        db_table = 'users'


class Dataset(models.Model):
    id = models.CharField(max_length=36, primary_key=True, default=uuid.uuid4)
    filename = models.CharField(max_length=255)
    uploaded_at = models.DateTimeField(default=datetime.now)
    summary = models.JSONField()
    user = models.ForeignKey(AppUser, on_delete=models.CASCADE, related_name='datasets')
    file_path = models.CharField(max_length=500)
    data = models.JSONField()  # Store the actual data

    class Meta:
        db_table = 'datasets'