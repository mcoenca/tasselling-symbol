#!/usr/bin/env python3

import sys, requests, time
from rotten_api_key import RT_KEY

RT_URL_BASE = 'http://api.rottentomatoes.com/api/public/v1.0/'
RT_URL_SEARCH = RT_URL_BASE + 'movies.json' 
RT_URL_REVIEWS = RT_URL_BASE + 'movies/{}/reviews.json'

RATE_LIMIT_PER_SECOND = 5

MIN_WAIT_INTERVAL = 1.2 / RATE_LIMIT_PER_SECOND

LAST_GET = 0

def get(url, **params):
    while True:
        global LAST_GET
        this_get = time.time()
        time_to_wait = MIN_WAIT_INTERVAL - (this_get - LAST_GET)
        if time_to_wait <= 0:
            LAST_GET = this_get
            break
        time.sleep(time_to_wait)

    params['apikey'] = RT_KEY
    return requests.get(url, params=params).json()

def search(query, page=1, page_limit=50):
    return get(
        RT_URL_SEARCH,
        q=query,
        page=page,
        page_limit=page_limit)

def reviews(movie_id, review_type='all', country='us', page=1, page_limit=50):
    url = RT_URL_REVIEWS.format(movie_id)
    return get(
        url,
        review_type=review_type,
        country=country,
        page=page,
        page_limit=page_limit)

def main():
    print(search(sys.argv[1]))

if __name__ == '__main__':
    main()
