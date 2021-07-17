from django.contrib.auth.models import AbstractUser
from django.db import models

from mainapp.models import University


class CustomUser(AbstractUser):
    univer = models.ForeignKey(University, models.CASCADE, verbose_name='Универ', null=True, blank=True)
    is_staff = models.BooleanField(default=True)
    REQUIRED_FIELDS = []


class Locale(models.Model):
    key = models.CharField(max_length=50, unique=True)
    value = models.TextField(null=True)

    cache = dict()

    def __class_getitem__(cls, key) -> str:
        if key not in cls.cache:
            obj, _ = cls.objects.get_or_create(key=key)
            cls.cache[key] = obj.value or obj.key
        return cls.cache[key]

    def save(self, *args, **kwargs):
        self.cache[self.key] = self.value
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.key} -> {self.value or 'Не заполнено'}"

    class Meta:
        verbose_name = "Текст"
        verbose_name_plural = "Текста"
