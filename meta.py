#!/usr/bin/env python3

import requests
import json
from metacritic_api_key import MT_KEY

FIND_MOVIE_URL = 'https://byroredux-metacritic.p.mashape.com/find/movie'
SEARCH_MOVIE_URL = 'https://byroredux-metacritic.p.mashape.com/search/movie'
GET_CRITIC_REVIEWS = 'https://byroredux-metacritic.p.mashape.com/reviews'
GET_USER_REVIEWS = 'https://byroredux-metacritic.p.mashape.com/user-reviews'


def find_movie(retry, title):
    headers={
        "X-Mashape-Key": MT_KEY,
        "Content-Type": "application/x-www-form-urlencoded"
    }
    params={
        "retry": retry,
        "title": title
    }
    try:
        return requests.post(FIND_MOVIE_URL, params=params, headers=headers).json()
    except:
        return None



def search_movie(max_pages, retry, title):
    headers={
        "X-Mashape-Key": MT_KEY,
        "Content-Type": "application/x-www-form-urlencoded"
    }
    params={
        "max_pages": max_pages,
        "retry": retry,
        "title": title
    }
    try:
        return requests.post(SEARCH_MOVIE_URL, params=params, headers=headers).json()
    except:
        return None


def critic_reviews(url, sort=None):
    headers={
        "X-Mashape-Key": MT_KEY,
        "Content-Type": "application/x-www-form-urlencoded"
    }
    params={
        "url": url
    }
    if sort:
        params["sort"] = sort
    try:
        return requests.get(GET_CRITIC_REVIEWS, params=params, headers=headers).json()
    except:
        return None

def user_reviews(url, count=None, sort=None):
    headers={
        "X-Mashape-Key": MT_KEY,
        "Content-Type": "application/x-www-form-urlencoded"
    }
    params={
        "url": url
    }
    if sort:
        params["sort"] = sort
    if count:
        params["page_count"] = count
    try:
        return requests.get(GET_USER_REVIEWS, params=params, headers=headers).json()
    except:
        return None


def main():
    print(find_movie(2,'Fast & Furious 6'))
    print(search_movie(3,2,'Fast'))
    print(critic_reviews('http://www.metacritic.com/game/pc/portal-2'))
    print(user_reviews('http://www.metacritic.com/game/pc/portal-2',5))

if __name__ == '__main__':
    main()
