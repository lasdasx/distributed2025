#!/bin/bash
# Run each command in a new terminal tab with a 3-second delay

#gnome-terminal --tab -- bash -c "python3 app.py --bootstrap --port 5000 -rf 1; exec bash"
ssh team_35-vm1 "cd distributed2025 ; python3 cli.py join --bootstrap --port 5000 -rf 1" 
sleep 3
ssh team_35-vm1 "cd distributed2025 ; python3 cli.py join --port 5001"
sleep 3
ssh team_35-vm2 "cd distributed2025 ; python3 cli.py join --port 5000"
sleep 3
ssh team_35-vm2 "cd distributed2025 ; python3 cli.py join --port 5001"
sleep 3
ssh team_35-vm3 "cd distributed2025 ; python3 cli.py join --port 5000"
sleep 3
ssh team_35-vm3 "cd distributed2025 ; python3 cli.py join --port 5001"
sleep 3
ssh team_35-vm4 "cd distributed2025 ; python3 cli.py join --port 5000"
sleep 3
ssh team_35-vm4 "cd distributed2025 ; python3 cli.py join --port 5001"
sleep 3
ssh team_35-vm5 "cd distributed2025 ; python3 cli.py join --port 5000"
sleep 3
ssh team_35-vm5 "cd distributed2025 ; python3 cli.py join --port 5001"
sleep 3

# gnome-terminal --tab -- bash -c "python3 app.py --port 5001; exec bash"
# sleep 3

# gnome-terminal --tab -- bash -c "python3 app.py --port 5002 --local; exec bash"
# sleep 3

# gnome-terminal --tab -- bash -c "python3 app.py --port 5003 --local; exec bash"
# sleep 3

# gnome-terminal --tab -- bash -c "python3 app.py --port 5004 --local; exec bash"
# sleep 3

# gnome-terminal --tab -- bash -c "python3 app.py --port 5005 --local; exec bash"
# sleep 3

# gnome-terminal --tab -- bash -c "python3 app.py --port 5006 --local; exec bash"
# sleep 3

# gnome-terminal --tab -- bash -c "python3 app.py --port 5007 --local; exec bash"
# sleep 3

# gnome-terminal --tab -- bash -c "python3 app.py --port 5008 --local; exec bash"
# sleep 3

# gnome-terminal --tab -- bash -c "python3 app.py --port 5009 --local; exec bash"
# sleep 3

echo "All commands finished!"
