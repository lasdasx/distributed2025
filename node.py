from flask import Flask, request, jsonify
from storage import Storage
from hash import ConsistentHash
from routing import Router

app = Flask(__name__)
storage = Storage()
consistent_hash = ConsistentHash()
router = Router(node_address="localhost:5000", consistent_hash=consistent_hash)

@app.route('/insert/<key>', methods=['POST'])
def insert(key):
    value = request.json['value']
    target_response = router.route_request(key, 'insert', value)
    if target_response is None:  # This node is responsible
        storage.insert(key, value)
        return jsonify({'status': 'success', 'node': 'self'}), 201
    return jsonify(target_response)

@app.route('/query/<key>', methods=['GET'])
def query(key):
    target_response = router.route_request(key, 'query')
    if target_response is None:  # This node is responsible
        value = storage.query(key)
        return jsonify({'value': value, 'node': 'self'}), 200
    return jsonify(target_response)

@app.route('/delete/<key>', methods=['DELETE'])
def delete(key):
    target_response = router.route_request(key, 'delete')
    if target_response is None:  # This node is responsible
        storage.delete(key)
        return jsonify({'status': 'deleted', 'node': 'self'}), 200
    return jsonify(target_response)

if __name__ == '__main__':
    # Add this node to the consistent hash ring
    consistent_hash.add_node("localhost:5000")
    app.run(port=5000)
