from flask import Blueprint, request, jsonify
import requests
from utils import is_responsible,forward_request
from state import node_state 
operationsBp = Blueprint('operations', __name__)
from utils import chord_hash
import threading
from eventual import replicate_to_successor, propagate_delete_to_successor

active_nodes = []
next_node = node_state.next_node
prev_node = node_state.prev_node
node_address = node_state.node_address
storage=node_state.storage

mode=node_state.consistencyMode
replicationFactor=node_state.replicationFactor

@operationsBp.route('/insert/<key>', methods=['POST'])
def insert(key):

    value = request.json['value']
    # Ring routing: Check if this node is responsible
    if is_responsible(key):
        node_state.storage.insert(key, value) 
        
        if node_state.consistencyMode == "eventual":
            threading.Thread(target=replicate_to_successor, args=(key, value)).start()
 
        return jsonify({'status': 'success', 'node': node_state.node_address}), 201
    else:
        # Forward to the next node
        return forward_request('insert', key, value)

@operationsBp.route('/query/<key>', methods=['GET'])
def query(key):
    if key=="*":
        results = {}
        results[node_state.node_address] = storage.data
        next_node=node_state.next_node
        while next_node!= node_state.node_address:
            response = requests.get(f"http://{next_node}/getData")
            data = response.json()['data']
            results[next_node] = data
            next_node = response.json()['next_node']
            
        return jsonify(results), 200

    if is_responsible(key):
        value = storage.query(key)
        return jsonify({'value': value, 'node': node_state.node_address}), 200
    else:
        return forward_request('query', key)
    
@operationsBp.route('/getData', methods=['GET'])
def getData():
    return jsonify({"data":storage.data, "next_node":node_state.next_node}), 200

@operationsBp.route('/delete/<key>', methods=['DELETE'])
def delete(key):
    if is_responsible(key):
        storage.delete(key)
        
        if node_state.consistencyMode == "eventual":
            threading.Thread(target=propagate_delete_to_successor, args=(key,)).start()
            
        return jsonify({'status': 'deleted', 'node': node_state.node_address}), 200
    else:
        return forward_request('delete', key)
    
