from flask import Blueprint, request, jsonify
import requests
from utils import forward_request,backward_request
from state import node_state  # Import the centralized state
from utils import chord_hash,is_responsible


registerLinearBp = Blueprint('registerLinear', __name__)


@registerLinearBp.route('/register', methods=['POST'])
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
    elif node_adress_hash < new_node_hash < next_node_hash:
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
        if new_node_hash > node_adress_hash or new_node_hash < next_node_hash:
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
    
# @registerBp.route('/registerLinear', methods=["POST"])
# def registerLinear():
#     new_node = request.json['newNode']
#     response = requests.post(f"http://{node_state.node_address}/register", json={'newNode': new_node})
#     nextOfNew = requests.get(f"http://{new_node}/get-next").json()['next_node']
#     print(nextOfNew)
#     response = requests.get(f"http://{nextOfNew}/getReplicated").json()
#     replicatedData=response['replicatedData']
#     print(replicatedData)
#     copyIndexes=response['copyIndexes']
#     print(copyIndexes)
#     response = requests.post(f"http://{new_node}/addReplicated", json={'replicatedData': replicatedData, 'copyIndexes': copyIndexes})
#     return response.json(), 201


# @registerBp.route('/getReplicated', methods=["GET"])
# def getReplicated():
#     replicatedData={}
#     copyIndexes={}
#     for key in list(node_state.storage.data):
#         if not is_responsible(key):
#             if node_state.storage.copyIndexes[key]==1:
#                 copyIndexes[key]=1
#                 replicatedData[key]=node_state.storage.query(key)
#                 node_state.storage.delete(key)

#                 requests.post(f"http://{node_state.node_address}/updateCopyIndexes", json={'key': key, 'currentCopy': copyIndexes[key]+ 1})

                
#             else:    
#                 copyIndexes[key]=node_state.storage.copyIndexes[key]
#                 replicatedData[key]=node_state.storage.query(key)
                
#                 requests.post(f"http://{node_state.node_address}/updateCopyIndexes", json={'key': key, 'currentCopy': copyIndexes[key]+ 1})


#     return jsonify({'replicatedData': replicatedData, "copyIndexes": copyIndexes}), 200


# @registerBp.route('/updateCopyIndexes', methods=["POST"])
# def updateCopyIndexes():
#     currentCopy=request.json["currentCopy"]
#     key=request.json["key"]

#     if node_state.storage.copyIndexes[key]!=1 or (node_state.storage.copyIndexes[key]==1 and node_state.replicationFactor==1): #not a full circle completed
#         if currentCopy>node_state.replicationFactor:
#             node_state.storage.delete(key)
#             return jsonify({'status': "success"}), 200
#         else: 
#             node_state.storage.copyIndexes[key]=currentCopy
#             requests.post(f"http://{node_state.next_node}/updateCopyIndexes", json={'key': key, 'currentCopy': currentCopy+1})
#             return jsonify({'status': "success"}), 200
        
#     return jsonify({'status': "success"}), 200


# @registerBp.route('/addReplicated', methods=["POST"])
# def addReplicated():
#     try:
#         replicatedData=request.json["replicatedData"]
#         copyIndexes=request.json["copyIndexes"]
#         for key, value in replicatedData.items():
#             node_state.storage.insert(key, value)
#             node_state.storage.copyIndexes[key]=copyIndexes[key]
            
#         return jsonify({'status': "success"}), 200
#     except Exception as e:
#         print(e)
#         return jsonify({'status': "failed"}), 500
    


@registerLinearBp.route('/registerLinear', methods=["POST"])
def registerLinear():
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

    response = requests.post(f"http://{nextOfNew}/updateCopyIndexes", json={'copyIndexes': keysToCopy}) #copy indexes= oi times poy exei o new node

    return response.json(), 201



@registerLinearBp.route('/updateCopyIndexes',methods=["POST"])
def updateCopyIndexes():
    try:
        copyIndexes=request.json["copyIndexes"]
        print(copyIndexes)
        for key in list(copyIndexes):
            if copyIndexes[key]<node_state.replicationFactor :
                if  copyIndexes[key]==node_state.storage.copyIndexes[key]:
                    node_state.storage.copyIndexes[key]=copyIndexes[key]+1
                    copyIndexes[key]+=1
                else:
                    del copyIndexes[key]

            elif copyIndexes[key]==node_state.replicationFactor:
                del copyIndexes[key]
                if not node_state.storage.copyIndexes[key]==1:
                    del node_state.storage.data[key]
                    del node_state.storage.copyIndexes[key]
        if copyIndexes!={}:
            response= requests.post(f"http://{node_state.next_node}/updateCopyIndexes", json={'copyIndexes': copyIndexes})
            return response.json()
        else:
            return jsonify({'status': "success"}), 200
    except Exception as e:
        print(e)
        return jsonify({'status': "failed"}), 500

@registerLinearBp.route('/addKeys', methods=["POST"])
def addKeys():
    try:
        values=request.json["values"]
        keys=request.json["keys"]
        for key in keys:
            node_state.storage.copyIndexes[key]=keys[key]
            node_state.storage.data[key]=values[key]
        return jsonify({'status': "success"}), 200
    except Exception as e:
        print(e)
        return jsonify({'status': "failed"}), 500

@registerLinearBp.route('/getRedistributeKeys', methods=["GET"])
def getRedistributeKeys():
    keys={}    
    values={}
    for key in list(node_state.storage.data):
        if not is_responsible(key) and node_state.storage.copyIndexes[key]==1:
            keys[key]=1  
            values[key]=node_state.storage.data[key]          
    return jsonify({'redistributeKeys': keys, 'values':values}), 200

@registerLinearBp.route('/getReplicateKeys', methods=["GET"])
def getReplicateKeys():
    keyCopies={}
    values={}
    for key in list(node_state.storage.data):
        if node_state.storage.copyIndexes[key]<node_state.replicationFactor:
            keyCopies[key]=node_state.storage.copyIndexes[key]+1
            values[key]=node_state.storage.data[key]
    return jsonify({'replicateKeys': keyCopies,'values':values}), 200