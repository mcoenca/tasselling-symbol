#!/usr/bin/env python

import json, peewee, argparse, os, os.path
from db import *

INPUT_DIR = 'rotten'

RESET_SEQ = '\033[0m'
RED_SEQ = '\033[1;31m'

def red_print(str):
    print(RED_SEQ + str + RESET_SEQ)

def get_or_create_actor(name, rotten_id):
    try:
        return Actor.create(name = name, rotten_id = rotten_id)
    except peewee.IntegrityError:
        return Actor.get(name = name)

def store_roles(actor, movie):
    db_actor = get_or_create_actor(actor['name'], actor['id'])
    characters = actor.get('characters', [''])
    for character in characters:
        Role.create(character = character, actor = db_actor, movie = movie)

def store_cast(cast, movie):
    for actor in cast:
        store_roles(actor, movie)

def int_or_none(str):
    if str:
        return int(str)
    else:
        return None

def store_movie(movie):
    try:
        imdb_id = movie['alternate_ids']['imdb']
    except KeyError:
        imdb_id = None
    rotten_id = int(movie['id'])
    year = int_or_none(movie['year'])
    runtime = int_or_none(movie['runtime'])
    critics_score = int(movie['ratings']['critics_score'])
    audience_score = int(movie['ratings']['audience_score'])
    try:
        return Movie.create(
            title = movie['title'],
            rotten_id = rotten_id,
            imdb_id = imdb_id,
            year = year,
            mpaa_rating = movie['mpaa_rating'],
            runtime = runtime,
            critics_score = critics_score,
            audience_score = audience_score,
            synopsis = movie['synopsis'])
    except peewee.IntegrityError:
        red_print('  Error: movie already in database')
        return None

def get_or_create_critic(name):
    try:
        return Critic.create(name = name)
    except peewee.IntegrityError:
        return Critic.get(name = name)

def get_or_create_pub(name):
    try:
        return Publication.create(name = name)
    except peewee.IntegrityError:
        return Publication.get(name = name)

def store_review(review, movie, is_top = False):
    critic = get_or_create_critic(review['critic'])
    publication = get_or_create_pub(review['publication'])
    is_fresh = review['freshness'] == 'fresh'
    original_score = review.get('original_score', None)
    return Review.create(
        critic = critic,
        movie = movie,
        publication = publication,
        is_top = is_top,
        is_fresh = is_fresh,
        original_score = original_score,
        score = 0,
        quote = review['quote'],
        date = review['date'])

def store_json(info):
    if not 'title' in info:
        print('  No title found')
        return
    print('  Title:', info['title'])

    if not 'movie' in info:
        red_print('  No movie info found')
        return

    movie = store_movie(info['movie'])
    if not movie:
        return
    store_cast(info['movie']['abridged_cast'], movie)

    if 'top_critic_reviews' in info:
        top_rev = info['top_critic_reviews']
        len_top = len(top_rev)
        print('  Found top critic reviews: {}'.format(len_top))
        for rev in top_rev:
            store_review(rev, movie, is_top = True)
    else:
        red_print('  No top critic reviews found')

    if 'all_reviews' in info:
        all_rev = info['all_reviews']
        len_all = len(info['all_reviews'])
        print('  Found all critic reviews: {}'.format(len_all))
        for rev in all_rev:
            store_review(rev, movie)
    else:
        red_print('  No "all reviews" found')

def store_all(dir):
    files = os.listdir(dir)
    n = len(files)
    for i, filename in enumerate(files):
        if filename[-5:] == '.json':
            print('{}/{}: Opening {}'.format(i+1, n, filename))
            with open(os.path.join(dir, filename), 'r') as f:
                info = json.load(f)
            with db.transaction():
                store_json(info)
            if i < n-1:
                print()

def main():
    parser = argparse.ArgumentParser(
        description='Parse json files downloaded from rotten tomatoes'
        + ' and store them in the database')
    parser.add_argument('-d', '--dir', default=INPUT_DIR,
        help='Directory in which JSON data is stored (default: {})'.
        format(INPUT_DIR))
    args = parser.parse_args()
    store_all(args.dir)

if __name__ == '__main__':
    main()