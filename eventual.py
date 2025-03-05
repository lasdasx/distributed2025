from flask import Blueprint, request, jsonify
import requests
from state import node_state
import threading 
eventualBp = Blueprint('eventual', __name__)

def get_successor_node():
    """ Get the next node in the Chord ring """
    return node_state.next_node  # Assuming this is updated by stabilization

# def get_replica_nodes():
#     """ Returns a list of replica nodes based on the replication factor. """
#     replicas = []
#     current_node = node_state.next_node  # Start with the next node

#     for _ in range(node_state.replicationFactor - 1):  # Get the next N-1 nodes
#         replicas.append(current_node)
#         # Ask the node for its successor to find the next replica
#         try:
#             response = requests.get(f"http://{current_node}/get_next_node", timeout=1)
#             if response.status_code == 200:
#                 current_node = response.json().get("next_node")
#             else:
#                 break
#         except Exception:
#             break  # If a node fails, stop adding replicas

#     return replicas

# def replicate_to_peers(key, value):
#     """ Propagates the update to other replicas asynchronously """
#     for peer in get_replica_nodes():
#         try:
#             requests.post(f"http://{peer}/replicate/{key}", json={'value': value}, timeout=1)
#         except Exception as e:
#             print(f"Replication to {peer} failed: {e}")
            

# @eventualBp.route('/replicate/<key>', methods=['POST'])
# def replicate(key):
#     """ Endpoint to handle replication from primary node """
#     value = request.json['value']
#     node_state.storage.insert(key, value)
#     return jsonify({'status': 'replicated', 'node': node_state.node_address}), 200

def replicate_to_successor(key, value, hop=1):
    """ Forward replication to the next node in the Chord ring """
    if hop >= node_state.replicationFactor:
        return  # Stop forwarding after reaching replication factor limit

    successor = get_successor_node()
    if not successor:
        return  # If no successor is found, replication stops

    try:
        requests.post(f"http://{successor}/replicate/{key}", 
                      json={'value': value, 'hop': hop + 1}, timeout=1)
    except Exception as e:
        print(f"Replication to successor {successor} failed: {e}")

@eventualBp.route('/replicate/<key>', methods=['POST'])
def replicate(key):
    """ Handle replication request, store locally and forward if needed """
    data = request.json
    value = data['value']
    hop = data.get('hop', 1)

    # Store the replicated value locally
    node_state.storage.insert(key, value)

    # Continue forwarding replication to the next successor
    threading.Thread(target=replicate_to_successor, args=(key, value, hop)).start()

    return jsonify({'status': 'replicated', 'node': node_state.node_address}), 200

# def propagate_delete(key):
#     """ Propagates the delete request to replica nodes asynchronously """
#     for peer in get_replica_nodes():
#         try:
#             requests.delete(f"http://{peer}/replicate_delete/{key}", timeout=1)
#         except Exception as e:
#             print(f"Delete replication to {peer} failed: {e}")

# @eventualBp.route('/replicate_delete/<key>', methods=['DELETE'])
# def replicate_delete(key):
#     """ Replica nodes receive delete requests asynchronously """
#     node_state.storage.delete(key)
#     return jsonify({'status': 'replicated_delete', 'node': node_state.node_address}), 200

def propagate_delete_to_successor(key, hop=1):
    """ Forward delete request to next node in the Chord ring """
    if hop >= node_state.replicationFactor:
        return  # Stop forwarding after reaching replication factor limit

    successor = get_successor_node()
    if not successor:
        return  # If no successor is found, stop

    try:
        requests.delete(f"http://{successor}/replicate_delete/{key}", json={"hop": hop + 1}, timeout=1)
    except Exception as e:
        print(f"Delete replication to successor {successor} failed: {e}")

@eventualBp.route('/replicate_delete/<key>', methods=['DELETE'])
def replicate_delete(key):
    """ Handle delete request, delete locally and forward if needed """
    hop = request.json.get("hop", 1)

    # Delete locally
    node_state.storage.delete(key)

    # Forward deletion to next successor
    threading.Thread(target=propagate_delete_to_successor, args=(key, hop)).start()

    return jsonify({'status': 'replicated_delete', 'node': node_state.node_address}), 200
