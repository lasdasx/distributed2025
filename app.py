from flask import Flask
from storage import Storage
import sys
import socket
from utils import utilsBp
from operations import operationsBp
from depart import departBp
import requests
from register import registerBp
from overlay import overlayBp
import time
from state import node_state
import threading
app=Flask(__name__)
storage = Storage()

# Get the local IP address dynamically

def get_local_ip():
    return socket.gethostbyname(socket.gethostname())

# Dynamic node address
node_ip = get_local_ip()
node_port = sys.argv[1] if len(sys.argv) > 1 else "5000"  # Allow port as a cmd argument
node_address = f"{node_ip}:{node_port}"
node_state.node_address = node_address

active_nodes = []
next_node = None
prev_node = None


app.register_blueprint(registerBp)
app.register_blueprint(overlayBp,)
app.register_blueprint(departBp)
app.register_blueprint(operationsBp)
app.register_blueprint(utilsBp)

# Bootstrap Node Logic
is_bootstrap = '--bootstrap' in sys.argv


# Function to register with bootstrap node
def register_with_bootstrap():
    if not is_bootstrap:
        # Non-bootstrap nodes register with the bootstrap node
        bootstrap_url = "http://localhost:5000/register"
        while True:
            try:
                print(f"Trying to join the network via {bootstrap_url}")
                response = requests.post(bootstrap_url, json={'newNode': node_address})
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

    threading.Thread(target=lambda: app.run(host='0.0.0.0', port=int(node_port)), daemon=True).start()

    # Wait a moment for the server to start
    time.sleep(2)

    # Start registration in a new thread
    if not is_bootstrap:
        threading.Thread(target=register_with_bootstrap, daemon=True).start()

    # Keep main thread alive
    while True:
        time.sleep(1)

