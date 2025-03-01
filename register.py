from flask import Blueprint, request, jsonify
import requests
from utils import forward_request,backward_request
from state import node_state  # Import the centralized state

registerBp = Blueprint('register', __name__)


@registerBp.route('/register', methods=['POST'])
def register():
    new_node = request.json['newNode']
    print("request received")

    print(f"Current node: {node_state.node_address}, Next node: {node_state.next_node}, Prev node: {node_state.prev_node}, New node: {new_node}")
    print(node_state.next_node is node_state.node_address)
    print(node_state.prev_node is node_state.node_address)
    print(type(node_state.node_address))
    print(type(node_state.prev_node))
    print(type(node_state.node_address))
    # Case 1: If the ring is empty, initialize it with the new node
    if node_state.next_node == node_state.node_address or node_state.prev_node == node_state.node_address:
        print("first if")
        requests.post(f"http://{node_state.node_address}/update-next", json={"next_node": new_node})
        requests.post(f"http://{node_state.node_address}/update-prev", json={"prev_node": new_node})
        requests.post(f"http://{new_node}/update-next", json={"next_node": node_state.node_address})
        requests.post(f"http://{new_node}/update-prev", json={"prev_node": node_state.node_address})
        return jsonify({'status': 'registered'}), 201

    # Case 2: New node belongs between the current node and next node
    elif node_state.node_address < new_node < node_state.next_node:
        print("second if")
        requests.post(f"http://{new_node}/update-prev", json={"prev_node": node_state.node_address})
        requests.post(f"http://{new_node}/update-next", json={"next_node": node_state.next_node})
        requests.post(f"http://{node_state.node_address}/update-next", json={"next_node": new_node})
        requests.post(f"http://{node_state.next_node}/update-prev", json={"prev_node": new_node})
        return jsonify({'status': 'registered'}), 201

    # Case 3: New node belongs before the current node but after previous node
    elif node_state.prev_node < new_node < node_state.node_address:
        print("third if")
        requests.post(f"http://{new_node}/update-prev", json={"prev_node": node_state.prev_node})
        requests.post(f"http://{new_node}/update-next", json={"next_node": node_state.node_address})
        requests.post(f"http://{node_state.prev_node}/update-next", json={"next_node": new_node})
        requests.post(f"http://{node_state.node_address}/update-prev", json={"prev_node": new_node})
        return jsonify({'status': 'registered'}), 201

    # Case 4: Ring Wraparound (Handles cases where the next node is smaller due to circular nature)
    elif node_state.next_node < node_state.node_address:
        print("fourth if")
        if new_node > node_state.node_address or new_node < node_state.next_node:
            print("fourth if inner")
            requests.post(f"http://{new_node}/update-prev", json={"prev_node": node_state.node_address})
            requests.post(f"http://{new_node}/update-next", json={"next_node": node_state.next_node})
            requests.post(f"http://{node_state.node_address}/update-next", json={"next_node": new_node})
            requests.post(f"http://{node_state.next_node}/update-prev", json={"prev_node": new_node})
            return jsonify({'status': 'registered'}), 201

    # Case 5: Forward request if the new node does not belong here
    elif new_node > node_state.node_address:
        print("fifth if")
        forward_request('register', new_node)
        return jsonify({'status': 'forwarded'}), 201
    else:
        print("sixth if")
        backward_request('register', new_node)
        return jsonify({'status': 'backwarded'}), 201