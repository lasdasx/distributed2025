from flask import Blueprint, request, jsonify
import requests
from state import node_state
from utils import forward_request,backward_request

overlayBp = Blueprint('overlay', __name__)


@overlayBp.route('/overlay/<key>', methods=['POST'])
def overlay(key):
    print(f"Got request at node: {node_state.node_address}")
    array = request.json.get('array', [])

    # Normalize key and node address for consistency
    normalized_key = key.replace('http://', '').replace('https://', '')
    normalized_node = node_state.node_address.replace('http://', '').replace('https://', '')

    # If the array is empty, this is the starting node
    if not array:
        array.append(normalized_node)

    # Check if current node is already in array, if not, add it
    if normalized_node not in array:
        array.append(normalized_node)

    # Filter out None values and remove duplicates while preserving order
    array = [addr for addr in array if addr]
    array = list(dict.fromkeys(array))
    print(f"Array so far: {array}")

    # If back at the origin node and we have visited at least one other node, return the result
    if normalized_node == normalized_key and len(array) > 1:
        print("Back at the origin node. Returning collected nodes.")
        return jsonify({'nodes': array}), 200

    # If there's only one node in the network, return immediately to avoid infinite loop
    if len(array) == 1 and node_state.next_node == normalized_node:
        print("Single-node network detected. Returning the only node.")
        return jsonify({'nodes': array}), 200

    # Otherwise, forward the request to the next node
    print(f"Forwarding to next node: {node_state.next_node}")
    forward_request('overlay', key, {'array': array})
    return jsonify({'status': 'forwarded'}), 202

