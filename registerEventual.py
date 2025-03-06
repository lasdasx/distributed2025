from flask import Blueprint, request, jsonify
import requests
from utils import forward_request,backward_request
from state import node_state  # Import the centralized state
from utils import chord_hash,is_responsible
import threading

registerEventualBp = Blueprint('registerEventual', __name__)



@registerEventualBp.route('/registerEventual', methods=["POST"])
def registerEventual():
    new_node = request.json['newNode']
    response = requests.post(f"http://{node_state.node_address}/register", json={'newNode': new_node})
    nextOfNew = requests.get(f"http://{new_node}/get-next").json()['next_node']
    print(nextOfNew)


    response = requests.get(f"http://{nextOfNew}/getRedistributeKeys").json()
    redistributeKeys=response['redistributeKeys']
    values1=response['values']
    prevOfNew = requests.get(f"http://{new_node}/get-prev").json()['prev_node']
    print(nextOfNew)

    response = requests.get(f"http://{prevOfNew}/getReplicateKeys").json()
    replicateKeys=response['replicateKeys']
    values2=response['values']
    values=values2|values1
    print('values ', values)
    keysToCopy=replicateKeys|redistributeKeys
    print('keysToCopy ', keysToCopy)
    response = requests.post(f"http://{new_node}/addKeys", json={'keys': keysToCopy, 'values':values})


    threading.Thread(
        target=requests.post, 
        args=(f"http://{nextOfNew}/updateCopyIndexes",), 
        kwargs={'json': {'copyIndexes': keysToCopy}, 'timeout': 2}, 
        daemon=True
    ).start()

    return response.json(), 201


