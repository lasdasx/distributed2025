#!/bin/bash
# Run each command in a new terminal tab with a 3-second delay

gnome-terminal --tab -- bash -c "python3 cli.py join --bootstrap --port 5000 -rf 1 --local ; exec bash"
sleep 3

gnome-terminal --tab -- bash -c "python3 cli.py join --port 5001 --local; exec bash"
sleep 3

gnome-terminal --tab -- bash -c "python3 cli.py join --port 5002 --local; exec bash"
sleep 3

gnome-terminal --tab -- bash -c "python3 cli.py join --port 5003 --local; exec bash"
sleep 3

gnome-terminal --tab -- bash -c "python3 cli.py join --port 5004 --local; exec bash"
sleep 3

gnome-terminal --tab -- bash -c "python3 cli.py join --port 5005 --local; exec bash"
sleep 3

gnome-terminal --tab -- bash -c "python3 cli.py join --port 5006 --local; exec bash"
sleep 3

gnome-terminal --tab -- bash -c "python3 cli.py join --port 5007 --local; exec bash"
sleep 3

gnome-terminal --tab -- bash -c "python3 cli.py join --port 5008 --local; exec bash"
sleep 3

gnome-terminal --tab -- bash -c "python3 cli.py join --port 5009 --local; exec bash"
sleep 3

echo "All commands finished!"

### local

