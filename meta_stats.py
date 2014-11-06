import json
import peewee
import argparse
from meta_db import *
import stats
import numpy as np


def reviews_per_movie():
    movies = Movie.select()
    critic_reviews = []
    user_reviews = []
    for item in movies:
        critic_reviews.append(item.criticreviews)
        user_reviews.append(item.userreviews)
    return {
        "critic_reviews": critic_reviews,
        "user_reviews": user_reviews
    }


def reviews_per_user():
    results = UserReview.select().order_by(UserReview.name)
    current_user = results[0].name
    count = 0
    review_list = []
    for result in results:
        if result.name != current_user:
            entry = (current_user, count)
            review_list.append(entry)
            count = 0
            current_user = result.name
        count += 1
    # the subtraction here prevents top reviews from being double counted
    entry = (current_user, count)
    review_list.append(entry)
    return sorted(review_list, key=lambda x: -(x[1]))

def reviews_per_critic():
    results = CriticReview.select().order_by(CriticReview.critic)
    current_critic = results[0].critic
    count = 0
    review_list = []
    for result in results:
        if result.critic != current_critic:
            entry = (current_critic, count)
            review_list.append(entry)
            count = 0
            current_critic = result.critic
        count += 1
    # the subtraction here prevents top reviews from being double counted
    entry = (current_critic, count)
    review_list.append(entry)
    return sorted(review_list, key=lambda x: -(x[1]))


def movie_stats():
    data = reviews_per_movie()
    #stats.print_stats('critics', data["critic_reviews"], [25, 50, 75])
    #stats.print_stats('users', data["user_reviews"], [25, 50, 75, 90])
    stats.latex_table_m(data["critic_reviews"],data["user_reviews"])
    stats.plot(data["critic_reviews"], 200, 
        title = "Cumulative Histogram of Critic Reviews per Movie",
        xlabel = "Number of Reviews",
        ylabel = "Cdf of Reviews per Movie",
        fname = "reports/plot_m_mov_top.png")
    stats.plot(data["user_reviews"], 200, 
        title = "Cumulative Histogram of User Reviews per Movie",
        xlabel = "Number of Reviews",
        ylabel = "Cdf of Reviews per Movie",
        fname = "reports/plot_m_mov_usr.png")

def user_critic_stats():
    critics, ccounts = zip(*reviews_per_critic())

    #stats.print_stats('critics', ccounts, [25, 50, 75, 90])
    users, ucounts = zip(*reviews_per_user())
    #stats.print_stats('users', ucounts, [25, 50, 75, 90])
    stats.latex_table_m(ccounts,ucounts)
    stats.plot(ccounts, 200, 
        title = "Cumulative Histogram of Movies Reviewed per Critic",
        xlabel = "Number of Critics",
        ylabel = "Cdf of Movies per Critic",
        fname = "reports/plot_m_crit_top.png")
    stats.plot(ucounts, 200, 
        title = "Cumulative Histogram of Movies Reviewed per User",
        xlabel = "Number of Users",
        ylabel = "Cdf of Movies per User",
        fname = "reports/plot_m_crit_usr.png")

print("Movie stats")
movie_stats()
print("User and critic stats")
user_critic_stats()
