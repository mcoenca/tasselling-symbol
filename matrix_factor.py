#!/usr/bin/python3

def partial_gradient(critic_rows, movie_cols, example, step):
	#unpacking
	row = critic_rows[example[0]]
	col = movie_cols[example[1]]
	exp_result = example[2]
	#calculation
	calc_result = row*col
	gradient = -2*(exp_result - calc_result)
	gradient_step = step * gradient
	#update
	col = col + row*grad
	row = row + col*grad
	