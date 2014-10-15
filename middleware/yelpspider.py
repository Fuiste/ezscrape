# -*- coding: utf-8 -*-
from __future__ import absolute_import
import json
import os
import random
import re
import urllib
import datetime
import urllib2
from dateutil.relativedelta import relativedelta
from pattern.web import Crawler, URL, DOM, plaintext, abs
import time
import unicodedata
import logging
from app.models import Property, ScrapedTextProvider, Review

__author__ = "MDee"

logger = logging.getLogger(__name__)

# Translation table for converting problematic unicode characters,
#    e.g. quote characters
TRANSLATE_TABLE = {
    0x201c: u'"', 0x201d: u'"',
    0x2019: u"'"
}

CUTOFF_HIT = "cutoff_hit"
# TODO: Is there a better way to handle bad unicode data?
def encode_utf(s):
    """Return a unicode string from s with translations of
    problematic characters.
    """
    return unicode(s).translate(TRANSLATE_TABLE)

class ScrapedTextProviderDTO(object):
    """
    """
    def __init__(self, name, url, rated=True, domains=[], max_rating=5.0):
        '''Create a provider.'''
        self.name = name
        self.url = url
        self.rated = rated
        self.max_rating = max_rating
        if domains:
            self.domains = domains
        else:
            base_url = URL(url)
            self.domains = [base_url.domain]

class ScrapedTextDTO(object):
    """
    """
    def __init__(self, property_id, provider, content, pub_date, date_format="%Y-%m-%d", rating=None, title=None):
        # Each of these is raw, scraped data
        self.property_id = property_id
        self.provider = provider
        self.rating = rating
        self.content = content
        self.pub_date = pub_date
        self.title = title
        self.date_format = date_format
        # Additionally, store the normalized rating
        try:
            self.normalized_rating = float(rating) / provider.max_rating
        except TypeError:
            print "Error trying to create normalized rating for TripAdvisor review"
            print "Rating value: {0}".format(rating)
            raise Exception

    def save(self, *args, **kwargs):
        """
        """
        property = Property.objects.get(pk=self.property_id)

    def __unicode__(self):
        return "\nDate: {0} Rating: {1}\nSource: {2}\n{3}".format(self.pub_date, self.rating, self.content)

    def __str__(self):
        return unicode(self).encode("utf-8")

