from django.db import models
from django.utils import timezone
import time

# Create your models here.
class Review(models.Model):
    """
    A review of a location
    """
    id = models.BigIntegerField(primary_key=True)
    text = models.CharField(max_length=5000)
    grade = models.IntegerField(null=True)
    created_date = models.DateTimeField(default=timezone.now(), null=False)

    def get_ember_dict(self):
        return {"text": self.text, "grade": self.grade, "date": self.created_date.strftime('%Y-%m-%d'), "timestamp": time.mktime(self.created_date.timetuple()), "id": self.id}


class Topic(models.Model):
    """
    A topic denoting a cluster or grouping of reviews.
        -'category' can be NGRAM, NOUNPHRASE, or ENTITY, defaults to NGRAM
    """
    name = models.CharField(max_length=100)
    category = models.CharField(max_length=100, null=False, default='NGRAM')
    reviews = models.ManyToManyField(Review, null=True)

    def get_ember_dict(self):
        return {"name": self.name, "id": self.id, "reviews": [r.id for r in self.reviews.all()]}


class Property(models.Model):
    """
    A physical location belonging to a Customer organization, stores its reviews
    """
    #  Instance fields
    upstream_id = models.IntegerField(null=False, default=-1)
    reviews = models.ManyToManyField(Review, null=True)
    topics = models.ManyToManyField(Topic, null=True)
    yelp_url = models.URLField(null=True)
    yelp_scraped = models.BooleanField(null=False, default=False)
    yelp_processing = models.BooleanField(null=False, default=False)
    topics_analyzed = models.BooleanField(null=False, default=False)
    topics_processing = models.BooleanField(null=False, default=False)

    def get_property_scrape_dict(self):
        if self.yelp_scraped:
            return {"done": self.yelp_scraped, "reviews": [r.get_ember_dict() for r in self.reviews.all()]}
        else:
            return {"done": self.yelp_scraped, "reviews": [r.id for r in self.reviews.all()]}

    def get_property_topics_dict(self):
        if self.topics_analyzed:
            return {"done": self.topics_analyzed, "topics": [t.get_ember_dict() for t in self.topics.all()]}
        else:
            return {"done": self.topics_analyzed, "topics": []}


class ScrapedTextProvider(models.Model):
    """Lifted directly from ReviewSage
    """
    name = models.CharField(max_length=50)
    url = models.URLField(null=True, blank=True)
    rated = models.BooleanField(default=True)

    def get_fields_in_dict(self, field_names=None):
        """Creates a dict representation of this ScrapedTextProvider

        Args:
            field_names: A list of strings of ScrapedText properties
        Returns:
            A dict representation of this ScrapedTextProvider
        """
        fields_dict = {"id": self.id}
        if field_names:
            for name in field_names:
                fields_dict[name] = getattr(self, name)
        return fields_dict

    def __unicode__(self):
        return self.name

    def __str__(self):
        return unicode(self).format("utf-8")
