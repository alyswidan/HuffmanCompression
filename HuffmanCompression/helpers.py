from collections import Counter
from HuffmanCompression.HuffmanTree import *

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
    with open(append_comp_suffix(filename), "ab") as out:
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
