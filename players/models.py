from django.db import models

class Player(models.Model):
    first_name = models.CharField(max_length=60)
    last_name = models.CharField(max_length=60)
    dob = models.DateField(null=True, blank=True)  # datum rođenja
    position = models.CharField(max_length=30, blank=True)

    def __str__(self):
        return f"{self.first_name} {self.last_name}"
