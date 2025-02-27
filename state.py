# state.py
from storage import Storage
class NodeState:
    prev_node = None
    next_node = None
    node_address = None
    active_nodes = []
    storage=Storage()

node_state = NodeState()
