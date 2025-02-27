from flask import Blueprint, request, jsonify
import requests
from utils import forward_request,backward_request
from state import node_state  # Import the centralized state

registerBp = Blueprint('register', __name__)


# @registerBp.record_once
# def setup(setup_state):
#     global prev_node, next_node, node_address , active_nodes
#     prev_node = setup_state.options['prev_node']
#     next_node = setup_state.options['next_node']
#     active_nodes = setup_state.options['active_nodes']
#     node_address = setup_state.options['node_address']

@registerBp.route('/register', methods=['POST'])
def register():

    new_node = request.json['newNode']
    if node_state.next_node == None or node_state.prev_node == None:
        print("AAAAAEEE")
        requests.post(f"http://{node_state.node_address}/update-next", json={"next_node": new_node})
        requests.post(f"http://{new_node}/update-prev", json={"prev_node": node_state.node_address})
        requests.post(f"http://{new_node}/update-next", json={"next_node": node_state.node_address})
        requests.post(f"http://{node_state.node_address}/update-prev", json={"prev_node": new_node})
        print(node_state.prev_node, node_state.next_node)
        print("AAAAAAAAAAAAAAcccc")
        return jsonify({'status': 'registered'}), 201
        
    if node_state.next_node < node_state.node_address and (new_node > node_state.node_address or new_node < node_state.next_node):
        requests.post(f"http://{node_state.node_address}/update-next", json={"next_node": new_node})
        requests.post(f"http://{new_node}/update-prev", json={"prev_node": node_state.node_address})
        requests.post(f"http://{new_node}/update-next", json={"next_node": node_state.next_node})
        requests.post(f"http://{node_state.next_node}/update-prev", json={"prev_node": new_node})
        
    else:     
        if new_node > node_state.node_address and new_node < node_state.next_node:
            requests.post(f"http://{node_state.node_address}/update-next", json={"next_node": new_node})
            requests.post(f"http://{new_node}/update-prev", json={"prev_node": node_state.node_address})
            requests.post(f"http://{new_node}/update-next", json={"next_node": node_state.next_node})
            requests.post(f"http://{node_state.next_node}/update-prev", json={"prev_node": new_node})
        
        elif new_node > node_state.node_address and new_node > node_state.next_node:
            forward_request('register', new_node)
            
        elif new_node < node_state.node_address and new_node < node_state.prev_node:
            backward_request('register', new_node)
        
        elif new_node < node_state.node_address and new_node > node_state.prev_node:
            requests.post(f"http://{node_state.node_address}/update-prev", json={"prev_node": new_node})
            requests.post(f"http://{new_node}/update-prev", json={"prev_node": node_state.prev_node})
            requests.post(f"http://{new_node}/update-next", json={"next_node": node_state.node_address})
            requests.post(f"http://{node_state.prev_node}/update-next", json={"next_node": new_node})
    print(node_state.prev_node, node_state.next_node)
    print("AAAAAAAAAAAAAA")