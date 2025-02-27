import sys
import socket
import requests
from flask import Flask, request, jsonify
from storage import Storage
import os
import time
import threading

app = Flask(__name__)
storage = Storage()

# Get the local IP address dynamically

def get_local_ip():
    return socket.gethostbyname(socket.gethostname())

# Dynamic node address
node_ip = get_local_ip()
node_port = sys.argv[1] if len(sys.argv) > 1 else "5000"  # Allow port as a cmd argument
node_address = f"{node_ip}:{node_port}"

def get_adress():
    return node_address

# Active nodes list and ring pointers
active_nodes = []
next_node = None
prev_node = None

# Bootstrap Node Logic
is_bootstrap = '--bootstrap' in sys.argv
if is_bootstrap:
    active_nodes.append(node_address)
    print("Starting as bootstrap node")

# Register a new node
@app.route('/register', methods=['POST'])
def register():
    new_node = request.json['node_address']
    if new_node not in active_nodes:
        active_nodes.append(new_node)
        active_nodes.sort()  # Keep nodes sorted to form a consistent ring
        update_ring_pointers()
        broadcast_pointer_update()  # Notify others


    return jsonify({'status': 'registered', 'nodes': active_nodes}), 201

@app.route('/depart', methods=['DELETE'])
def depart():
    
    notify_pointer_update(prev=prev_node,nxt=next_node)
    
    propagate_node_removal(prev_node,next_node, node_address)
    def delayed_exit():
        time.sleep(1)  # Wait a bit to ensure response is sent
        os._exit(0)

    # Start the exit in a new thread, allowing the response to be returned first
    threading.Thread(target=delayed_exit).start()
    
    return jsonify({'status': 'left'}), 200

def propagate_node_removal(end_node, target_node, leaving_node):
    """ Propagate the node removal through the ring """
    
    try:
        url = f"http://{target_node}/propagate-removal"
        requests.post(url, json={'node_address': leaving_node, 'final_node': end_node })
    except requests.exceptions.ConnectionError:
        print(f"Failed to contact {target_node} for propagation.")

@app.route('/propagate-removal', methods=['POST'])
def propagate_removal():
    """ Handle the removal propagation """
    leaving_node = request.json['node_address']
    final_node = request.json['final_node']
    if leaving_node in active_nodes:
        active_nodes.remove(leaving_node)
        print(f"Removed node: {leaving_node}. Active nodes now: {active_nodes}")

    # Continue propagation to the next node
    if final_node == node_address:
        print("Removal completed.")
        return jsonify({'status': 'removal completed'}), 200
    else:
        print(final_node,next_node,leaving_node)
        propagate_node_removal(final_node,next_node, leaving_node)

        return jsonify({'status': 'propagated'}), 200

def notify_pointer_update(prev, nxt):
    """ Notify neighbors to update their pointers """
    # Notify the previous node
    try:
        url = f"http://{prev}/update-next"
        requests.post(url, json={'next_node': nxt})
    except requests.exceptions.ConnectionError:
        print(f"Failed to notify {prev} for next pointer update.")
    
    # Notify the next node
    try:
        url = f"http://{nxt}/update-prev"
        requests.post(url, json={'prev_node': prev})
    except requests.exceptions.ConnectionError:
        print(f"Failed to notify {nxt} for previous pointer update.")

@app.route('/update-next', methods=['POST'])
def update_next():
    """ Update the next pointer """
    global next_node
    next_node = request.json['next_node']
    print(f"Next pointer updated to: {next_node}")
    return jsonify({'status': 'next updated'}), 200

@app.route('/update-prev', methods=['POST'])
def update_prev():
    """ Update the previous pointer """
    global prev_node
    prev_node = request.json['prev_node']
    print(f"Previous pointer updated to: {prev_node}")
    return jsonify({'status': 'prev updated'}), 200

# Update next and previous pointers
def update_ring_pointers():
    global next_node, prev_node
    index = active_nodes.index(node_address)
    next_node = active_nodes[(index + 1) % len(active_nodes)]
    prev_node = active_nodes[(index - 1) % len(active_nodes)]
    print(f"Updated ring pointers: Prev -> {prev_node}, Next -> {next_node}")

@app.route('/nodes', methods=['GET'])
def get_nodes():
    return jsonify({'nodes': active_nodes})

@app.route('/insert/<key>', methods=['POST'])
def insert(key):
    value = request.json['value']
    # Ring routing: Check if this node is responsible
    if is_responsible(key):
        storage.insert(key, value)  
        return jsonify({'status': 'success', 'node': 'self'}), 201
    else:
        # Forward to the next node
        return forward_request('insert', key, value)

@app.route('/query/<key>', methods=['GET'])
def query(key):
    if is_responsible(key):
        value = storage.query(key)
        return jsonify({'value': value, 'node': 'self'}), 200
    else:
        return forward_request('query', key)

@app.route('/delete/<key>', methods=['DELETE'])
def delete(key):
    if is_responsible(key):
        storage.delete(key)
        return jsonify({'status': 'deleted', 'node': 'self'}), 200
    else:
        return forward_request('delete', key)
    
def is_responsible(key):
    """ Check if this node is responsible for the key """
    key_hash = hash(key)
    node_hash = hash(node_address)
    prev_hash = hash(prev_node)

    # Responsible if the key is in the (prev_node, current_node] range
    if prev_hash < node_hash:
        return prev_hash < key_hash <= node_hash
    else:
        # Handle wrap-around case in the ring
        return prev_hash < key_hash or key_hash <= node_hash

def forward_request(action, key, value=None):
    """ Forward request to the next node in the ring """
    url = f"http://{next_node}/{action}/{key}"
    try:
        if action == "insert":
            response = requests.post(url, json={'value': value})
        elif action == "delete":
            response = requests.delete(url)
        else:  # query
            response = requests.get(url)
        return response.json()
    except requests.exceptions.ConnectionError:
        return jsonify({'error': 'Failed to contact next node'}), 500

def broadcast_pointer_update():
    """ Notify all nodes to update their ring pointers """
    for node in active_nodes:
        if node != node_address:  # Don't notify self
            try:
                url = f"http://{node}/update-pointers"
                requests.post(url, json={'nodes': active_nodes})
            except requests.exceptions.ConnectionError:
                print(f"Failed to notify {node} for pointer update.")

@app.route('/update-pointers', methods=['POST'])
def receive_pointer_update():
    global active_nodes
    active_nodes = request.json['nodes']
    update_ring_pointers()
    return jsonify({'status': 'pointers updated'}), 200


if __name__ == '__main__':
    # Bootstrap Node Logic
    if is_bootstrap:
        print("Bootstrap node managing active nodes.")
    else:
        # Non-bootstrap nodes register with the bootstrap node
        bootstrap_url = "http://localhost:5000/register"
        try:
            response = requests.post(bootstrap_url, json={'node_address': node_address})
            nodes = response.json().get('nodes', [])
            active_nodes.extend(nodes)
            active_nodes.sort()
            update_ring_pointers()
            broadcast_pointer_update()  # Notify others

            print(f"Joined network. Active nodes: {active_nodes}")
        except requests.exceptions.ConnectionError:
            print("Failed to contact the bootstrap node.")

    app.run(host='0.0.0.0', port=int(node_port))

