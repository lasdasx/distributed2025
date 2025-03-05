from flask import Blueprint, request, jsonify
import requests
from state import node_state 
eventualBp = Blueprint('eventual', __name__)

def get_replica_nodes():
    """ Returns a list of replica nodes based on the replication factor. """
    replicas = []
    current_node = node_state.next_node  # Start with the next node

    for _ in range(node_state.replicationFactor - 1):  # Get the next N-1 nodes
        replicas.append(current_node)
        # Ask the node for its successor to find the next replica
        try:
            response = requests.get(f"http://{current_node}/get_next_node", timeout=1)
            if response.status_code == 200:
                current_node = response.json().get("next_node")
            else:
                break
        except Exception:
            break  # If a node fails, stop adding replicas

    return replicas

def replicate_to_peers(key, value):
    """ Propagates the update to other replicas asynchronously """
    for peer in get_replica_nodes():
        try:
            requests.post(f"http://{peer}/replicate/{key}", json={'value': value}, timeout=1)
        except Exception as e:
            print(f"Replication to {peer} failed: {e}")

@eventualBp.route('/replicate/<key>', methods=['POST'])
def replicate(key):
    """ Endpoint to handle replication from primary node """
    value = request.json['value']
    node_state.storage.insert(key, value)
    return jsonify({'status': 'replicated', 'node': node_state.node_address}), 200

def propagate_delete(key):
    """ Propagates the delete request to replica nodes asynchronously """
    for peer in get_replica_nodes():
        try:
            requests.delete(f"http://{peer}/replicate_delete/{key}", timeout=1)
        except Exception as e:
            print(f"Delete replication to {peer} failed: {e}")

@eventualBp.route('/replicate_delete/<key>', methods=['DELETE'])
def replicate_delete(key):
    """ Replica nodes receive delete requests asynchronously """
    node_state.storage.delete(key)
    return jsonify({'status': 'replicated_delete', 'node': node_state.node_address}), 200