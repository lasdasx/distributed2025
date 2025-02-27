import hashlib

class ConsistentHash:
    def __init__(self):
        self.ring = {}
        self.nodes = []

    def _hash(self, key):
        return int(hashlib.sha256(key.encode('utf-8')).hexdigest(), 16)

    def add_node(self, node):
        hash_value = self._hash(node)
        self.ring[hash_value] = {
            'address': node,
            'next': None,
            'prev': None
        }
        self.nodes.append(hash_value)
        self.nodes.sort()
        self._update_pointers()

    def remove_node(self, node):
        hash_value = self._hash(node)
        del self.ring[hash_value]
        self.nodes.remove(hash_value)
        self._update_pointers()

    def _update_pointers(self):
        if len(self.nodes) < 2:
            return

        for i, node_hash in enumerate(self.nodes):
            prev_index = (i - 1) % len(self.nodes)
            next_index = (i + 1) % len(self.nodes)
            self.ring[node_hash]['prev'] = self.ring[self.nodes[prev_index]]['address']
            self.ring[node_hash]['next'] = self.ring[self.nodes[next_index]]['address']

    def get_node(self, key):
        hash_value = self._hash(key)
        for node_hash in self.nodes:
            if hash_value <= node_hash:
                return self.ring[node_hash]['address']
        return self.ring[self.nodes[0]]['address']

    def get_next(self, node):
        hash_value = self._hash(node)
        return self.ring[hash_value]['next']

    def get_prev(self, node):
        hash_value = self._hash(node)
        return self.ring[hash_value]['prev']
