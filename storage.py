class Storage:
    def __init__(self):
        self.data = {}

    def insert(self, key, value):
        self.data[key] = value

    def delete(self, key):
        if key in self.data:
            del self.data[key]

    def query(self, key):
        return self.data.get(key, None)
