#!/usr/bin/env python3

import numpy as np
import rotten_matrix_compare
import rotten_collab

def main():
    p = 0.9
    n = 1
    k = 10

    num_critics, num_movies = rotten_collab.get_db_data_size()
    r_train, r_test = rotten_collab.get_reviews(p, n)
    
    collab = rotten_collab.RottenLearn(
            num_critics, num_movies, r_train, method='pearson')

    _, _, est = collab.compare_test_ratings(r_test, k)
    
    mu = np.mean([s for (c,m,s) in r_train])
    r_train_factor = [(c, m, s-mu) for (c,m,s) in r_train]
    
    sgd = rotten_matrix_compare.run_test(r_train_factor, r_test)
    
    err = np.zeros(len(r_test))
    for i, (c,m,s) in enumerate(r_test):
        mf = sgd.predict(c,m)
        err[i] = abs(s - (mf + est[c-1, m-1])/2)

    err_avg = np.mean(err)
    err_std = np.std(err)
    print("Mean err: {}  std dev: {}".format(err_avg, err_std))

if __name__ == '__main__':
    main()

