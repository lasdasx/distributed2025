class Storage:
    def __init__(self):
        self.data = {}
        self.copyIndexes = {}

    def insert(self, key, value):
        self.data[key] = value

    def delete(self, key):
        if key in self.data:
            del self.data[key]
            del self.copyIndexes[key]

    def query(self, key):
        return self.data.get(key, None)
