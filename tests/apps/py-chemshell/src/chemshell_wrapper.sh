#!/bin/bash

# Function to check job status
check_job_status() {
    squeue -j "$jobid" -h 2>/dev/null | wc -l
}

chemsh --submit --jobname pycs-nwchem $CHEMSHELL_SUBMIT_OPTIONS $TEST_CASE 2>&1 | tee submit.log

jobid=$( tail  -n 10 submit.log | sed -nE "s:.*job ([0-9]+).*:\1:p" )

# Wait until job is no longer in the queue
while [ "$(check_job_status)" -gt 0 ]; do
    sleep 5  # Check every 10 seconds
done

echo "Job $jobid has completed"