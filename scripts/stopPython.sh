#!/bin/bash

# List of VMs
VMS=("team_35-vm1" "team_35-vm2" "team_35-vm3" "team_35-vm4" "team_35-vm5")

# Run the command on each VM in parallel
for VM in "${VMS[@]}"; do
    ssh "$VM" "sudo killall python3" &
done

# Wait for all background processes to finish
wait

echo "All python3 processes killed on all VMs."