class Spiderman(Crawler):
    name = ""
    base_url = None
    domains = []
    date_format = "%Y-%m-%d"
    unique_attributes = None
    desired_count = 0
    retrieved_count = 0
    # text_sage = TextSage()

    def __init__(self, url, property_id, provider_name, rated_text=True, domains=None, relative=True,
                 delay_interval=(3, 5),
                 verbose=True, links=None, organization_name=None, scrape_count_limit=None, review_date_cutoff=None, *args, **kwargs):
        """
        """
        super(Spiderman, self).__init__(*args, **kwargs)
        self.organization_name = organization_name
        self.domains = domains
        self.delay_interval = delay_interval
        self.rated_text = rated_text
        self.property_id = property_id
        self.existing_count = 0
        self.provider = ScrapedTextProviderDTO(name=provider_name, url=self.base_url, domains=self.domains)
        self.links = links
        self.scrape_count_limit = scrape_count_limit
        self.review_date_cutoff = review_date_cutoff
        self.verbose = verbose
        self.url = url
        # Newly saved reviews are put in here
        self.new_reviews = []

    def fetch_url(self, url, proximo_route=True, post_data=None):
        """
        Tries to route through PROXIMO_URL proxy, if it's set
        """
        print "Fetching from URL: {0}".format(url)
        # if proximo_route and os.environ.get("PROXIMO_URL", "") != "":
        #     logger.info("Proximo set!")
        #     proxy = urllib2.ProxyHandler({"http": os.environ.get("PROXIMO_URL", "")})
        #     auth = urllib2.HTTPBasicAuthHandler()
        #     opener = urllib2.build_opener(proxy, auth, urllib2.HTTPHandler)
        #     urllib2.install_opener(opener)
        try:
            if post_data:
                conn = urllib2.urlopen(url, post_data)
            else:
                conn = urllib2.urlopen(url)
            return conn.read()
        except urllib2.HTTPError as e:
            print "ERROR FETCHING URL!"
            print e
            return None

    def page_is_blocked(self, dom):
        raise NotImplementedError

    def random_delay(self):
        """Sleeps for a random number of seconds within the interval specified
        by self.delay_period.
        """
        # Make delay interval inclusive of both ends
        min, max = self.delay_interval[0], self.delay_interval[1] + 1
        delay_period = random.choice(range(min, max))
        if self.verbose:
            logger.info("Delaying for {0} seconds".format(delay_period))
        time.sleep(delay_period)
        return None

    def get_unique_attributes(self):
        return self.unique_attributes

    def get_dom(self, link, source=None):
        """Return a pattern.web.DOM object given a link or source html."""
        return DOM(source) if source else DOM(self.fetch_url(url=link))

    def scrape_rating(self, elem):
        """Returns a rating value (float) given a base element."""
        raise NotImplementedError

    def scrape_content(self, elem):
        """Returns a review's content given a base element."""
        raise NotImplementedError

    def scrape_date(self, elem):
        """Returns a review's publish date given a base element."""
        raise NotImplementedError

    def scrape_title(self, elem):
        return ""

    def scrape_base_element(self, elem):
        """Takes a "base" element from the DOM and wraps it up as a ScrapedDTO

        Args:
            elem: An object representing a review / scraped block of text
        Returns:
            A new ScrapedTextDTO instance
        """
        content = self.scrape_content(elem)
        date = self.scrape_date(elem)
        if date is None:
            print "DATE IS NONE, SKIPPING REVIEW"
            return None
        rating = None
        title = self.scrape_title(elem)
        if self.rated_text:
            rating = self.scrape_rating(elem)
            # Return a ScrapedText instance
        scraped_elem = ScrapedTextDTO(provider=self.provider, property_id=self.property_id, content=content,
                                      pub_date=date, date_format=self.date_format, rating=rating, title=title)
        return scraped_elem

    def start(self, limit=None):
        """Start crawlin the spider

        Args:
            limit: An int or None, how many of the links to scrape. If None, visit all links in self.get_links().
        Returns:
            An integer count of the number of reviews grabbed
        """
        if not self.links:
            page_links_to_crawl = self.get_links()
            if not page_links_to_crawl or page_links_to_crawl == -1:
                logger.info("No links returned to crawl, exiting")
                return self.new_reviews
            self.links = page_links_to_crawl
        for index, link in enumerate(self.links):
            if self.scrape_count_limit and self.retrieved_count >= self.scrape_count_limit:
                logger.info("Hit limit for scraping!")
                break
            elif index >= 2 and self.retrieved_count == 0:
                logger.info("Haven't hit any new reviews yet after loading 2+ pages, exiting")
                break
            logger.info("Visiting {0}".format(link))
            result = self.visit(link)
            if result == CUTOFF_HIT:
                print "Cutoff hit! Breaking out of the scrape"
                break
            if self.verbose:
                logger.info("Finished scraping {0}".format(link))
        if self.verbose:
            logger.info("Desired: {0} & Retrieved: {1}".format(self.desired_count, self.retrieved_count))
            logger.info("All done. Spider's going to sleep.")
        return self.new_reviews

    def fail(self):
        """What to do if something goes wrong. By default, does nothing."""
        logger.error("Failure occurred. Moving on...")
        pass

    def convert_to_abs(self, link):
        """Converts a relative URL to an absolute url.

        e.g. '/biz/hyatt-#hrid:123' --> 'http://www.hipadvisor.com/biz/hyatt-#hrid123'
        """
        base_url = URL(self.url)
        return abs(link, base=base_url.string)

    def save_item(self, scraped_text_dto):
        """Saves an item to a database. If something goes wrong, rolls back
        the transaction and runs self.fail().

        Arguments:
            scraped_text_dto: An instance of ScrapedTextDTO
        """
        self.retrieved_count += 1
        property = Property.objects.get(pk=scraped_text_dto.property_id)
        content = scraped_text_dto.content
        content = content.replace("<br>", "\n");
        pub_date = datetime.datetime.strptime(scraped_text_dto.pub_date, scraped_text_dto.date_format)
        rating = float(scraped_text_dto.rating)
        if len(Review.objects.filter(text=content, grade=rating)):
            print "Already existed"
        else:
            rated_scraped_text = Review(text=content, created_date=pub_date, grade=rating, id=Review.get_next_id())
            rated_scraped_text.save()
            # Save it to this list in order to send out an alert
            property.reviews.add(rated_scraped_text)
            if self.verbose:
                print "Saved to DB: {0}".format(rated_scraped_text)

    def visit(self, link, source=None):
        """
        Called from Spider.start() and Spider.crawl() once a Link
         visited. The `source` will be an HTML string with the content. If
         `source` isn't provided,  the source html is downloaded from the
         URL given by `link`.

        Returns the url for the visited link.
        """
        if not source:
            # Download the page from self.url if the source HTML isn't provided
            page = self.fetch_url(url=link)
            dom = DOM(page)
        else:
            dom = DOM(source)
        result = self.scrape_elements_from_dom_and_save_if_new(dom)
        if result == CUTOFF_HIT:
            print "Cutoff hit! stopping the scrape"
            return CUTOFF_HIT
        self.visited[link] = True  # Mark link as visited
        # Delay before the next visit
        self.random_delay()
        return link

    def scrape_elements_from_dom_and_save_if_new(self, dom, expanded=False):
        for elem in self.generate_base_elements(dom, expanded):
            # Skip over owner's responses
            quote = self.scrape_title(elem)
            if quote == '"Owner response"':
                continue
                # Scrape the element and get a new ReviewItem object
            scraped_text_elem = self.scrape_base_element(elem)
            if not scraped_text_elem:
                print "Received NONE from scrape_base_elem, Skipping"
                continue
            text_year = datetime.datetime.strptime(scraped_text_elem.pub_date, scraped_text_elem.date_format).date().year
            if text_year == self.review_date_cutoff:
                print "Hit a review that was written in the {0}, and the cutoff is {1}".format(text_year, self.review_date_cutoff)
                return CUTOFF_HIT
            else:
                # Save it to the database
                self.save_item(scraped_text_elem)
        return True

    def generate_base_elements(self, dom, expanded=False):
        """
        Yields each base element on the current page.
        """
        raise NotImplementedError

    def get_links(self):
        raise NotImplementedError

