class Node:
    """
    node_type: junction or leaf
    left: left child
    right: right child
    """

    def __init__(self, value=None, count=0, left=None, right=None, node_type='leaf'):
        self.right = right
        self.left = left
        self.node_type = node_type
        self.value = value
        self.count = count
        self.code = None

    def __lt__(self, other):
        return self.count < other.count

    def __str__(self):
        return str((self.value, self.count, self.node_type))

    __repr__ = __str__