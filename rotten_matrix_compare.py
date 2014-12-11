#!/usr/bin/env python3

from rotten_db import *
import argparse
import numpy as np
import matrix_factor

def get_normalized_ratings():
    ratings = list(Review
        .select(Review.critic, Review.movie, Review.score)
        .tuples())
    np.random.shuffle(ratings)
    just_ratings = list(zip(*ratings))[2]
    mu = np.mean(just_ratings)
    ratings = [(c, m, (s - mu)) for (c,m,s) in ratings]
    return ratings

def run_test(ratings_train, ratings_test):
    sgd = matrix_factor.StochasticGradientDescent(ratings_train, 
        test_examples=ratings_test, critics=4475, movies=4539, dimension=40,
        lambda_val=1000, filename=None, step=0.002)
    sgd.stochastic_descent(10, print_error=False, print_iter=True)
    return sgd

def main():
    ratings = get_normalized_ratings()
    train = ratings[:len(ratings)*4//5]
    test = ratings[len(ratings)*4//5:]
    thing = run_test(train, test)
    print(thing.calculate_error(test))
    print(thing.predict(1,1))



if __name__ == '__main__':
    #random_test()
    main()
