from django.core.exceptions import ValidationError
from django.db import models
from django.contrib.auth.models import AbstractUser
from django.shortcuts import redirect
from django.urls import reverse


class User(AbstractUser):
    username = models.CharField(max_length=50, unique=True)
    email = models.EmailField(unique=True)
    image = models.ImageField(upload_to='users_images', blank=True, null=True)
