#!/usr/bin/python3

import sys
import requests
from rottentomatoes_api_key import RT_KEY

RT_URL_BASE = 'http://api.rottentomatoes.com/api/public/v1.0/'
RT_URL_SEARCH = RT_URL_BASE + 'movies.json' 
RT_URL_REVIEWS = RT_URL_BASE + 'movies/{}/reviews.json'

def get(url, **params):
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
