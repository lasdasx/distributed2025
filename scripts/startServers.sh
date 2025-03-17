#!/bin/bash
# Run each command in a new terminal tab with a 3-second delay

#gnome-terminal --tab -- bash -c "python3 app.py --bootstrap --port 5000 -rf 1; exec bash"

wt.exe new-tab --title "VM1-5000" -- wsl -e bash -c "ssh team_35-vm1 'cd distributed2025 && python3 app.py --bootstrap --port 5000 -rf 3'" ; sleep 6
wt.exe new-tab --title "VM1-5001" -- wsl -e bash -c "ssh team_35-vm1 'cd distributed2025 && python3 app.py --port 5001'" ; sleep 6
wt.exe new-tab --title "VM2-5000" -- wsl -e bash -c "ssh team_35-vm2 'cd distributed2025 && python3 app.py --port 5000'" ; sleep 6
wt.exe new-tab --title "VM2-5001" -- wsl -e bash -c "ssh team_35-vm2 'cd distributed2025 && python3 app.py --port 5001'" ; sleep 6
wt.exe new-tab --title "VM3-5000" -- wsl -e bash -c "ssh team_35-vm3 'cd distributed2025 && python3 app.py --port 5000'" ; sleep 6
wt.exe new-tab --title "VM3-5001" -- wsl -e bash -c "ssh team_35-vm3 'cd distributed2025 && python3 app.py --port 5001'" ; sleep 6
wt.exe new-tab --title "VM4-5000" -- wsl -e bash -c "ssh team_35-vm4 'cd distributed2025 && python3 app.py --port 5000'" ; sleep 6
wt.exe new-tab --title "VM4-5001" -- wsl -e bash -c "ssh team_35-vm4 'cd distributed2025 && python3 app.py --port 5001'" ; sleep 6
wt.exe new-tab --title "VM5-5000" -- wsl -e bash -c "ssh team_35-vm5 'cd distributed2025 && python3 app.py --port 5000'" ; sleep 6
wt.exe new-tab --title "VM5-5001" -- wsl -e bash -c "ssh team_35-vm5 'cd distributed2025 && python3 app.py --port 5001'" ; sleep 6

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
