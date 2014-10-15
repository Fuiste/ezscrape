from middleware.yelpspider import YelpSpider
from app.models import *


def scrape_yelp_for_reviews(property_id):
    """
    rq function for scraping the yelp reviews in a worker.
    """
    prop = Property.objects.get(id=property_id)
    prop.save()
    review_date_cutoff = 2011
    yelp_spider = YelpSpider(url=prop.yelp_url, property_id=prop.id, provider_name="Yelp", review_date_cutoff=review_date_cutoff)
    print "Starting Yelp spider."
    yelp_spider.start()
    print "YELP DONE"
    prop.yelp_scraped = True
    prop.save()
    # If there's no topics yet, build them (now using NOUNPHRASE).
