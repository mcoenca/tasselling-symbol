import json
import peewee
from meta_db import *

def critic_review_to_db(review, movie):
    link = None
    if 'link' in review:
        link = review['link']
    try:
        return CriticReview.create(
                link = link,
                critic = review['critic'],
                excerpt = review['excerpt'],
                score = review['score'],
                movie = movie
            )
    except peewee.IntegrityError:
        print(' Movie already in database')
        return None

def user_review_to_db(review, movie):
    try:
        return UserReview.create(
            date = review['date'],
            total_thumbs = review['total_thumbs'],
            review = review['review'],
            name = review['name'],
            total_ups = review['total_ups'],
            score = review['score'],
            movie = movie)
    except peewee.IntegrityError:
        print(' Movie already in database')
        return None


def movie_to_db(movie, movie_id, critic_rc, user_rc):
    avguserscore = int(10*float(movie['avguserscore']))
    genre = movie['genre']
    score = movie['score']
    rating = movie['rating']
    cast = movie['cast']
    runtime = movie['runtime']
    url = movie['url']
    name = movie['name']
    rlsdate = movie['rlsdate']
    try:
        return Movie.create(
            id = movie_id,
            avguserscore = avguserscore,
            genre = genre,
            score = score,
            rating = rating,
            cast = cast,
            runtime = runtime,
            url = url,
            name = name,
            rlsdate = rlsdate,
            criticreviews = critic_rc,
            userreviews = user_rc)
    except peewee.IntegrityError:
        print(' Movie already in database')
        return None

def read_json(filename):
    with open(filename) as f:
        json_data = json.load(f)
        print(json_data.keys())
        movie_title = json_data['title']
        movie_key = json_data['key']
        movie_data = json_data['first']
        critic_reviews = json_data['critic_reviews']
        user_reviews = json_data['user_reviews']
        critic_rc = critic_reviews['count']
        user_rc = user_reviews['count']
        print(critic_reviews.keys())
        print(critic_reviews['count'])
        print(critic_reviews['result'][0].keys())
        print(user_reviews.keys())
        movie = movie_to_db(json_data['first'], movie_key, critic_rc, user_rc)
        for review in critic_reviews['result']:
            critic_review_to_db(review, movie)
        for review in user_reviews['reviews']:
            user_review_to_db(review, movie)

read_json('meta/meta_0.json')