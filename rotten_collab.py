#!/usr/bin/env python3

import rotten_db as db
import numpy as np
from scipy import sparse
from numpy import linalg

class RottenLearn():

    def __init__(self, critics, movies, scores, method='cos'):
        self.coo          = self._get_review_coo(critics, movies, scores)
        self.num_critics  = self.coo.shape[0]
        self.num_movies   = self.coo.shape[1]
        self.matrix       = self.coo.todense()
        self.csr          = self.coo.tocsr()
        self.csc          = self.coo.tocsc()
        self.critic_means = self._calc_critic_means()
        self.critic_sim   = self._calc_critic_sim(method)

    def _get_review_coo(self, critics, movies, scores):
        return sparse.coo_matrix((scores, (critics, movies)))

    def _calc_critic_means(self):
        return np.divide(
                self.csr.sum(axis=1),
                self.csr.getnnz(axis=1).reshape(-1,1))

    def _calc_critic_sim_pearson(self, i, j):
        return 0

    def _calc_critic_sim_cos(self):
        simil = self.csr.dot(self.csr.transpose()).todense()
        normvec = np.maximum(np.sqrt(np.diag(simil)), 1)
        ret = np.divide(simil, normvec) # divide columns
        ret = np.divide(ret, normvec.reshape(-1,1)) # divide rows
        return ret

    def _calc_critic_sim(self, method):
        if method == 'cos':
            return self._calc_critic_sim_cos()
        else:
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
    for c, m, s in reviews:
        critics.append(c-1)
        movies.append(m-1)
        scores.append(s)

    return critics, movies, scores

def main():
    print("Getting reviews from database")
    critics, movies, scores = get_reviews()
    print("Calculating critic similarity")
    learn = RottenLearn(critics, movies, scores)
    print(learn.num_critics)
    print(learn.get_critic_similarity(0,1))
    estimates = learn.estimate_all_ratings()
    print(estimates)
    print(np.sqrt(linalg.norm(estimates - self.coo)))

if __name__ == '__main__':
    main()
