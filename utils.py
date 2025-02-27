from flask import Blueprint, request, jsonify
import requests
from state import node_state  # Import the centralized state

utilsBp = Blueprint('utils', __name__)


node_address = node_state.node_address

def is_responsible(key):
    """ Check if this node is responsible for the key """
    key_hash = hash(key)
    node_hash = hash(node_address)
    prev_hash = hash(node_state.prev_node)

    # Responsible if the key is in the (prev_node, current_node] range
    if prev_hash < node_hash:
        return prev_hash < key_hash <= node_hash
    else:
        # Handle wrap-around case in the ring
        return prev_hash < key_hash or key_hash <= node_hash

def forward_request(action, key, value=None):
    """ Forward request to the next node in the ring """
    url = f"http://{node_state.next_node}/{action}/{key}"
    try:
        if action == "insert":
            response = requests.post(url, json={'value': value})
        elif action == "delete":
            response = requests.delete(url)
        elif action == "join":
            response = requests.post(url)
        elif action == "overlay":
            array = value.get('array', [])
            array.append(node_state.node_address)
            value['array'] = array
            response = requests.post(url, json=value)
        else:  # query
            response = requests.get(url)
        return response.json()
    except requests.exceptions.ConnectionError:
        return jsonify({'error': 'Failed to contact next node'}), 500


def backward_request(action, key, value=None):
    """ Forward request to the next node in the ring """
    url = f"http://{node_state.prev_node}/{action}/{key}"
    try:
        if action == "insert":
            response = requests.post(url, json={'value': value})
        elif action == "delete":
            response = requests.delete(url)
        elif action == "join":
            response = requests.post(url)
        elif action=="overlay":
            response = requests.post(url, json={'array': value})
        else:  # query
            response = requests.get(url)
        return response.json()
    except requests.exceptions.ConnectionError:
        return jsonify({'error': 'Failed to contact next node'}), 500



@utilsBp.route('/update-next', methods=['POST'])
def update_next():
    """ Update the next pointer """
    # global next_node
    node_state.next_node = request.json['next_node']
    print(f"Next pointer updated to: {node_state.next_node}")
    return jsonify({'status': 'next updated'}), 200

@utilsBp.route('/update-prev', methods=['POST'])
def update_prev():
    """ Update the previous pointer """
    # global prev_node
    node_state.prev_node = request.json['prev_node']
    print(f"Previous pointer updated to: {node_state.prev_node}")
    return jsonify({'status': 'prev updated'}), 200
