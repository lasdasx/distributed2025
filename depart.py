
from flask import Blueprint, request, jsonify
import requests
import time
import threading
import os
from state import node_state
departBp = Blueprint('depart', __name__)


@departBp.route('/depart', methods=['DELETE'])
def depart():
    if node_state.consistencyMode == "eventual":
        return departEventual()
    else:
        return departLinear()


@departBp.route('/departEventual', methods=['DELETE'])
def departEventual():
    if node_state.prev_node == node_state.node_address and node_state.next_node == node_state.node_address:
        # Case 1: This is the only node in the ring
        node_state.next_node = None
        node_state.prev_node = None
        threading.Timer(2, lambda: os._exit(0)).start()

        return jsonify({'status': 'departed', 'message': 'Node was the only one in the ring'}), 200



    # Case 2: This is not the only node in the ring
    print("AAAAAA")
    keys = [key for key in node_state.storage.copyIndexes]
    print(keys)
    values = node_state.storage.data
    keyCopies = node_state.storage.copyIndexes
    visited=[node_state.node_address]
    print("BBBBBB")
    #asynchronous execution
    threading.Thread(
        target=requests.post,
        args=(f"http://{node_state.next_node}/updateNext",),
        kwargs={'json': {'keys': keys, 'values': values, 'keyCopies': keyCopies, 'visited': visited}, 'timeout': 2},
        daemon=True
    ).start()



    print("CCCCCCCC")
    # Inform the previous and next nodes to update their pointers
    requests.post(f"http://{node_state.prev_node}/update-next", json={"next_node": node_state.next_node})
    requests.post(f"http://{node_state.next_node}/update-prev", json={"prev_node": node_state.prev_node})

    print("DDDDDDDD")
    # Clear the node's state to indicate departure
    departing_node = node_state.node_address
    
    node_state.next_node = None
    node_state.prev_node = None 
    threading.Timer(2, lambda: os._exit(0)).start()

    return jsonify({'status': 'departed', 'node': departing_node}), 200
    

@departBp.route('/departLinear', methods=['DELETE'])
def departLinear():
    if node_state.prev_node == node_state.node_address and node_state.next_node == node_state.node_address:
        # Case 1: This is the only node in the ring
        node_state.next_node = None
        node_state.prev_node = None
        threading.Timer(2, lambda: os._exit(0)).start()

        return jsonify({'status': 'departed', 'message': 'Node was the only one in the ring'}), 200



    # Case 2: This is not the only node in the ring
    print("AAAAAA")
    keys = [key for key in node_state.storage.copyIndexes]
    print(keys)
    values = node_state.storage.data
    keyCopies = node_state.storage.copyIndexes
    visited=[node_state.node_address]
    print("BBBBBB")
    response = requests.post(f"http://{node_state.next_node}/updateNext", json={ 'keys':keys, 'values':values, 'keyCopies':keyCopies, 'visited':visited})



    print("CCCCCCCC")
    # Inform the previous and next nodes to update their pointers
    requests.post(f"http://{node_state.prev_node}/update-next", json={"next_node": node_state.next_node})
    requests.post(f"http://{node_state.next_node}/update-prev", json={"prev_node": node_state.prev_node})

    print("DDDDDDDD")
    # Clear the node's state to indicate departure
    departing_node = node_state.node_address
    
    node_state.next_node = None
    node_state.prev_node = None 
    threading.Timer(2, lambda: os._exit(0)).start()

    return jsonify({'status': 'departed', 'node': departing_node}), 200

@departBp.route('/updateNext', methods=['POST'])
def updateNext():
    print("updateNext")
    visited=request.json['visited']
    if node_state.node_address not in visited:
        print("updateNext inside if")
        keys= request.json['keys']
        values= request.json['values']
        keyCopies = request.json['keyCopies']
        print("before for")
        for key in keys[:]:
            print(key)
            print(node_state.replicationFactor)
            if keyCopies[key]<node_state.replicationFactor:
                node_state.storage.copyIndexes[key]=keyCopies[key]
                keyCopies[key]+=1
            elif keyCopies[key]==node_state.replicationFactor:
                node_state.storage.insert(key, values[key])
                node_state.storage.copyIndexes[key]=node_state.replicationFactor
                del keyCopies[key] #avoid loop contition for next node
                keys.remove(key)
                del values[key]
        print("after for")
        visited.append(node_state.node_address)
        print(visited)
        print(keys)
        if keys==[]:
            return jsonify({'status': 'success', 'message': f"reached node {node_state.node_address} with all keys updated"}), 201
        print("before next node")
        response= requests.post(f"http://{node_state.next_node}/updateNext", json={ 'keys':keys, 'values':values, 'keyCopies':keyCopies, 'visited':visited})
        print("after next node")
        return response.json()
    else:
        response= jsonify({'status': 'success', 'message': f"reached node {node_state.node_address}"}), 201
        return response.json()

