import heapq
from collections import Counter


class _Node:
    """
    node_type: junction or normal
    left: left child
    right: right child
    """

    def __init__(self, value=None, count=0, left=None, right=None, node_type='normal'):
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
        root = _Node(node_type='junction')
        for (code, value) in sorted_codes:
            current_node = root
            for i in code:
                if i == '0':
                    if current_node.left is None:
                        current_node.left = _Node(node_type='junction')
                    current_node = current_node.left
                elif i == '1':
                    if current_node.right is None:
                        current_node.right = _Node(node_type='junction')
                    current_node = current_node.right
            current_node.code = code
            current_node.node_type = 'normal'
            current_node.value = value
        return cls(root, calculate_codes=False)

    @classmethod
    def from_frequencies(cls, freq_dict):
        node_heap = [_Node(value=freq[0], count=freq[1]) for freq in freq_dict.items()]

        heapq.heapify(node_heap)
        while len(node_heap) != 1:
            left = heapq.heappop(node_heap)
            right = heapq.heappop(node_heap)
            heapq.heappush(node_heap, _Node(count=left.count + right.count,
                                            left=left,
                                            right=right,
                                            node_type='junction'))
        return cls(node_heap[0])

    @staticmethod
    def _elements_iterator(current_node, get_junctions=False):
        if current_node:
            for node in HuffmanTree._elements_iterator(current_node.left, get_junctions):
                yield node

            if get_junctions or current_node.node_type == 'normal':
                yield current_node

            for node in HuffmanTree._elements_iterator(current_node.right, get_junctions):
                yield node

    def elements(self, get_junctions=False):
        return HuffmanTree._elements_iterator(self.root, get_junctions)

    @staticmethod
    def _calculate_codes(root=None, current_code=""):
        if root is None:
            return
        if root.node_type == 'normal':
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


def bytes_from_file(filename, chunksize=8192):
    with open(filename, "rb") as file:
        while True:
            chunk = file.read(chunksize)
            if chunk:
                for b in chunk:
                    yield b
                else:
                    break


def write_header(filename, huff_tree):
    with open('{}.comp'.format(filename), 'w') as file:
        num = len(huff_tree)
        for i, node in enumerate(huff_tree.elements()):
            file.write(chr(node.value))
            file.write(node.code)
            if i < num - 1:
                file.write('.')
        file.write('_.')


def packed_bits(filename, code_dict):
    file_content = [b for b in bytes_from_file(filename)]
    file_codes = [code_dict[val] for val in file_content]
    current = 0
    idx = 7
    for code in file_codes:
        for b in code:
            mask = (int(b) << idx)
            current |= mask
            idx -= 1
            if idx == -1:
                idx = 7
                yield current
                current = 0


def to_byte_str(num):
    return '{:08b}'.format(num)


def dict_from_header(filename="", chunksize=512):
    code_dict = {}
    idx = 0
    with open('{}.comp'.format(filename), "rb") as inp:
        done = False
        while not done:
            chunk = inp.read(chunksize)
            if chunk:
                prev = None
                key = None
                code = ''
                for c in chunk:
                    idx += 1
                    if c >= 128:
                        return idx, code_dict
                    c = chr(c)
                    if c == '.' and prev != '.':
                        if key:
                            code_dict[key] = code
                            key = None
                            code = ''
                        if prev == '_':
                            done = True
                            break

                    elif key is None:
                        key = c
                    elif c in ['0', '1']:
                        code += c
                    prev = c

            else:
                break

    return idx, code_dict


def compress(filename=""):
    byte_freq = Counter(bytes_from_file(filename))

    huff_tree = HuffmanTree.from_frequencies(byte_freq)

    encoded_file = bytes([x for x in packed_bits(filename, huff_tree.codes)])
    ss = [to_byte_str(x) for x in packed_bits(filename, huff_tree.codes)]
    print(sorted([x for x in huff_tree.codes.values()], key=len))
    print(' '.join(ss))
    print(dict([(chr(a), b) for (a, b) in huff_tree.codes.items()]))
    write_header(filename, huff_tree)
    with open('{}.comp'.format(filename), "ab") as out:
        out.write(encoded_file)


def decode(strn, code_dict):
    huff_tree = HuffmanTree.from_codes(code_dict)
    result = ''
    current_node = huff_tree.root
    strn = strn + 'e'  # a hack to indicate end of line
    for i in strn:
        if current_node.node_type == 'normal' or i == 'e':
            result += current_node.value
            current_node = huff_tree.root
        if i == '0':
            current_node = current_node.left
        elif i == '1':
            current_node = current_node.right

    return result


def decompress(filename=""):
    last, codes = dict_from_header(filename)
    print(codes)
    file_content = ""
    with open('{}.comp'.format(filename), "rb") as inp:
        inp.seek(last)
        file_content = file_content.join([to_byte_str(b) for b in inp.read(8192)])

    print(file_content)
    print(decode(file_content, codes))


compress('HuffmanCompression/test.test')
decompress('HuffmanCompression/test.test')
