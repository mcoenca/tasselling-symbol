#!/bin/bash
dimension=( 1 10 25 40)
lambda=( 0 10 100 1000 )
iterations=40

for dim in "${dimension[@]}"; do
	for i in 0 1 2 3; do
		lam=${lambda[i]}
		cmd="./rotten_factor_tests.py -i $iterations -d $dim -l $lam -s 0.002 -f factor_results"
		$cmd &
		pid[i]=$!
	done
	for i in 0 1 2 3; do
		echo "waiting for ${pid[i]}"
		wait ${pid[i]}
	done 
done
