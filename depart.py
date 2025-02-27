
from flask import Blueprint, request, jsonify
import requests
import time
import threading
import os
from state import node_state
departBp = Blueprint('depart', __name__)


prev_node=node_state.prev_node
next_node=node_state.next_node
node_address=node_state.node_address
# @departBp.record_once
# def setup(setup_state):
#     global prev_node, next_node, node_address ,active_nodes
#     prev_node = setup_state.options['prev_node']
#     next_node = setup_state.options['next_node']
#     node_address = setup_state.options['node_address']
#     active_nodes = setup_state.options['active_nodes']

@departBp.route('/depart', methods=['DELETE'])
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

@departBp.route('/propagate-removal', methods=['POST'])
def propagate_removal():
    """ Handle the removal propagation """
    leaving_node = request.json['node_address']
    final_node = request.json['final_node']
    # if leaving_node in active_nodes:
    #     active_nodes.remove(leaving_node)
    #     print(f"Removed node: {leaving_node}. Active nodes now: {active_nodes}")

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

