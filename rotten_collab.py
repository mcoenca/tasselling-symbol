#!/usr/bin/env python3

import sys
import pickle
import argparse
import random
import peewee
from os import path
import rotten_db as db
import numpy as np
from scipy import sparse
from numpy import linalg

#----------------------------------------------------------#
# The class that actually performs collaborative filtering #
#----------------------------------------------------------#

class RottenLearn():

    def __init__(self, num_critics, num_movies, reviews, method='cos'):

        self.method = method
        self._set_method_functions()

        self.num_critics = num_critics
        self.num_movies  = num_movies

        self.coo = self._make_coo(reviews) 

        self.matrix       = self.coo.todense()
        self.csr          = self.coo.tocsr()
        self.csc          = self.coo.tocsc()
        self.critic_means = self._calc_critic_means()
        self.critic_sim   = self._calc_critic_sim()

        self.movie_reviewers, self.movie_reviews = self._calc_movie_reviews()

    def _set_method_functions(self):
        if self.method == 'cosine':
            self._calc_critic_sim = self._calc_critic_sim_cos
            self.estimate_rating = self._estimate_rating_cos
        elif self.method == 'pearson':
            self._calc_critic_sim = self._calc_critic_sim_pearson
            self.estimate_rating = self._estimate_rating_pearson
        else:
            raise ValueError("RottenLearn: unknown similarity method {}"
                    .format(self.method))

    def _unzip_review_tuples(self, reviews):
        critics = []
        movies  = []
        scores  = []
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

    def _make_coo(self, reviews):
        critics, movies, scores = self._unzip_review_tuples(reviews)
        return sparse.coo_matrix(
                (scores, (critics, movies)),
                shape=(self.num_critics, self.num_movies))

    def _calc_critic_means(self):
        n_rev_per_critic = np.maximum(1, self.csr.getnnz(axis=1).reshape(-1,1))
        return np.divide(self.csr.sum(axis=1), n_rev_per_critic)

    def _calc_movie_reviews(self):
        movie_reviews   = [None] * self.num_movies
        movie_reviewers = [None] * self.num_movies

        for m in range(self.num_movies):
            r = self.csc[:, m]
            nz = r.nonzero()
            movie_reviewers[m] = nz[0]
            movie_reviews[m] = r[nz]

        return movie_reviewers, movie_reviews

    # Calculate the dot products of the matrix rows,
    # divided by the product of the norms
    # Set the diagonal to zero
    def _calc_normalized_dot_products(self, csrmat):
        simil = csrmat.dot(csrmat.transpose()).todense()
        normvec = np.maximum(np.sqrt(np.diag(simil)), 1)
        ret = np.divide(simil, normvec) # divide columns
        ret = np.divide(ret, normvec.reshape(-1,1)) # divide rows
        for i in range(simil.shape[0]):
            ret[i,i] = 0
        return ret

    # Calculate the similarity between critics using Pearson correlation
    def _calc_critic_sim_pearson(self):
        zeromean = self.csr.copy()
        for critic_id in range(self.num_critics):
            nnz = zeromean[critic_id, :].nonzero()
            # -= operator is not implemented
            zeromean[critic_id, nnz[1]] = \
                zeromean[critic_id, nnz[1]] - self.critic_means[critic_id]

        zeromean.eliminate_zeros()
        return self._calc_normalized_dot_products(zeromean)

    # Calculate the similarity between critics using dot product (cosine)
    def _calc_critic_sim_cos(self):
        return self._calc_normalized_dot_products(self.csr)

    def get_critic_similarity(self, i, j):
        return self.critic_sim[i,j]

    def _estimate_rating_cos(self, critic_id, movie_id, k):
        sim = self.critic_sim[critic_id, self.movie_reviewers[movie_id]]
        simidx = np.argsort(np.abs(sim))[0,-k:]
        simsort = sim[0, simidx]
        totsim = np.sum(np.abs(simsort))

        if totsim == 0:
            return self.critic_means[critic_id]

        tmp = np.multiply(self.movie_reviews[movie_id][0, simidx], simsort)
        return np.sum(tmp) / totsim

    def _estimate_rating_pearson(self, critic_id, movie_id, k):
        reviewers = self.movie_reviewers[movie_id]
        sim = self.critic_sim[critic_id, reviewers]
        simidx = np.argsort(np.abs(sim))[0,-k:]
        simsort = sim[0, simidx]
        totsim = np.sum(np.abs(simsort))

        if totsim == 0:
            return self.critic_means[critic_id]

        tmp = self.movie_reviews[movie_id][0, simidx]
        tmp = tmp - self.critic_means[reviewers][simidx, 0]
        return np.sum(np.multiply(tmp, simsort)) / totsim

    def estimate_all_ratings(self, k, est):
        for m in range(self.num_movies):
            print("\rEstimating all ratings for movie {}".format(m), end='')
            for c in range(self.num_critics):
                if estimates[c,m] != 0:
                    continue # already estimated
                est[c,m] = self.estimate_rating(c,m,k)
        print()
        return est

    def compare_test_ratings(self, r_test, k):
        c_test, m_test, s_test = self._unzip_review_tuples(r_test)         
        n = len(c_test)
        estimates = self.coo.todense()
        errors = np.zeros(n)

        for i in range(n):
            print("\rEstimating rating {}/{}".format(i+1,n), end='')
            c = c_test[i]
            m = m_test[i]
            s = s_test[i]
            e = self.estimate_rating(c,m,k)
            estimates[c,m] = e
            errors[i] = abs(e-s)

        print()
        err_mean = errors.mean()
        err_std = errors.std()
        return err_mean, err_std, estimates

