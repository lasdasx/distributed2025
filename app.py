from flask import Flask
from storage import Storage
import sys
import socket
from utils import utilsBp
from operations import operationsBp
from depart import departBp
import requests
from registerEventual import registerEventualBp
from registerLinear import registerLinearBp
from overlay import overlayBp
from eventual import eventualBp
import time
from state import node_state
import threading
import os
from utils import chord_hash
app=Flask(__name__)
storage = Storage()

# Get the local IP address dynamically

def get_local_ip():
    return socket.gethostbyname(socket.gethostname())

# Dynamic node address
node_ip = get_local_ip()
print(node_ip)
node_port = sys.argv[sys.argv.index("--port") + 1] if "--port" in sys.argv else "5000"  # Allow port as a cmd argument
node_address = f"{node_ip}:{node_port}"
node_state.node_address = node_address
node_state.node_address_hash = chord_hash(node_state.node_address)

active_nodes = []
next_node = None
prev_node = None


app.register_blueprint(registerLinearBp)
app.register_blueprint(registerEventualBp)

app.register_blueprint(overlayBp,)
app.register_blueprint(departBp)
app.register_blueprint(operationsBp)
app.register_blueprint(utilsBp)
app.register_blueprint(eventualBp)

# Bootstrap Node Logic
is_bootstrap = '--bootstrap' in sys.argv


# Function to register with bootstrap node
def register_with_bootstrap():
    if not is_bootstrap:
        bootstrapIp = "10.0.42.248" if not "--local" in sys.argv else "127.0.0.1" #first vm bootstrap
        # Non-bootstrap nodes register with the bootstrap node
        bootstrap_url = f"http://{bootstrapIp}:5000"
        while True:
            try:
                print(f"Trying to join the network via {bootstrap_url}")
                node_state.consistencyMode=requests.get(f"{bootstrap_url}/getMode").json()['mode']
                node_state.replicationFactor=requests.get(f"{bootstrap_url}/getReplicationFactor").json()['replicationFactor']


                response = requests.post(f"{bootstrap_url}/registerLinear" if node_state.consistencyMode == "linear" else f"{bootstrap_url}/registerEventual", json={'newNode': node_state.node_address})
                if response.status_code == 201:
                    print("Successfully registered with the bootstrap node.")
                    break
                else:
                    print(f"Failed to register. Status code: {response.status_code}")
            
            except requests.exceptions.ConnectionError:
                print("Failed to contact the bootstrap node. Retrying in 5 seconds...")
            time.sleep(5)

if __name__ == '__main__':
    # Run Flask app
    node_state.node_address = node_address
    node_state.node_address_hash = chord_hash(node_state.node_address)
    threading.Thread(target=lambda: app.run(host='0.0.0.0', port=int(node_port)), daemon=True).start()

    # Wait a moment for the server to start
    time.sleep(2)

    # Start registration in a new thread
    if not is_bootstrap:
        threading.Thread(target=register_with_bootstrap, daemon=True).start()
    else:
        node_state.next_node = node_address
        node_state.prev_node = node_address
        node_state.replicationFactor = 1 if not "-rf" in sys.argv else int(sys.argv[sys.argv.index("-rf") + 1])
        node_state.consistencyMode = "eventual" if "-e" in sys.argv else "linear"
    # Keep main thread alive
    while True:
        time.sleep(1)

