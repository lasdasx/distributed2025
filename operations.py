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

    if node_state.consistencyMode == "eventual":
        ## return insertEventual(key)
        value = request.json['value']
        # Ring routing: Check if this node is responsible
        if is_responsible(key):
            node_state.storage.insert(key, value)
            node_state.storage.copyIndexes[key] = 1
            print(f"[Insert] Key {key} inserted at {node_state.node_address}. Starting replication.")  
            threading.Thread(target=replicate_to_successor, args=(key, value, 1)).start()

            return jsonify({'status': 'success', 'node': node_state.node_address}), 201
        else:
            # Forward to the next node
            print(f"[Forward] Key {key} not stored here. Forwarding request.")
            return forward_request('insert', key, value)
    else:
        return insertLinear(key)
    
@operationsBp.route('/insertLinear/<key>', methods=['POST'])
def insertLinear(key):
    value = request.json['value']
    
    if is_responsible(key):
        currentCopy=1
        # node_state.storage.insert(key, value)  

        response=requests.post(f"http://{node_state.node_address}/addReplica", json={'key': key,'value': value, 'currentCopy':currentCopy})
        print(node_state.storage.copyIndexes)
        return response.json()
    else:
        return forward_request('insertLinear', key, value)

@operationsBp.route('/addReplica', methods=['POST'])
def addReplica():
    key=request.json['key']
    value=request.json['value']
    currentCopy=request.json['currentCopy']

    print(f"key: {key}, value: {value}, currentCopy: {currentCopy}")
    if key not in list(node_state.storage.copyIndexes):
        node_state.storage.insert(key, value)
        node_state.storage.copyIndexes[key] = currentCopy
        print(f"key: {key}, value: {value}, currentCopy: {currentCopy}")

    currentCopy+=1
    print(node_state.replicationFactor)
    if currentCopy>node_state.replicationFactor:
        print(f"key: {key}, value: {value}, currentCopy: {currentCopy}")
        return jsonify({'status': 'success', 'message': f"insertion of key {key} reached node {node_state.node_address}"}), 201
    else:
        response=requests.post(f"http://{node_state.next_node}/addReplica", json={'key': key,'value': value, 'currentCopy':currentCopy})
        print(f"key: {key}, value: {value}, currentCopy: {currentCopy}")
        return response.json()
  
@operationsBp.route('/deleteLinear/<key>', methods=['DELETE'])
def deleteLinear(key):
    if is_responsible(key):
        currentCopy=1
        response=requests.delete(f"http://{node_state.node_address}/removeReplica", json={'key': key, 'currentCopy':currentCopy})
        return response.json()
    else:
        return forward_request('deleteLinear', key)
    
@operationsBp.route('/removeReplica', methods=['DELETE'])
def removeReplica():
    key=request.json['key']
    currentCopy=request.json['currentCopy']

    node_state.storage.delete(key)
    currentCopy+=1
    if currentCopy>node_state.replicationFactor:
        return jsonify({'status': 'success', 'message': f"removal of key {key} reached node {node_state.node_address}"}), 201
    else:
        response=requests.delete(f"http://{node_state.next_node}/removeReplica", json={'key': key, 'currentCopy':currentCopy})
        return response.json()
  


@operationsBp.route('/queryLinear/<key>', methods=['GET'])
def queryLinear(key):
    if key=="*":
        results = {}
        results[node_state.node_address] = storage.data #( , copyIndexes)
        next_node=node_state.next_node
        while next_node!= node_state.node_address:
            response = requests.get(f"http://{next_node}/getData")
            data = response.json()['data']
            results[next_node] = data
            next_node = response.json()['next_node']
            
        return jsonify(results), 200

    if is_responsible(key) :
        response = requests.post(f"http://{node_state.node_address}/queryLast", json={'key': key, 'currentCopy':1})
        return response.json()
    else:
        return forward_request('queryLinear', key)
    
@operationsBp.route('/queryLast', methods=['POST'])
def queryLast():
    key=request.json['key']
    currentCopy=request.json['currentCopy']
    if currentCopy==node_state.replicationFactor:
        return jsonify({'status':"success", "message":f"Returned from node {node_state.node_address}", "value":storage.query(key= key)}) 
    else:
        return requests.post(f"http://{node_state.next_node}/queryLast", json={"currentCopy":currentCopy+1, "key":key}).json()


@operationsBp.route('/query/<key>', methods=['GET'])
def query(key):
   
    if node_state.consistencyMode == "eventual":
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

        elif is_responsible(key) or key in storage.data:
            value = storage.query(key)
            return jsonify({'value': value, 'node': node_state.node_address}), 200
        else:
            return forward_request('query', key)
        
    else:
        return queryLinear(key)

    
@operationsBp.route('/getData', methods=['GET'])
def getData():
    return jsonify({"data":storage.data, "next_node":node_state.next_node}), 200 #(, queryIndexes)

@operationsBp.route('/delete/<key>', methods=['DELETE'])
def delete(key):
    # if is_responsible(key):
    #     storage.delete(key)
    #     return jsonify({'status': 'deleted', 'node': node_state.node_address}), 200
    # else:
    #     return forward_request('delete', key)
    if node_state.consistencyMode == "eventual":
        ## return insertEventual(key)
        if is_responsible(key):
            storage.delete(key)
            threading.Thread(target=propagate_delete_to_successor, args=(key,)).start()
            return jsonify({'status': 'deleted', 'node': node_state.node_address}), 200
        else:
            return forward_request('delete', key)
    else:
        return deleteLinear(key)
