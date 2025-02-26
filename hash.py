import hashlib

class ConsistentHash:
    def __init__(self):
        self.ring = {}
        self.nodes = []

    def _hash(self, key):
        return int(hashlib.sha256(key.encode('utf-8')).hexdigest(), 16)

    def add_node(self, node):
            hash_value = self._hash(node)
            self.ring[hash_value] = node
            self.nodes.append(hash_value)
            self.nodes.sort()

    def remove_node(self, node):
            hash_value = self._hash(node)
            del self.ring[hash_value]
            self.nodes.remove(hash_value)

    def get_node(self, value):
        hash_value = self._hash(value)
        for node_hash in self.nodes:
            if hash_value <= node_hash:
                return self.ring[node_hash]
        return self.ring[self.nodes[0]]
