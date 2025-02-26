import requests

class Router:
    def __init__(self, node_address, consistent_hash):
        self.node_address = node_address
        self.consistent_hash = consistent_hash

    def route_request(self, key, action, value=None):
        target_node = self.consistent_hash.get_node(key)
        if target_node == self.node_address:
            return None  # This node is responsible

        url = f"http://{target_node}/{action}/{key}"
        if action == "insert":
            response = requests.post(url, json={'value': value})
        elif action == "delete":
            response = requests.delete(url)
        else:  # query
            response = requests.get(url)
        return response.json()
