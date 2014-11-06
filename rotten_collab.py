#!/usr/bin/env python3

import rotten_db as db
import numpy as np
from scipy import sparse
from numpy import linalg

class RottenLearn():

    def __init__(self):
        self.coo         = self._get_review_coo()
        self.num_critics = self.coo.shape[0]
        self.num_movies  = self.coo.shape[1]
        self.matrix      = self.coo.todense()
        self.csr         = self.coo.tocsr()
        self.csc         = self.coo.tocsc()
        self.critic_sim  = self._calc_critic_sim()

    def _get_review_coo(self):
        reviews = (db.Review
            .select(
                db.Review.critic,
                db.Review.movie,
                db.Review.score)
            .tuples())

        critics = []
        movies = []
        scores = []
        num_reviews = 0
        for c, m, s in reviews:
            num_reviews += 1
            critics.append(c-1)
            movies.append(m-1)
            scores.append(s)

        return sparse.coo_matrix((scores, (critics, movies)))

    def _calc_critic_sim_one(self, i, j):
        return 0

    def _calc_critic_sim_cos(self):
        sim = self.csr.dot(self.csr.transpose()).todense()
        norm2 = self.csr.multiply(self.csr).sum(axis=1)
        invnorm2 = np.diagflat(1 / norm2)
        return invnorm2.dot(sim)

    def _calc_critic_sim(self, method='cosine'):
        if method == 'cosine':
            return self._calc_critic_sim_cos()
        else:
            raise ValueError('Unknown method ' + method)

    def estimate_rating_usercollab(critic_id, movie_id):
        return 0

def main():
    learn = RottenLearn()
    print(learn.coo.shape)
    print(learn.critic_sim.shape)
    print(learn.critic_sim[0,:])

if __name__ == '__main__':
    main()
