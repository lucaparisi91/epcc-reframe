#!/bin/bash

# Function to check job status
check_job_status() {
    squeue -j "$jobid" -h 2>/dev/null | wc -l
}

chemsh --submit --jobname $NAME $CHEMSHELL_SUBMIT_OPTIONS $TEST_CASE 2>&1 | tee submit.log

jobid=$( tail  -n 10 submit.log | sed -nE "s:.*job ([0-9]+).*:\1:p" ) # Get the id of the slurm job submitted by chemshell

# Wait until job is no longer in the queue
while [ "$(check_job_status)" -gt 0 ]; do
    sleep 5  # Check every 5 seconds
done

echo "Job $jobid has completed"