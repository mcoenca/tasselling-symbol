#!/usr/bin/python3

import numpy as np
import random as rand

class StochasticGradientDescent:
	__step_size = 1
	__lambda_val = 0.1
	__dimension = 1

	def __init__(self, step, l, dimension):
		self.__lambda_val = l
		self.__step_size = step
		self.__dimension = dimension

	def stochastic_descent(self, iters, thresh, examples, movies, critics):
		critic_rows = np.random.rand(movies, self.__dimension)
		movie_cols = np.random.rand(self.__dimension, critics)
		num_examples = len(examples)
		thresh = 0
		sumgrads = 0
		for _ in range(iters):
			rand.shuffle(examples)
			for example in examples:
				rows = critic_rows[example[0],:]
				cols = movie_cols[:,example[1]]
				value = example[2]
				row_grad, col_grad = \
					self.__partial_gradient(rows, cols, value, num_examples)
				critic_rows[example[0], :] -= row_grad
				movie_cols[:, example[1]] -= col_grad
				sumgrads += sum(abs(row_grad))+sum(abs(col_grad))
			if sumgrads <= thresh:
				break
			sumgrads = 0
		return critic_rows, movie_cols


	def __partial_gradient(self, row, col, value, count):
		#calculation
		calculated_value = row.dot(col)
		gradient = -2*(value - calculated_value)
		gradient_step = self.__step_size * gradient
		#column reg
		regularize_const = self.__lambda_val*2/float(count)
		row_regularize = row*regularize_const
		column_regularize = col*regularize_const
		#update
		row_gradient = gradient_step*col.T + row_regularize
		col_gradient = gradient_step*row.T + column_regularize
		#update
		return row_gradient, col_gradient

def train_test(train, test, movies, critic, sgd, iters):
	row, col = sgd.stochastic_descent(iters, train, movies, critics)
	predictor = row*col
	badness = 0
	for ex in train:
		i,j,rate = ex
		badness += (predictor[i,j] - rate)**2

sgd = StochasticGradientDescent(0.02, 0, 2)
test_data = [(0,0,3),(0,1,6),(0,2,9),(1,0,4),(1,1,8),(1,2,12),(2,0,5),(2,1,10),(2,2,15)]

row,col = sgd.stochastic_descent(500, 0, test_data, 3, 3)
print(row)
print(col)
print()
print(row.dot(col))
