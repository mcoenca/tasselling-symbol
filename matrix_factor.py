#!/usr/bin/python3

import numpy as np
import random as rand
import json

class StochasticGradientDescent:
	__step_size = 1
	__lambda_val = 0.1
	__dimension = 1
	__examples = None
	__test_examples = None
	__filename = None
	__iteration_record = []
	critic_rows = None
	movie_cols = None
	predictor = None
	

	def __init__(self, examples, step=0.002, lambda_val=0, dimension=1, 
				movies=None, critics=None, test_examples=None, filename=None):
		self.__lambda_val = lambda_val
		self.__step_size = step
		self.__dimension = dimension
		self.__examples = examples
		self.__test_examples = test_examples
		self.__filename = filename
		self.__regularize_const = self.__lambda_val*2/ len(self.__examples)
		if not movies or not critics:
			raise ValueError("Must specify movies and critics")
		self.critic_rows = np.random.rand(critics, self.__dimension) / self.__dimension
		self.movie_cols = np.random.rand(self.__dimension, movies) / self.__dimension


	def iteration_printer(self, it):
		example_err, example_count = self.calculate_error(self.__examples)
		if self.__filename:
			training = ("tr",it,example_err,example_count)
			testing = tuple()
			if self.__test_examples:
				test_err, test_count = self.calculate_error(self.__test_examples)
				testing = ("te",it,test_err,test_count)
			self.__iteration_record.append((training, testing))
		else:
			error, count = self.calculate_error(self.__examples)
			print("{0} : {1:0.1f} error in {2} examples => {3:0.3f} average"\
				.format("training", error, count, error/count))
			if self.__test_examples:
				error, count = self.calculate_error(self.__test_examples)
				print("{0} : {1:0.1f} error in {2} examples => {3:0.3f} average"\
					.format("testing", error, count, error/count))


	def stochastic_descent(self, iters, thresh=0, print_iter=False, 
						   print_error=False, print_every=1):
		for i in range(iters):
			sumgrads = self.stochastic_iteration()
			if sumgrads <= thresh:
				break
			if i % print_every == 0:
				if print_iter:
					print("Completed iteration {}".format(i))
				if print_error:
					self.iteration_printer(i)
		if self.__filename and print_error:
			with open(self.__filename, "w") as fp:
				params = {
					"lambda" : self.__lambda_val,
					"dimension" : self.__dimension,
					"step" : self.__step_size,
					"result" : self.__iteration_record
				}
				json.dump(params, fp, indent=4)
					

	def stochastic_iteration(self):
		sumgrads = 0
		rand.shuffle(self.__examples)
		for example in self.__examples:
			row_grad, col_grad = self.__partial_gradient(example)
			sumgrads += sum(abs(row_grad))+sum(abs(col_grad))
		return sumgrads


	def predict(self, critic, movie):
		if self.predictor == None:
			self.predictor = self.critic_rows.dot(self.movie_cols)
		return self.predictor[critic, movie]


	def calculate_error(self, examples):
		predictor = self.critic_rows.dot(self.movie_cols)
		cumulative_sq_error = 0
		for example in examples:
			critic, movie, value = example
			expected_value = predictor[critic, movie]
			cumulative_sq_error += abs(value - expected_value)
		return cumulative_sq_error, len(examples)


	def __partial_gradient(self, example):
		#extraction
		row = self.critic_rows[example[0],:]
		col = self.movie_cols[:,example[1]]
		value = example[2]
		#calculation
		calculated_value = row.dot(col)
		gradient = -2*(value - calculated_value)
		gradient_step = self.__step_size * gradient
		#column reg
		row_regularize = row*self.__regularize_const
		column_regularize = col*self.__regularize_const
		#combine
		row_gradient = gradient_step*col.T + row_regularize
		col_gradient = gradient_step*row.T + column_regularize
		#update
		self.critic_rows[example[0], :] -= row_gradient
		self.movie_cols[:, example[1]] -= col_gradient
		#return gradients
		return row_gradient, col_gradient

def main():
	test_data = [(0,0,3),(0,1,6),(0,2,9),(1,0,4),(1,1,8),(1,2,12),(2,0,5),(2,1,10),(2,2,15)]
	sgd = StochasticGradientDescent(test_data)
	sgd.stochastic_descent(200, print_error=True, print_iterations=10)
	rows = sgd.critic_rows
	cols = sgd.movie_cols
	print(rows)
	print(cols)
	print()
	print(rows.dot(cols))

if __name__ == '__main__':
	main()
