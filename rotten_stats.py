import json
import peewee
import argparse
from rotten_db import *
import stats
import numpy as np
import stats


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


def reviews_per_critic():
    results = Review.select().order_by(Review.critic)
    current_critic = results[0].critic.name 
    top = 0
    other = 0
    count = 0
    critic_list = []
    for result in results:
        if result.critic.name != current_critic:
            entry = (current_critic, top, other - top, count - top)
            critic_list.append(entry)
            top = 0
            other = 0
            count = 0
            current_critic = result.critic.name
        if result.is_top:
            top += 1
        else:
            other += 1
        count += 1
    # the subtraction here prevents top reviews from being double counted
    entry = (current_critic, top, other - top, count - top)
    critic_list.append(entry)
    return sorted(critic_list, key=lambda x: -(x[3]))


def reviews_per_publication():
    results = Review.select().order_by(Review.publication)
    current_publication = results[0].publication.name
    top = 0
    other = 0
    count = 0
    publication_list = []
    for result in results:
        if result.publication.name != current_publication:
            entry = (current_publication, top, other - top, count - top)
            publication_list.append(entry)
            top = 0
            other = 0
            count = 0
            current_publication = result.publication.name
        if result.is_top:
            top += 1
        else:
            other += 1
        count += 1
    # the subtraction here prevents top reviews from being double counted
    entry = (current_publication, top, other - top, count - top)
    publication_list.append(entry)
    return sorted(publication_list, key=lambda x: -(x[3]))


def reviews_stats():
    results = stats.get_or_compute('reviews_list.json', reviews_per_movie)
    #stats.print_stats("top", results["tops"], [25, 50, 75])
    #stats.print_stats("other", results["others"], [25, 50, 75])
    stats.latex_table_r(results["tops"],results["others"])
    stats.plot(results["tops"], 50, 
        title = "Cumulative Histogram of Top Critic Reviews per Movie",
        xlabel = "Number of Reviews",
        ylabel = "Cdf of Reviews per Movie",
        fname = "reports/plot_r_mov_top.png")
    stats.plot(results["others"], 50, 
        title = "Cumulative Histogram of Other Critic Reviews per Movie",
        xlabel = "Number of Reviews",
        ylabel = "Cdf of Reviews per Movie",
        fname = "reports/plot_r_mov_oth.png")


def critics_stats():
    # the top item in this list is blank
    # the second is really unsurprising
    data = stats.get_or_compute('critics_list.json', reviews_per_critic)
    names, top, other, total = zip(*(data[1:]))
    #stats.print_stats("top", top, [50, 80, 90, 99])
    #stats.print_stats("other", other, [50, 80, 90, 99])
    #stats.print_stats("total", total, [50, 80, 90, 99])
    stats.latex_table_r(top,other,total=total)
    stats.plot(top, 50, 
        title = "Cumulative Histogram of Movies Reviewed per Top Critic",
        xlabel = "Number of Critics",
        ylabel = "Cdf of Movies per Critic",
        fname = "reports/plot_r_crit_top.png",
        log = True)
    stats.plot(other, 50, 
        title = "Cumulative Histogram of Movies Reviewed per Other Critic",
        xlabel = "Number of Critics",
        ylabel = "Cdf of Movies per Critic",
        fname = "reports/plot_r_crit_oth.png",
        log = True)


def publications_stats():
    data = stats.get_or_compute(
        'publications_list.json', reviews_per_publication)
    names, top, other, total = zip(*(data[1:]))
    #stats.print_stats("top", top, [50, 80, 90, 99])
    #stats.print_stats("other", other, [50, 80, 90, 99])
    #stats.print_stats("total", total, [50, 80, 90, 99])
    stats.latex_table_r(top,other,total=total)
    stats.plot(top, 200, 
        title = "Cumulative Histogram of Movies Reviewed per Top Publication",
        xlabel = "Number of Publications",
        ylabel = "Cdf of Movies per Publication",
        fname = "reports/plot_r_pub_top.png")
    stats.plot(other, 200, 
        title = "Cumulative Histogram of Movies Reviewed per Other Publication",
        xlabel = "Number of Publications",
        ylabel = "Cdf of Movies per Publication",
        fname = "reports/plot_r_pub_oth.png")

print("Movie stats")
reviews_stats()
print("Critic stats")
critics_stats()
print("Publication stats")
publications_stats()
