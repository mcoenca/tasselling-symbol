#!/usr/bin/env python3

import sys
import pickle
import argparse
import random
import rotten_db as db
import numpy as np
from scipy import sparse
from numpy import linalg

#----------------------------------------------------------#
# The class that actually performs collaborative filtering #
#----------------------------------------------------------#

class RottenLearn():

    def __init__(self, num_critics, num_movies, reviews, method='cos'):

        self.method      = method
        self.num_critics = num_critics
        self.num_movies  = num_movies

        self.coo = self._make_coo(reviews) 

        self.matrix       = self.coo.todense()
        self.csr          = self.coo.tocsr()
        self.csc          = self.coo.tocsc()
        self.critic_means = self._calc_critic_means()
        self.critic_sim   = self._calc_critic_sim()

        self.movie_reviewers, self.movie_reviews = self._calc_movie_reviews()

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

    def _calc_critic_sim(self):
        if self.method == 'cosine':
            return self._calc_critic_sim_cos()
        if self.method == 'pearson':
            return self._calc_critic_sim_pearson()
        raise ValueError('Unknown method ' + method)

    def get_critic_similarity(self, i, j):
        return self.critic_sim[i,j]

    def estimate_rating(self, critic_id, movie_id, k):
        sim = self.critic_sim[critic_id, self.movie_reviewers[movie_id]]
        simidx = np.argsort(np.abs(sim))[0,-k:]
        simsort = sim[0, simidx]
        totsim = np.sum(np.abs(simsort))

        if totsim == 0:
            return self.critic_means[critic_id]

        tmp = np.multiply(self.movie_reviews[movie_id][0, simidx], simsort)
        return np.sum(tmp) / totsim

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

    
def get_reviews(p):
    reviews = list(db.Review
        .select(
            db.Review.critic,
            db.Review.movie,
            db.Review.score)
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

def train(filename, method, p):
    num_critics, num_movies = get_db_data_size()

    print("Getting reviews from database")
    r_train, r_test = get_reviews(p)
    
    print("Calculating critic similarity")
    learn = RottenLearn(num_critics, num_movies, r_train, method=method)

    data = {
        "learn":     learn,
        "r_train":   r_train,
        "r_test":    r_test,
        "estimates": sparse.coo_matrix((num_critics, num_movies))
    }

    print("Dumping data to {}".format(filename))
    with open(filename, "wb") as f:
        pickle.dump(data, f)

    print("All done boss!")

#------------------------------------#
# Calculate missing estimate reviews #
#------------------------------------#

def calculate_all_estimates(filename, k):
    print("Loading data from {}".format(filename))
    with open(filename, "rb") as f:
        data = pickle.load(f)

    learn     = data["learn"]
    estimates = data["estimates"]

    print("Estimating all remaining ratings")
    learn.estimate_all_ratings(estimates, k) 

    print("Dumping data to {}".format(filename))
    with open(filename, "wb") as f:
        pickle.dump(data, f)

    print("All cool bro!")

#--------------------------------------#
# Compare estimates to observed values #
#--------------------------------------#

def compare_estimates(filename, k):
    print("Loading data from {}".format(filename))
    with open(filename, "rb") as f:
        data = pickle.load(f)

    learn  = data["learn"]
    r_test = data["r_test"]

    print("Calculating error statistics")
    err_mean, err_std, estimates = learn.compare_test_ratings(r_test, k)
    print("Error stats: mean = {}  std dev = {}".format(err_mean, err_std))

    data["estimates"] = estimates

    print("Dumping data to {}".format(filename))
    with open(filename, "wb") as f:
        pickle.dump(data, f)

    print("All finished pal!") 

#-------------------#
# Actually do stuff #
#-------------------#

def main():
    parser = argparse.ArgumentParser(description='Collaborative filtering yo!')
    parser.add_argument('command', metavar='COMMAND',
            choices=["train", "estimate", "compare"],
            help='Whatchu wanna do: train, estimate, compare')
    parser.add_argument('-f', metavar='FILE', default='collab.pickle',
            help='File to load data from and dump data to')
    parser.add_argument('-m', metavar='METHOD',
            choices=['pearson', 'cosine'], default='cosine',
            help='Similarity measurement method: cosine, pearson')
    parser.add_argument('-p', metavar='PROPORTION', type=float,
            help='Proportion of data to use as training samples')
    parser.add_argument('-k', metavar='K', type=int, default=10,
            help='Number of nearest neighbors to use for estimation')

    args = parser.parse_args()
    if args.command == 'train':
        train(args.f, args.m, args.p)
    if args.command == 'estimate':
        calculate_all_estimates(args.f, args.k)
    elif args.command == 'compare':
        compare_estimates(args.f, args.k)

if __name__ == '__main__':
    main()
