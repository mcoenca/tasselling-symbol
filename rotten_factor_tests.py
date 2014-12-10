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

def run_test(iterations, dimension, lambda_v, step, filename):
    ratings = get_normalized_ratings()
    num_ratings = len(ratings)
    num_train = (4 * num_ratings) // 5 
    ratings_train = ratings[:num_train]
    ratings_test = ratings[num_train:]

    #critics, movies = sgd.stochastic_descent(10, 0, ratings_train, 4475, 4539)
    sgd = matrix_factor.StochasticGradientDescent(ratings_train, 
        test_examples=ratings_test, critics=4475, movies=4539, dimension=dimension,
        lambda_val=lambda_v, filename=filename, step=step)
    sgd.stochastic_descent(iterations, print_error=True, print_iter=True)

def main():
    parser = argparse.ArgumentParser(description='Run test')
    parser.add_argument('-i', '--iter', dest='iter', metavar='i',
                        help='Number of iterations',
                        required=True)
    parser.add_argument('-d', '--dim', dest='dim', metavar='d',
                        help='The free dimension',
                        required=True)
    parser.add_argument('-l', '--lambda', dest='lambda_val', metavar='l',
                        help='The value of lambda',
                        required=True)
    parser.add_argument('-s', '--step', dest='step', metavar='s',
                        help='The step size',
                        required=True)
    parser.add_argument('-f', '--fname', dest='fname', metavar='f',
                        help='The filename',
                        required=True)
    args = parser.parse_args()
    iterations = int(args.iter)
    dimension = int(args.dim)
    lambda_val = float(args.lambda_val)
    step = float(args.step)
    directory = args.fname
    filename = "{}/test-i{}d{}l{}s{}.json".format(directory,iterations,dimension,lambda_val,step)
    run_test(iterations,dimension,lambda_val,step,filename)

def random_test():
    ratings = get_normalized_ratings()
    num_ratings = len(ratings)
    num_train = (4 * num_ratings) // 5 
    ratings_train = ratings[:num_train]
    ratings_test = ratings[num_train:]
    error = 0
    for rating in ratings_train:
        _,_,value = rating
        calc = np.random.normal(0,100)
        error +=  abs(value - calc)
    print(error / len(ratings_train))
    error = 0
    for rating in ratings_train:
        _,_,value = rating
        error +=  abs(value)
    print(error / len(ratings_train))



if __name__ == '__main__':
    #random_test()
    main()