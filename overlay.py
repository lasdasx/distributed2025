from flask import Blueprint, request, jsonify
import requests
from state import node_state

from utils import forward_request,backward_request, chord_hash

overlayBp = Blueprint('overlay', __name__)


@overlayBp.route('/overlay', methods=['GET'])
def overlay():
    visitedNodes=[]
    nextNode=node_state.next_node
    currrentNode=node_state.node_address
    while currrentNode not in visitedNodes:
        visitedNodes.append(currrentNode)    
        response=requests.get(f"http://{currrentNode}/get-next")
        nextNode=response.json()['next_node']
        currrentNode=nextNode
        print(currrentNode,chord_hash(currrentNode))
    print(node_state.next_node,node_state.prev_node)

    return jsonify({'nodes': visitedNodes}), 200
# @overlayBp.route('/overlay/<key>', methods=['POST'])
# def overlay(key):
#     print(f"Got request at node: {node_state.node_address}")
#     array = request.json.get('array', [])
#     print(f"Received array: {array}")

#     # If the current node is already in the array, check if it's the first or second occurrence
#     if array.count(node_state.node_address) >= 1:
#         print("Cycle detected or node revisited. Returning collected nodes.")
#         # Deduplicate the array before returning
#         unique_nodes = list(dict.fromkeys(array))
#         return jsonify({'nodes': unique_nodes}), 200
    
#     # If not, add the current node to the array
#     array.append(node_state.node_address)
#     print(f"Array after appending: {array}")
#     print(f"Forwarding to next node: {node_state.next_node}")
    
#     # Forward to the next node
#     response = forward_request('overlay', key, {'array': array})
    
#     # If we got a response, pass it back up the chain
#     if response and 'nodes' in response:
#         return jsonify(response), 200
    
#     return jsonify({'status': 'forwarded'}), 202

