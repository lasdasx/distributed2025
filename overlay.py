from flask import Blueprint, request, jsonify
import requests
from state import node_state
from utils import forward_request,backward_request

overlayBp = Blueprint('overlay', __name__)

# @overlayBp.record_once
# def setup(setup_state):
#     global prev_node, next_node, node_address , active_nodes
#     prev_node = setup_state.options['prev_node']
#     next_node = setup_state.options['next_node']
#     active_nodes = setup_state.options['active_nodes']
#     node_address = setup_state.options['node_address']

@overlayBp.route('/overlay/<key>', methods=['POST'])
def overlay(key):
    if node_state.next_node== None or node_state.prev_node == None:
        print("AAAA")
        return jsonify({'nodes': [node_state.node_address]}), 200
    if 'array' not in request.json:
        array = []
    else:
        array = request.json['array']

        
    if node_state.node_address != key:
        array.append(node_state.node_address)
        forward_request('overlay', key, array)
    else:
        if len(array) == 0:
            array.append(node_state.node_address)
            forward_request('overlay', key, array)
        else:
            return jsonify({'nodes': array}), 200

