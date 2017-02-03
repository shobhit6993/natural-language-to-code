#!/usr/bin/env bash

cd /scratch/cluster/shobhit/natural-language-to-code/experiments/rnn
dir_name=trigger-func-2
for ((i = 0 ; i < 1 ; i++ ))
do
	mkdir $dir_name-$i
	mkdir $dir_name-$i/model-checkpoints
	mkdir $dir_name-$i/plots
done