#-----------------------------------#
# Getting stuff out of the database #
#-----------------------------------#

def shuffle_split(l, p):
    n = len(l)
    m = int(n * p)
    random.shuffle(l)
    return l[:m], l[m:]

def get_best_critics(n):
    return (db.Critic
            .select(db.Critic.id)
            .join(db.Review)
            .group_by(db.Critic.id)
            .having(peewee.fn.Count(db.Review.movie) >= n))

def get_reviews(p, n):
    reviews = list(db.Review
        .select(
            db.Review.critic,
            db.Review.movie,
            db.Review.score)
        .where(db.Review.critic << get_best_critics(n))
        .where(db.Review.is_top == False)
        .tuples())

    return shuffle_split(reviews, p)

def get_db_data_size():
    num_critics = db.Critic.select().count()
    num_movies = db.Movie.select().count()
    return num_critics, num_movies

#-------------------------------------------------------------#
# Train the collaborative filtering model on part of the data #
#-------------------------------------------------------------#

def train(method, p, n):
    num_critics, num_movies = get_db_data_size()

    print("Getting reviews from database")
    r_train, r_test = get_reviews(p, n)
    
    print("Training model using {} reviews".format(len(r_train)))
    learn = RottenLearn(num_critics, num_movies, r_train, method=method)

    data = {
        "learn":     learn,
        "r_train":   r_train,
        "r_test":    r_test,
        "estimates": sparse.coo_matrix((num_critics, num_movies))
    }

    print("All done boss!")
    return data

#--------------------------------------#
# Compare estimates to observed values #
#--------------------------------------#

def compare_estimates(data, k):
    learn  = data["learn"]
    r_test = data["r_test"]

    print("Calculating error statistics")
    err_mean, err_std, estimates = learn.compare_test_ratings(r_test, k)
    print("Error stats: mean = {}  std dev = {}".format(err_mean, err_std))

    data["estimates"] = estimates

    print("All cool bro!") 

#-------------------#
# Actually do stuff #
#-------------------#

def main():
    parser = argparse.ArgumentParser(description='Collaborative filtering yo!')
    parser.add_argument('-m', metavar='METHOD',
            choices=['pearson', 'cosine'], default='cosine',
            help='Similarity measurement method: cosine, pearson')
    parser.add_argument('-p', metavar='PROPORTION', type=float,
            help='Proportion of data to use as training samples')
    parser.add_argument('-k', metavar='K', type=int, default=10,
            help='Number of nearest neighbors to use for estimation')
    parser.add_argument('-n', metavar='N', type=int, default=10,
            help=
            'Only consider reviewers which have reviewed more than N films')

    args = parser.parse_args()
    
    data = train(args.m, args.p, args.n)
    compare_estimates(data, args.k)

if __name__ == '__main__':
    main()
