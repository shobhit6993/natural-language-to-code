Universe=vanilla
Getenv=True

Initialdir = /scratch/cluster/shobhit/natural-language-to-code/experiments/rnn/trigger-func-2-$(Process)
#Output = out.$(cluster)
Error = err.$(cluster)
Log = log.$(cluster)

+GPUJob=true
Requirements = TARGET.GPUSlot
# Requirements = Cuda8 && TARGET.GPUSlot && CUDAGlobalMemoryMb >= 6144
#(TARGET.Machine != "eldar-2.cs.utexas.edu")
#target.machine=="eldar-16.cs.utexas.edu"
#target.machine=='eldar-10.cs.utexas.edu' && target.machine=="eldar-3.cs.utexas.edu"
#CUDAGlobalMemoryMb >= 6144
#&& target.machine=="eldar-3.cs.utexas.edu"
request_GPUs=1

Notification=Always
notify_user = shobhit@utexas.edu

+Group="GRAD"
+Project="AI_ROBOTICS"
+ProjectDescription="Natural language to code."

Environment=PATH=/lusr/opt/condor/bin/:/u/shobhit/archive/packages/anaconda-2/bin:$PATH
Environment=PYTHONPATH=/u/shobhit/archive/packages/anaconda-2/bin:$PYTHONPATH

Executable=trigger-func-train.sh
Arguments=trigger-func-2-$(Process)

Queue 1
