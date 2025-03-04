# state.py
from storage import Storage
class NodeState:
    prev_node = None
    next_node = None
    node_address = None
    node_address_hash = None
    prev_node_hash = None
    next_node_hash = None
    storage=Storage()

node_state = NodeState()
