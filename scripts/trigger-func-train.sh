#!/bin/bash
export PATH=/u/shobhit/archive/packages/anaconda-2/bin:$PATH
export CUDA_HOME=/u/shobhit/archive/packages:$CUDA_HOME
export LD_LIBRARY_PATH=/u/shobhit/archive/packages/lib64:$LD_LIBRARY_PATH

cd /scratch/cluster/shobhit/natural-language-to-code

python ./parser/train.py --experiment-name ${1} --model TriggerFunctionModel --use-train-set --use-triggers-api --use-synthetic-recipes --use-names-descriptions --log-level INFO
