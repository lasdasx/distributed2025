from flask import Blueprint, request, jsonify
import requests
from utils import is_responsible,forward_request
from state import node_state 
operationsBp = Blueprint('operations', __name__)

active_nodes = []
next_node = node_state.next_node
prev_node = node_state.prev_node
node_address = node_state.node_address

# @operationsBp.record_once
# def setup(setup_state):
#     global prev_node, next_node, node_address ,active_nodes,storage
#     prev_node = setup_state.options['prev_node']
#     next_node = setup_state.options['next_node']
#     node_address = setup_state.options['node_address']
#     active_nodes = setup_state.options['active_nodes']
#     storage =setup_state.options['storage']

@operationsBp.route('/nodes', methods=['GET'])
def get_nodes():
    return jsonify({'nodes': active_nodes})

@operationsBp.route('/insert/<key>', methods=['POST'])
def insert(key):
    value = request.json['value']
    # Ring routing: Check if this node is responsible
    if is_responsible(key):
        storage.insert(key, value)  
        return jsonify({'status': 'success', 'node': 'self'}), 201
    else:
        # Forward to the next node
        return forward_request('insert', key, value)

@operationsBp.route('/query/<key>', methods=['GET'])
def query(key):
    if is_responsible(key):
        value = storage.query(key)
        return jsonify({'value': value, 'node': 'self'}), 200
    else:
        return forward_request('query', key)

@operationsBp.route('/delete/<key>', methods=['DELETE'])
def delete(key):
    if is_responsible(key):
        storage.delete(key)
        return jsonify({'status': 'deleted', 'node': 'self'}), 200
    else:
        return forward_request('delete', key)
    
