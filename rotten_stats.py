import json, peewee, argparse
from rotten_db import *
import statistics as stats
import numpy as np

def reviews_per_movie():
    movies = Movie.select(Movie.id, Movie.title)
    tops = []
    others = []
    for item in movies:
        reviews = Review.select(Review.is_top).where(Review.movie == item.id)
        top = 0
        other = 0
        for review in reviews:
            if review.is_top:
                top += 1
            else:
                other += 1
        tops.append(top)
        others.append(other)
    return {
     "tops": tops, 
     "others": others
    }

def print_stats(name, l, percentiles):   
    print("{} :: mean: {} stdev: {}"
        .format(name, '%.2f' % np.mean(l), '%.2f' % np.std(l)))
    for percentile in percentiles:
        print("{} :: {}'th percentile : {}"
            .format(name, percentile, '%.2f' % np.percentile(l, percentile)))

def reviews_per_critic():
    results = Review.select().order_by(Review.critic)
    current_critic = '%%%%%##%%^%%%%' #that magic string
    top = 0
    other = 0
    count = 0
    critic_list = []
    for result in results:
        if result.critic.name !=  current_critic:
            entry = (current_critic, top, other-top, count-top)
            critic_list.append(entry)
            top = 0
            other = 0
            count = 0
            current_critic = result.critic.name
        if result.is_top :
            top += 1
        else:
            other += 1
        count += 1
    entry = (current_critic, top, other-top, count-top)
    critic_list.append(entry)
    return sorted(critic_list, key=lambda x: -(x[3]))


def reviews_per_publication():
    results = Review.select().order_by(Review.publication)
    current_publication = '%%%%%##%%^%%%%' #that magic string
    top = 0
    other = 0
    count = 0
    publication_list = []
    for result in results:
        if result.publication.name !=  current_publication:
            entry = (current_publication, top, other-top, count-top)
            publication_list.append(entry)
            top = 0
            other = 0
            count = 0
            current_publication = result.publication.name
        if result.is_top :
            top += 1
        else:
            other += 1
        count += 1
    entry = (current_publication, top, other-top, count-top)
    publication_list.append(entry)
    return sorted(publication_list, key=lambda x: -(x[3]))

def get_or_compute(filename, function):
    data = None
    try:
        with open(filename,'r') as infile:
            data = json.load(infile)
        print("loaded data from file")
    except:
        print("computing data")
        data = function()
        with open(filename,'w') as outfile:
            json.dump(data, outfile)
    return data

def reviews_stats():
    results = get_or_compute('reviews_list.json', reviews_per_movie)
    print_stats("top", results["tops"], [25,50,75])
    print_stats("other", results["others"], [25,50,75])

def critics_stats():
    data = get_or_compute('critics_list.json', reviews_per_critic)
    names, top, other, total = zip(*(data[1:]))
    print_stats("top",top, [50,80,90,99])
    print_stats("other",other,[50,80,90,99])
    print_stats("total",total,[50,80,90,99])

def publications_stats():
    data = get_or_compute('publications_list.json', reviews_per_publication)
    names, top, other, total = zip(*(data[1:]))
    print_stats("top",top, [50,80,90,99])
    print_stats("other",other,[50,80,90,99])
    print_stats("total",total,[50,80,90,99])

publications_stats()
