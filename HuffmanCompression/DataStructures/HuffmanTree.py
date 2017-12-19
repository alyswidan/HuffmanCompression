import heapq

from HuffmanCompression.DataStructures.Node import *


class HuffmanTree:
    def __init__(self, root=None, calculate_codes=True):
        self.root = root
        self._len = 0
        if calculate_codes:
            HuffmanTree._calculate_codes(root)
        self._codes = None

    @classmethod
    def from_codes(cls, code_dict):
        # left = 0, right = 1
        sorted_codes = sorted([(v, k) for (k, v) in code_dict.items()], key=lambda pair: len(pair[0]))
        root = Node(node_type='junction')
        for (code, value) in sorted_codes:
            current_node = root
            for i in code:
                if i == '0':
                    if current_node.left is None:
                        current_node.left = Node(node_type='junction')
                    current_node = current_node.left
                elif i == '1':
                    if current_node.right is None:
                        current_node.right = Node(node_type='junction')
                    current_node = current_node.right
            current_node.code = code
            current_node.node_type = 'leaf'
            current_node.value = value
        return cls(root, calculate_codes=False)

    @classmethod
    def from_frequencies(cls, freq_dict):
        node_heap = [Node(value=freq[0], count=freq[1]) for freq in freq_dict.items()]

        heapq.heapify(node_heap)
        while len(node_heap) != 1:
            left = heapq.heappop(node_heap)
            right = heapq.heappop(node_heap)
            heapq.heappush(node_heap, Node(count=left.count + right.count,
                                            left=left,
                                            right=right,
                                            node_type='junction'))
        return cls(node_heap[0])

    @staticmethod
    def _elements_iterator(current_node, get_junctions=False):
        if current_node:
            for node in HuffmanTree._elements_iterator(current_node.left, get_junctions):
                yield node

            if get_junctions or current_node.node_type == 'leaf':
                yield current_node

            for node in HuffmanTree._elements_iterator(current_node.right, get_junctions):
                yield node

    def elements(self, get_junctions=False):
        return HuffmanTree._elements_iterator(self.root, get_junctions)

    @staticmethod
    def _calculate_codes(root=None, current_code=""):
        if root is None:
            return
        if root.node_type == 'leaf':
            root.code = current_code
            return
        HuffmanTree._calculate_codes(root.left, current_code=current_code + '0')
        HuffmanTree._calculate_codes(root.right, current_code=current_code + '1')

    @property
    def codes(self):
        """code dict"""
        if self._codes is None:
            self._codes = dict([(node.value, node.code) for node in self.elements()])

        return self._codes

    def __len__(self):
        if self._len == 0:
            self._len = len(list(self.elements()))
        return self._len

    def __str__(self):
        return str(list(self.elements(get_junctions=True)))
