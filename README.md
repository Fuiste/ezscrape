ezscrape
========

## Offsite implementation of the yelp scraper for Distill

So, Yelp caught on to what we were doing with Distill on Heroku.  This is our answer.  It's a simple review scraper that can be hosted from a local IP which will ocmmunicate with Distill proper to grab reviews.

Isn't that cool?

## Setup
1. Install from requirements.txt
2. Create a new db (default is `ezscrape_db`)
3. Run an rqworker with `foreman run python manage.py rqworker`
4. Run the server with `foreman run python manage.py runserver` 
5. Make sure Distill can reach you!
6. ...
7. Profit!