class YelpSpider(Spiderman):
    name = "Yelp"
    base_url = "http://www.yelp.com"
    domains = ["www.yelp.com"]
    date_format = "%Y-%m-%d"
    # Each review's permalink is unique, so use it as a unique key to prevent duplicate records
    unique_attributes = []
    date_sort_query_param = "sort_by=date_desc"
    paginated_result_query_param = "start={0}"
    reviews_per_page = 40
    url_template = "{0}?{1}&{2}"

    def get_links(self):
        # Checking up with reviews sorted in by date descending from now on
        page = self.fetch_url(url=self.url + "?" + self.date_sort_query_param)
        dom = DOM(page)
        if self.page_is_blocked(dom=dom):
            logger.info("No reviewCount span found on Yelp! Shit I wonder if we blocked n shit")
            return None
        return self._generate_page_links(dom)

    def scrape_review_count(self, dom):
        """Scrapes the count of reviews from the top level Yelp property page

        Args:
            dom: An object representing the Yelp DOM
        Returns:
            An integer of the total # of reviews for this property
        """
        review_count_span_result = dom.by_attribute(itemprop="reviewCount")
        if not review_count_span_result:
            logger.info("No reviewCount span found on Yelp")
            print dom.by_class("review-count")
            return -1
        return int(plaintext(review_count_span_result[0].content))

    def page_is_blocked(self, dom):
        review_count_span_result = dom.by_attribute(itemprop="reviewCount")
        if not review_count_span_result:
            return True
        return False

    def _generate_page_links(self, dom):
        """Constructs the page links to navigate for scraping reviews

        Generates them by scraping the number of reviews, and utilizing known structure of Yelp links

        Args:
            dom: a pattern DOM instance representing a page for the crawler to crawl
        Returns:
            A list of string urls
        """
        # Yelp organizes its reviews with 40 per page. Links to the other pages are constructed by
        # taking the base url (example: http://www.yelp.com/biz/tex-tubbs-taco-palace-madison) and appending a
        # query parameter of "start=<multiple of 40>".
        # What we'll do is grab the number of reviews from the page, and construct the links based on this known behavior
        review_count = self.scrape_review_count(dom)
        logger.info("Yelp sez it has {0} reviews for Property with PK {1}".format(review_count, self.property_id))
        self.desired_count = review_count
        self.existing_count = len(Property.objects.get(id=self.property_id).reviews.all())
        logger.info("{0} reviews already exist in DB for Property with PK {1} on Yelp".format(self.existing_count, self.property_id))
        if self.desired_count == self.existing_count or self.existing_count > self.desired_count:
            logger.info("No scraping necessary\n, attempting to save what's on the front page")
            self.scrape_elements_from_dom_and_save_if_new(dom)
            return 0
        else:
            self.desired_count -= self.existing_count
        logger.info("Scraping for {0} reviews on Yelp".format(self.desired_count))
        page_links = ["{0}?{1}".format(self.url, self.date_sort_query_param)]
        if review_count == -1:
            logger.error("Unable to find review count for url {0}".format(self.url))
            return -1
            # Send an email to mark with teh source
            # self.email_mark_error("Error trying to scrape Yelp Reviews", dom.source)
            # logger.error("Scraping for the existing count of {0} to see what happens".format(self.existing_count))
            # self.desired_count = self.existing_count
            # Logic for constructing links:
        # 1) Divide the review count by reviews_per_page
        #     - That gives you the number of pages with a full listing of reviews (40 as of 2/14/14)
        #     - Let's call that "page_count"
        # 2) Take the modulus of the review count by reviews_per_page
        #     - If it's zero, you're good
        #     - If it's not, that means there's one more page with results, so increase page count by 1
        # 3) The top-level page corresponds to page 1 of reviews
        #     - For each number in the range of 1 to (page_count + 1), take self.url and append a starting
        #       number of (reviews_per_page * index)
        page_count = int(self.desired_count / self.reviews_per_page)
        page_remainder = self.desired_count % self.reviews_per_page
        if page_remainder:
            page_count += 1
        for i in range(1, page_count):
            query_count = self.reviews_per_page * i
            query_param = self.paginated_result_query_param.format(query_count)
            page_links.append(self.url_template.format(self.url, self.date_sort_query_param, query_param))
        return page_links

    def scrape_elements_from_dom_and_save_if_new(self, dom, expanded=False):
        review_elems = self.generate_base_elements(dom)
        for elem in review_elems:
            scraped_text_elem = self.scrape_base_element(elem)
            if not scraped_text_elem:
                print "Received NONE from scrape_base_elem, Skipping"
                continue
            text_year = datetime.datetime.strptime(scraped_text_elem.pub_date, scraped_text_elem.date_format).date().year
            if text_year == self.review_date_cutoff:
                print "Hit a review that was written in the {0}, and the cutoff is {1}".format(text_year, self.review_date_cutoff)
                return CUTOFF_HIT
            else:
                # Save it to the database
                # logger.info("New record, saving")
                self.save_item(scraped_text_elem)
        return True

    def generate_base_elements(self, dom, expanded=False):
        """Gets the individual text or "base" elements on this page

        A "base" element in this case is a review. They're stored under a ul with class="reviews",
        and each review is contained in a div with the class="review"

        Args:
            dom: a pattern DOM instance
        Returns:
            A Python generator, NOT a list, of each review block
        """
        reviews_container = dom.body.by_class("reviews")[0]
        elems = reviews_container.by_class("review")
        for elem in elems:
            yield elem

    def scrape_rating(self, elem):
        """Returns a rating value (float) given a "base" element.

        A "base" element is a block of HTML containing a review

        Args:
            elem: An object representing a review in the DOM
        Returns:
            A float representing the rating given by a user, or None if it can't find it
        """
        meta_tag_result = elem.by_attribute(itemprop="ratingValue")
        if not meta_tag_result:
            logger.error("Error when trying to scrape 'ratingValue' for Yelp Review")
            logger.error("Here's the elem: {0}".format(elem))
            return None
        meta_tag = meta_tag_result[0]
        rating = float(plaintext(meta_tag.attributes["content"]))
        return rating

    def scrape_content(self, elem):
        """Scrape a review's content from base element

        Args:
            elem: An object representing a review in the DOM
        Returns:
            The review content, or None if not found
        """
        # Use pattern's plaintext method to strip tags and decode unicode
        comment_result = elem.by_class("review_comment")
        if not comment_result:
            logger.error("No review_comment class found for Yelp review")
            logger.error(elem)
            return None
        normalized_comment = unicodedata.normalize("NFD", comment_result[0].content).encode("ascii", "ignore")
        comment = plaintext(normalized_comment, keep={"br": []})
        return comment

    def scrape_date(self, elem):
        """Scrape a review's date from base element

        Args:
            elem: An object representing a review in the DOM
        Returns:
            A String of the review's date (YYYY-MM-DD), or None if not found
        """
        meta_tag_result = elem.by_attribute(itemprop="datePublished")
        if not meta_tag_result:
            logger.error("Error finding review date 'datePublished' in Yelp review")
            logger.error(elem)
            return None
        meta_tag = meta_tag_result[0]
        date = plaintext(meta_tag.attributes["content"])
        return date
