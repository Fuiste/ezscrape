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

        # Grab the property from the local db, create it if it doesn't exist
        prop_l = Property.objects.filter(upstream_id=request.POST["upstream_id"])
        if len(prop_l):
            prop = prop_l[0]
        else:
            prop = Property(upstream_id=request.POST["upstream_id"], yelp_url=request.POST["yelp_url"])
            prop.save()

        print "Scraped: {0} Processing: {1}".format(prop.yelp_scraped, prop.yelp_processing)
        # If scraping hasn't been run yet (initial GET) grab 'em
        if not prop.yelp_scraped:
            if not prop.yelp_processing:
                prop.yelp_processing = True
                prop.reviews.all().delete()
                prop.save()
                django_rq.enqueue(scrape_yelp_for_reviews, prop.id)
        else:
            print "NOTHING TO SCRAPE"

        return HttpResponse(json.dumps(prop.get_property_scrape_dict()), content_type="application/json")


    @csrf_exempt
    def dispatch(self, *args, **kwargs):
        return super(QueueScrapeView, self).dispatch(*args, **kwargs)


class POSTagView(View):

    def post(self, request):
        """
        POS Tags a given property for noun phrases. 
        """
        print "Recieved POS tag request for upstream property {0}".format(request.POST["upstream_id"])

        # Grab the property from the local db, error it if it doesn't exist
        prop_l = Property.objects.filter(upstream_id=request.POST["upstream_id"])
        if len(prop_l):
            prop = prop_l[0]
        else:
            return HttpResponse(json.dumps({"error": 1}), content_type="application/json")

        print "Analyzed: {0} Processing: {1}".format(prop.topics_analyzed, prop.topics_processing)
        # If POS tags haven't been run, do it!
        if not prop.topics_analyzed:
            if not prop.topics_processing:
                prop.topics_processing = True
                prop.topics.all().delete()
                prop.save()
                django_rq.enqueue(analyze_reviews_for_topics, prop.id)

        return HttpResponse(json.dumps(prop.get_property_topics_dict()), content_type="application/json")

    @csrf_exempt
    def dispatch(self, *args, **kwargs):
        return super(POSTagView, self).dispatch(*args, **kwargs)

