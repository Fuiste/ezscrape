from django.conf.urls import patterns, include, url
from app.views import *

from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('',
    # Examples:
    # url(r'^$', 'ezscrape.views.home', name='home'),
    # url(r'^blog/', include('blog.urls')),

    url(r'^admin/', include(admin.site.urls)),
    url(r'^scrape/?$', QueueScrapeView.as_view()),
    url(r'^tag/?$', POSTagView.as_view())
)
