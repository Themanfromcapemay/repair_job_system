import os
from datetime import datetime

from django.contrib.auth.models import User
from django.db import models


class Customer(models.Model):
    name = models.CharField(max_length=50, blank=True, null=True)
    email = models.EmailField(blank=True, null=True)
    contact_number = models.CharField(max_length=20, blank=True, null=True)
    alt_contact_number = models.CharField(max_length=255, blank=True, null=True)
    address = models.CharField(max_length=255, blank=True, null=True)

    def __str__(self):
        return self.name


class JobNumberField(models.CharField):
    def __init__(self, *args, **kwargs):
        kwargs.setdefault('max_length', 7)
        super().__init__(*args, **kwargs)

    def generate_job_number(self):
        prefix = 'LA'
        count = JobCard.objects.count()
        suffix = f"{count + 1:04d}"  # Format the count as a 10-digit number
        return f"{prefix}-{suffix}"

    def pre_save(self, model_instance, add):
        value = getattr(model_instance, self.attname, None)
        if not value:
            value = self.generate_job_number()
            setattr(model_instance, self.attname, value)
        return value


class JobCard(models.Model):
    STATUS_CHOICES = (
        ('Open', 'Open'),
        ('Closed', 'Closed'),
        ('In Progress', 'In Progress')
    )

    customer = models.ForeignKey(Customer, on_delete=models.CASCADE)
    complaint_or_query = models.TextField(blank=True, null=True)
    error_code = models.CharField(max_length=50, blank=True, null=True)
    date_created = models.DateTimeField(auto_now_add=True)
    date_of_query = models.DateField(blank=True, null=True)
    date_of_purchase = models.DateField(blank=True, null=True)
    store_name = models.CharField(max_length=50, blank=True, null=True)
    product_name = models.CharField(max_length=100)
    serial_number = models.CharField(max_length=50, blank=True, null=True)
    date_of_technician_assessment = models.DateField(blank=True, null=True)
    technician_assessment = models.TextField(blank=True, null=True)
    additional_notes = models.TextField(blank=True, null=True)
    fault_code = models.CharField(max_length=5, blank=True, null=True)
    job_status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="Open")
    resolution = models.TextField(blank=True, null=True)
    last_modified_by = models.CharField(max_length=50, blank=True, null=True)
    last_modified_at = models.DateTimeField(auto_now=True)
    job_number = JobNumberField(unique=True)

    def __str__(self):
        return f"{self.customer.name} - {self.job_number}"


class Images(models.Model):
    job_card = models.ForeignKey(JobCard, on_delete=models.CASCADE)

    def job_card_directory(instance, filename):
        date_string = datetime.now().strftime('%Y-%m-%d')
        return f'job_cards/{instance.job_card.job_number}/{date_string}/{filename}'

    def delete_old_image(self, old_image):
        if old_image and os.path.isfile(old_image.path):
            os.remove(old_image.path)

    def save(self, *args, **kwargs):
        if self.pk:
            old_images = Images.objects.get(pk=self.pk)
            if self.pop_image != old_images.pop_image:
                self.delete_old_image(old_images.pop_image)
            if self.before_assessment_image1 != old_images.before_assessment_image1:
                self.delete_old_image(old_images.before_assessment_image1)
            if self.before_assessment_image2 != old_images.before_assessment_image2:
                self.delete_old_image(old_images.before_assessment_image2)
            if self.before_assessment_image3 != old_images.before_assessment_image3:
                self.delete_old_image(old_images.before_assessment_image3)
            if self.after_assessment_image1 != old_images.after_assessment_image1:
                self.delete_old_image(old_images.after_assessment_image1)
            if self.after_assessment_image2 != old_images.after_assessment_image2:
                self.delete_old_image(old_images.after_assessment_image2)
            if self.after_assessment_image3 != old_images.after_assessment_image3:
                self.delete_old_image(old_images.after_assessment_image3)
            if self.assessment_environment_image != old_images.assessment_environment_image:
                self.delete_old_image(old_images.assessment_environment_image)
        super(Images, self).save(*args, **kwargs)

    pop_image = models.ImageField(upload_to=job_card_directory, blank=True, null=True)
    before_assessment_image1 = models.ImageField(upload_to=job_card_directory, blank=True, null=True)
    before_assessment_image2 = models.ImageField(upload_to=job_card_directory, blank=True, null=True)
    before_assessment_image3 = models.ImageField(upload_to=job_card_directory, blank=True, null=True)
    after_assessment_image1 = models.ImageField(upload_to=job_card_directory, blank=True, null=True)
    after_assessment_image2 = models.ImageField(upload_to=job_card_directory, blank=True, null=True)
    after_assessment_image3 = models.ImageField(upload_to=job_card_directory, blank=True, null=True)
    assessment_environment_image = models.ImageField(upload_to=job_card_directory, blank=True, null=True)

    def __str__(self):
        return f"Images for {self.job_card.customer.name} - {self.job_card.job_number}"
