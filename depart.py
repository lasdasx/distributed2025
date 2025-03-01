
from flask import Blueprint, request, jsonify
import requests
import time
import threading
import os
from state import node_state
departBp = Blueprint('depart', __name__)


# @departBp.record_once
# def setup(setup_state):
#     global prev_node, next_node, node_address ,active_nodes
#     prev_node = setup_state.options['prev_node']
#     next_node = setup_state.options['next_node']
#     node_address = setup_state.options['node_address']
#     active_nodes = setup_state.options['active_nodes']

@departBp.route('/depart', methods=['DELETE'])
def depart():
    if node_state.prev_node == node_state.node_address and node_state.next_node == node_state.node_address:
        # Case 1: This is the only node in the ring
        node_state.next_node = None
        node_state.prev_node = None
        threading.Timer(2, lambda: os._exit(0)).start()

        return jsonify({'status': 'departed', 'message': 'Node was the only one in the ring'}), 200

    # Inform the previous and next nodes to update their pointers
    requests.post(f"http://{node_state.prev_node}/update-next", json={"next_node": node_state.next_node})
    requests.post(f"http://{node_state.next_node}/update-prev", json={"prev_node": node_state.prev_node})

    # Clear the node's state to indicate departure
    departing_node = node_state.node_address
    
    node_state.next_node = None
    node_state.prev_node = None 
    threading.Timer(2, lambda: os._exit(0)).start()

    return jsonify({'status': 'departed', 'node': departing_node}), 200

