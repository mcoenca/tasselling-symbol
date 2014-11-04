import json
import peewee
from meta_db import *

def score_or_none(score):
    try:
        return int(10*float(score))
    except:
        return None

def value_or_none(dictionary, key):
    if key in dictionary:
        return dictionary[key]
    else:
        return None

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
    except peewee.IntegrityError as e:
        print(' Critic already in database')
        print(e)
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
    except peewee.IntegrityError as e:
        print(' User already in database')
        print(e)
        return None

def movie_to_db(movie, movie_id, critic_rc, user_rc):
    avguserscore = score_or_none(movie['avguserscore'])
    score = score_or_none(movie['score'])
    rlsdate = value_or_none(movie,'rlsdate')
    try:
        return Movie.create(
            id = movie_id,
            avguserscore = avguserscore,
            genre = movie['genre'],
            score = score,
            rating = movie['rating'],
            cast = movie['cast'],
            runtime = movie['runtime'],
            url = movie['url'],
            name = movie['name'],
            rlsdate = rlsdate,
            criticreviews = critic_rc,
            userreviews = user_rc)
    except peewee.IntegrityError:
        print(movie['name'])
        print(' Movie already in database')
        return None

def read_json(filename):
    with open(filename) as f:
        json_data = None
        try:
            json_data = json.load(f)
        except:
            return None
        movie_title = json_data['title']
        print(movie_title)
        movie_key = json_data['key']
        movie_data = json_data['film']
        critic_reviews = json_data['critic_reviews']
        user_reviews = json_data['user_reviews']
        if not movie_data or 'name' not in movie_data:
            print("Failed to find movie")
            return None
        if not critic_reviews or 'result' not in critic_reviews:
            print("Failed to find critic reviews")
            return None
        if not user_reviews or 'reviews' not in user_reviews:
            print("Failed to find user reviews")
            return None
        critic_rc = critic_reviews['result']
        user_rc = user_reviews['reviews']
        if not isinstance(critic_rc,list):
            return None
        if not isinstance(user_rc, list):
            return None
        movie = movie_to_db(json_data['film'], movie_key, len(critic_rc), len(user_rc))
        if not movie:
            return None
        for review in critic_reviews['result']:
            critic_review_to_db(review, movie)
        for review in user_reviews['reviews']:
            user_review_to_db(review, movie)

def load_all(basedir):
    for i in range(5000):
        filename = str(basedir)+'/meta-'+str(i)+'.json'
        read_json(filename)
        print(i)

load_all('meta')