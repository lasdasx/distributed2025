from flask import Blueprint, request, jsonify
import requests
from utils import forward_request,backward_request
from state import node_state  # Import the centralized state
from utils import chord_hash

registerBp = Blueprint('register', __name__)


@registerBp.route('/register', methods=['POST'])
def register():
    new_node = request.json['newNode']
    new_node_hash = chord_hash(new_node)
    node_adress_hash = node_state.node_address_hash
    next_node_hash = chord_hash(node_state.next_node)
    prev_node_hash = chord_hash(node_state.prev_node)
  
    # Case 1: If the ring is empty, initialize it with the new node
    if next_node_hash == node_adress_hash or prev_node_hash == node_adress_hash:
        print("first if")
        requests.post(f"http://{node_state.node_address}/update-next", json={"next_node": new_node})
        requests.post(f"http://{node_state.node_address}/update-prev", json={"prev_node": new_node})
        requests.post(f"http://{new_node}/update-next", json={"next_node": node_state.node_address})
        requests.post(f"http://{new_node}/update-prev", json={"prev_node": node_state.node_address})
        return jsonify({'status': 'registered'}), 201

    # Case 2: New node belongs between the current node and next node
    elif node_adress_hash < new_node_hash < new_node_hash:
        print("second if")
        requests.post(f"http://{new_node}/update-prev", json={"prev_node": node_state.node_address})
        requests.post(f"http://{new_node}/update-next", json={"next_node": node_state.next_node})
        requests.post(f"http://{node_state.next_node}/update-prev", json={"prev_node": new_node})    
        requests.post(f"http://{node_state.node_address}/update-next", json={"next_node": new_node})

        return jsonify({'status': 'registered'}), 201

    # Case 3: New node belongs before the current node but after previous node
    elif prev_node_hash < new_node_hash < node_adress_hash:
        print("third if")
        requests.post(f"http://{new_node}/update-prev", json={"prev_node": node_state.prev_node})
        requests.post(f"http://{new_node}/update-next", json={"next_node": node_state.node_address})
        requests.post(f"http://{node_state.prev_node}/update-next", json={"next_node": new_node})
        requests.post(f"http://{node_state.node_address}/update-prev", json={"prev_node": new_node})
        return jsonify({'status': 'registered'}), 201

    # Case 4: Ring Wraparound (Handles cases where the next node is smaller due to circular nature)
    elif next_node_hash < node_adress_hash:
        print("fourth if")
        if new_node_hash > node_adress_hash or new_node_hash < new_node_hash:
            print("fourth if inner")
            requests.post(f"http://{new_node}/update-prev", json={"prev_node": node_state.node_address})
            requests.post(f"http://{new_node}/update-next", json={"next_node": node_state.next_node})
            requests.post(f"http://{node_state.next_node}/update-prev", json={"prev_node": new_node})
            requests.post(f"http://{node_state.node_address}/update-next", json={"next_node": new_node})
            return jsonify({'status': 'registered'}), 201

    # Case 5: Forward request if the new node does not belong here
    elif new_node_hash > node_adress_hash:
        print("fifth if")
        forward_request('register', new_node)
        return jsonify({'status': 'forwarded'}), 201
    else:
        print("sixth if")
        backward_request('register', new_node)
        return jsonify({'status': 'backwarded'}), 201