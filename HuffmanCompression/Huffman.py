import heapq
from collections import Counter


class _Node:
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
            current_node.node_type = 'leaf'
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


def read_from_file(filename, chunksize=8192, mode="rb", start=0):
    with open(filename, mode) as file:
        file.seek(start)
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
        file.write('_.')  # terminate header with _. this can't occur in actual header


def packed_bits(filename, code_dict):
    file_content = [b for b in read_from_file(filename, mode="rb")]
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


def append_comp_suffix(filename):
    return '{}.comp'.format(filename)


def dict_from_header(filename=""):
    code_dict = {}
    idx = 0
    prev = None
    key = None
    code = ''

    for c in read_from_file(append_comp_suffix(filename), mode="rb"):
        idx += 1
        if c >= 128:  # if c is not in ascii range we fetched beyond header
            return idx, code_dict
        c = chr(c)
        if c == '.' and prev != '.':  # .. means separator followed by code of character '.'
            if key:
                code_dict[key] = code
                key = None
                code = ''
            if prev == '_':
                break

        elif key is None:
            key = c
        elif c in ['0', '1']:
            code += c
        prev = c

    return idx, code_dict


def compress(filename=""):
    file_content = [b for b in read_from_file(filename, mode="rb")]
    byte_freq = Counter(file_content)

    huff_tree = HuffmanTree.from_frequencies(byte_freq)

    encoded_file = bytes([x for x in packed_bits(filename, huff_tree.codes)])
    # debug
    # ss = [to_byte_str(x) for x in packed_bits(filename, huff_tree.codes)]
    # print(sorted([x for x in huff_tree.codes.values()], key=len))
    # print(' '.join(ss))
    # print(dict([(chr(a), b) for (a, b) in huff_tree.codes.items()]))
    # debug
    write_header(filename, huff_tree)
    with open('{}.comp'.format(filename), "ab") as out:
        out.write(encoded_file)

    compression_ratio = len(encoded_file)/len(file_content)

    return compression_ratio, huff_tree.codes


def decode(strn, code_dict):
    huff_tree = HuffmanTree.from_codes(code_dict)
    result = ''
    current_node = huff_tree.root
    strn = strn + 'e'  # a hack to indicate end of line
    for i in strn:
        if current_node.node_type == 'leaf' or i == 'e':
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
    file_content = "".join([to_byte_str(b) for b in read_from_file(append_comp_suffix(filename), mode="rb", start=last)])

    print(decode(file_content, codes))


cr,d = compress('HuffmanCompression/test.test')
decompress('HuffmanCompression/test.test')
