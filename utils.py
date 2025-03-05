from flask import Blueprint, request, jsonify
import requests
from state import node_state  # Import the centralized state

utilsBp = Blueprint('utils', __name__)


node_address = node_state.node_address

import hashlib

def chord_hash(data):
    """
    Computes the SHA-1 hash of the given input string and returns it as an integer.

    :param data: Input string to be hashed.
    :return: Integer representation of the SHA-1 hash.
    """
    sha1 = hashlib.sha1()  # Create SHA-1 hash object
    sha1.update(data.encode())  # Encode the string and hash it
    return int(sha1.hexdigest(), 16) 

def containsKey(key):
    return key in node_state.storage

def is_responsible(key):
    """ Check if this node is responsible for the key """
    key_hash = chord_hash(key)
    node_hash = chord_hash(node_state.node_address)
    prev_hash = chord_hash(node_state.prev_node)

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
        if action == "insert" or action=='insertLinear':
            response = requests.post(url, json={'value': value})
        elif action == "delete" or action=='deleteLinear':
            response = requests.delete(url)
        elif action == "register":
            url = f"http://{node_state.next_node}/{action}"
            response = requests.post(url, json={'newNode': key})
        elif action == "overlay":
            array = value.get('array', [])
            array.append(node_state.node_address)
            value['array'] = array
            response = requests.post(url, json=value)
        else:  # query
            response = requests.get(url)
        return response.json()
    except requests.exceptions.ConnectionError:
        return {'error': 'Failed to contact next node'}


def backward_request(action, key, value=None):
    """ Forward request to the next node in the ring """
    url = f"http://{node_state.prev_node}/{action}/{key}"
    try:
        if action == "insert":
            response = requests.post(url, json={'value': value})
        elif action == "delete":
            response = requests.delete(url)
        elif action == "register":
            url = f"http://{node_state.next_node}/{action}"
            response = requests.post(url, json={'newNode': key})    
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

@utilsBp.route('/get-next', methods=['GET'])
def get_next():
    return jsonify({'next_node': node_state.next_node if node_state.next_node else node_state.node_address}), 200

@utilsBp.route('/get-prev', methods=['GET'])
def get_prev():
    return jsonify({'prev_node': node_state.prev_node if node_state.prev_node else node_state.node_address}), 200


@utilsBp.route('/getMode', methods=['GET'])
def getMode():
    return jsonify({'mode': node_state.consistencyMode}), 200


@utilsBp.route('/getReplicationFactor', methods=['GET'])
def getReplicationFactor():
    return jsonify({'replicationFactor': node_state.replicationFactor}), 200