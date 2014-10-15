from django.shortcuts import render
from django.http import HttpResponse
from app.models import *
from django.views.decorators.csrf import csrf_exempt
from django.views.generic import View
from middleware.rq_lib import *
import urllib2
import urllib
import json
import django_rq

# Create your views here.
class QueueScrapeView(View):

    def post(self, request):
        """
        Builds a new property and sets the scraper on it.  Needs the upstream id and yelp_url of the property to get started.
        """
        print "Recieved scrape request for upstream property {0}".format(request.POST["upstream_id"])
        print request.POST["yelp_url"]

        prop_l = Property.objects.filter(upstream_id=request.POST["upstream_id"])
        if len(prop_l):
            prop = prop_l[0]
        else:
            prop = Property(upstream_id=request.POST["upstream_id"], yelp_url=request.POST["yelp_url"])
            prop.save()

        # If there's no reviews yet (initial GET) grab 'em
        if prop.yelp_scraped == False:
            if not prop.yelp_processing == True:
                prop.yelp_processing = True
                prop.reviews.all().delete()
                django_rq.enqueue(scrape_yelp_for_reviews, prop.id)
        else:
            print "NOTHING TO SCRAPE"

        return HttpResponse(json.dumps(prop.get_property_status_dict()), content_type="application/json")


    @csrf_exempt
    def dispatch(self, *args, **kwargs):
        return super(QueueScrapeView, self).dispatch(*args, **kwargs)
