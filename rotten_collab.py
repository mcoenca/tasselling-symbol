#!/usr/bin/env python3

import sys
import pickle
import argparse
import rotten_db as db
import numpy as np
from scipy import sparse
from numpy import linalg

class RottenLearn():

    def __init__(self, critics, movies, scores, method='cos'):
        self.method       = method
        self.coo          = sparse.coo_matrix((scores, (critics, movies)))
        self.num_critics  = self.coo.shape[0]
        self.num_movies   = self.coo.shape[1]
        self.matrix       = self.coo.todense()
        self.csr          = self.coo.tocsr()
        self.csc          = self.coo.tocsc()
        self.critic_means = self._calc_critic_means()
        self.critic_sim   = self._calc_critic_sim()

    def _calc_critic_means(self):
        return np.divide(
                self.csr.sum(axis=1),
                self.csr.getnnz(axis=1).reshape(-1,1))

    def _calc_normalized_dot_products(self, csrmat):
        simil = csrmat.dot(csrmat.transpose()).todense()
        normvec = np.maximum(np.sqrt(np.diag(simil)), 1)
        ret = np.divide(simil, normvec) # divide columns
        ret = np.divide(ret, normvec.reshape(-1,1)) # divide rows
        return ret

    def _calc_critic_sim_pearson(self):
        zeromean = self.csr.copy()
        for critic_id in range(self.num_critics):
            nnz = zeromean[critic_id, :].nonzero()
            # -= operator is not implemented
            zeromean[critic_id, nnz[1]] = \
                zeromean[critic_id, nnz[1]] - self.critic_means[critic_id]

        zeromean.eliminate_zeros()
        return self._calc_normalized_dot_products(zeromean)

    def _calc_critic_sim_cos(self):
        return self_calc_normalized_dot_products(self.csr)

    def _calc_critic_sim(self):
        if self.method == 'cos':
            return self._calc_critic_sim_cos()
        if self.method == 'pearson':
            return self._calc_critic_sim_pearson()
        raise ValueError('Unknown method ' + method)

    def get_critic_similarity(self, i, j):
        return self.critic_sim[i,j]

    def estimate_rating(self, critic_id, movie_id):
        movie_ratings = self.csc[:, movie_id]
        nonzero = movie_ratings.nonzero()
        sim = self.critic_sim[critic_id, nonzero[0]]
        totsim = np.sum(sim)

        if totsim == 0:
            return self.critic_means[critic_id]

        return np.sum(
                np.multiply(movie_ratings[nonzero], sim)
                ) / totsim

    def estimate_all_ratings(self):
        ret = np.zeros((self.num_critics, self.num_movies))

        for movie_id in range(self.num_movies):
            print("Estimating all ratings for movie {}".format(movie_id))
            movie_ratings = self.csc[:, movie_id]
            nonzero = movie_ratings.nonzero()
            nnz = len(nonzero[0])
            mrnz = movie_ratings[nonzero]

            for critic_id in range(self.num_critics):
                sim = self.critic_sim[critic_id, nonzero[0]]
                totsim = np.sum(sim)

                if totsim == 0:
                    ret[critic_id, movie_id] = self.critic_means[critic_id]
                else:
                    ret[critic_id, movie_id] = np.sum(
                            np.multiply(mrnz, sim)
                            ) / totsim

        return ret

def get_reviews():
    reviews = (db.Review
        .select(
            db.Review.critic,
            db.Review.movie,
            db.Review.score)
        .where(db.Review.is_top == False)
        .tuples())

    critics = []
    movies = []
    scores = []
    dedup = set()
    n_dup = 0
    for c, m, s in reviews:
        if (c,m) in dedup:
            #print("already seen {{c:{} m:{} s:{}}}".format(c,m,s))
            n_dup += 1
            continue
        else:
            dedup.add((c,m))
        critics.append(c-1)
        movies.append(m-1)
        scores.append(s)

    print("Found {} duplicate reviews".format(n_dup))
    return critics, movies, scores

def calculate_estimates(filename):
    print("Getting reviews from database")
    critics, movies, scores = get_reviews()
    print("Calculating critic similarity")
    learn = RottenLearn(critics, movies, scores, method="pearson")
    print("Estimating all ratings")
    estimates = learn.estimate_all_ratings()
    print("Dumping estimates to {}".format(filename))
    with open(filename, "wb") as f:
        pickle.dump(estimates, f)

def compare_estimates(filename):
    print("Getting reviews from database")
    critics, movies, scores = get_reviews()
    print("Loading estimates from {}".format(filename))
    with open(filename, "rb") as f:
        estimates = pickle.load(f)
    print("Calculating error statistics")
    n = len(critics)
    errors = np.zeros(n)
    for i in range(len(critics)):
        c = critics[i]
        m = movies[i]
        s = scores[i]
        e = estimates[c,m]
        errors[i] = e - s
        #print("critic:{} movie:{} score:{} estimate:{}".format(c, m, s, e))
    err_mean = errors.mean()
    tmp = errors - err_mean
    err_var = np.dot(tmp,tmp) / tmp.size
    err_std = np.sqrt(err_var)
    print("Error stats: mean = {}  std dev = {}".format(err_mean, err_std))

def main():
    parser = argparse.ArgumentParser(description='Collaborative filtering yo!')
    parser.add_argument('command', metavar='COMMAND',
            choices=["estimate", "compare"], help='Whatchu wanna do?')
    parser.add_argument('-f', metavar='FILE', default='collab.out',
            help='estimates file')

    args = parser.parse_args()
    if args.command == 'estimate':
        calculate_estimates(args.f)
    elif args.command == 'compare':
        compare_estimates(args.f)

if __name__ == '__main__':
    main()
