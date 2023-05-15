# models.py
from django.contrib.auth.models import AbstractUser
from django.db import models

# Create your models here.
from django.dispatch import receiver
from django.urls import reverse
from django_rest_passwordreset.signals import reset_password_token_created
from django.core.mail import send_mail


@receiver(reset_password_token_created)
def password_reset_token_created(sender, instance, reset_password_token, *args, **kwargs):
    email_plaintext_message = "{}?token={}".format(reverse('password_reset:reset-password-request'),
                                                   reset_password_token.key)

    send_mail(
        # title:
        "Password Reset for {title}".format(title="Some website title"),
        # message:
        email_plaintext_message,
        # from:
        "noreply@somehost.local",
        # to:
        [reset_password_token.user.email]
    )


class CustomUser(AbstractUser):
    SERVICE_CENTERS = [
        ('Middelburg SC', 'Middelburg SC'),
        ('Polokwane SC', 'Polokwane SC'),
        ('Cape Town SC', 'Cape Town SC'),
        ('Johannesburg SC', 'Johannesburg SC'),
        ('Bloemfontein SC', 'Bloemfontein SC'),
        ('Port Elizabeth SC', 'Port Elizabeth SC')
    ]

    service_center = models.CharField(max_length=100, choices=SERVICE_CENTERS, null=True, blank=True)

    @property
    def full_name(self):
        return f"{self.first_name} {self.last_name}"
