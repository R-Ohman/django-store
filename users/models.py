from django.core.exceptions import ValidationError
from django.db import models
from django.contrib.auth.models import AbstractUser
from django.shortcuts import redirect
from django.urls import reverse



class User(AbstractUser):
    username = models.CharField(max_length=50, unique=True)
    email = models.EmailField(unique=True)
    image = models.ImageField(upload_to='users_images', blank=True, null=True)
    is_confirmed = models.BooleanField(default=False)
    number_of_available_username_changes = models.PositiveIntegerField(default=1)
