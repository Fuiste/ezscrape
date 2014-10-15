from django.shortcuts import render
from app.models import *
from django.views.decorators.csrf import csrf_exempt
from django.views.generic import View
from middleware.rq_lib import *
import urllib2
import json
import django_rq

# Create your views here.
class QueueScrapeView(View):

    def get(self, request):
        """
        Builds a new property and sets the scraper on it.
        """
        url = 'url?auth_token=' + token
        jsondata = {"array": [1, 2, 3, 4, 5], "title": "hey world"}
        data = {"data" : json.dumps(jsondata)}
        data = urllib.urlencode(data)
        print data
        req = urllib2.Request(url)
        req.add_data(data)

        return HttpResponse(json.dumps({"Success": "EYO SON"}), content_type="application/json")

        # If there's no reviews yet (initial GET) grab 'em
        # if prop.yelp_scraped == False:
        #     if not prop.yelp_processing:
        #         prop.reviews.all().delete()
        #         django_rq.enqueue(scrape_yelp_for_reviews, prop.id)


    @csrf_exempt
    def dispatch(self, *args, **kwargs):
        return super(QueueScrapeView, self).dispatch(*args, **kwargs)
