from django.db import models

class CountryUpdate(models.Model):
    country = models.CharField(max_length=255)
    update_date = models.DateField()
    link = models.URLField()