from django.db import models
from django.utils import timezone
import time

# Create your models here.
class Review(models.Model):
    """
    A review of a location
    """
    text = models.CharField(max_length=5000)
    grade = models.IntegerField(null=True)
    created_date = models.DateTimeField(default=timezone.now(), null=False)


class Property(models.Model):
    """
    A physical location belonging to a Customer organization, stores its reviews
    """
    #  Instance fields
    upstream_id = models.IntegerField(null=False, default=-1)
    reviews = models.ManyToManyField(Review, null=True)
    yelp_url = models.URLField(null=True)
    yelp_scraped = models.BooleanField(default=False)
    yelp_processing = models.BooleanField(default=False)
