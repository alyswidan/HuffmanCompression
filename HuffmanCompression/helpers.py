from collections import Counter
from HuffmanCompression.HuffmanTree import *

def read_from_file(filename, chunksize=8192, mode="rb", start=0):
    with open(filename, mode) as file:
        file.seek(start)
        while True:
            chunk = file.read(chunksize)
            if chunk and len(chunk) != 0:
                for b in chunk:
                    yield b
            else:
                break


def write_header(filename, huff_tree):
    """

    :param filename: the file to be encoded
    :param huff_tree: the huffman tree used to generate codes for the given file
    :return: writes the 'code to original file mapping' into a file with the same name
             as the input file but with .comp suffix appended

    every thing writen to the file as a byte has to be converted to byte using the bytes()
    builtin function
    """

    with open(append_comp_suffix(filename), 'wb') as file:
        num_codes = len(huff_tree)
        for i, node in enumerate(huff_tree.elements()):
            file.write(bytes([node.value]))
            file.write(bytes(node.code,'ascii'))
            if i < num_codes - 1:
                file.write(bytes('.', 'ascii'))
        file.write(bytes('_.','ascii'))  # terminate header with _. this can't occur in actual header


def pack_bits(filename,code_dict):
    """

    :param filename: name of the file to be encoded
    :param code_dict: the codes lookup table generated by the huffman tree
    :return: returns the encoded bytes of the file as packed into bytes
             by concatenating the codes after appending zeroes to make the
             string length divisible by 8
    """
    file_content = [b for b in read_from_file(filename, mode="rb")]
    file_codes = ''.join([code_dict[val] for val in file_content])
    size = len(file_codes)
    remaining = 8 - (size % 8)
    file_codes = file_codes + '0'*(remaining if remaining != 8 else 0)
    size = len(file_codes)
    x = [int(file_codes[i:i+8],2) for i in range(0,size,8)]
    for i in x:
        yield i


def to_byte_str(num):
    return '{:08b}'.format(num)


def append_comp_suffix(filename):
    return '{}.comp'.format(filename)


def remove_decomp_suffix(filename):
    arr = filename.split('.')
    return '.'.join(arr[0:len(arr)-1])


def dict_from_header(filename=""):

    """
    This function reads the header containing the code to byte value mappingg from the file
    and interprets it as a byte value to code dict
    :param filename: name of the file containing the header contatining the mapping
    :return: code to byte value dict as well as the position in the file where the header ended (idx)
    """
    code_dict = {}
    idx = 0
    prev = None
    key = None
    code = ''

    for c in read_from_file(filename, mode="rb"):
        idx += 1
        if c == ord('.') and prev != ord('.'):  # .. means separator followed by code of character '.'
            if key is not None:
                code_dict[key] = code
                key = None
                code = ''
            if prev == ord('_'):
                break

        elif key is None:
            key = c
        elif c in [48, 49]: # ascii value of 0 and 1 respictively
            code += chr(c)
        prev = c

    return idx, code_dict


def compress(filename=""):
    file_content = [b for b in read_from_file(filename, mode="rb")]
    byte_freq = Counter(file_content)

    huff_tree = HuffmanTree.from_frequencies(byte_freq)
    before = [x for x in pack_bits(filename, huff_tree.codes)]
    encoded_file = bytes(before)

    write_header(filename, huff_tree)
    with open(append_comp_suffix(filename), "ab") as out:
        out.write(encoded_file)

    compression_ratio = len(encoded_file)/len(file_content)

    return compression_ratio, huff_tree.codes


def decode(strn, code_dict):

    """
    It works by traversing the huffman tree starting at the root going left or right based
    on a one or zero is encountered until it reaches a leaf which contains the original value of
    the byte, it then restarts at the root and repeats the same procedure

    :param strn: the contents of the encoded file concatenated into a string
    :param code_dict: the byte value to code dict
    :return: the original contents of the file before encoding
    """
    huff_tree = HuffmanTree.from_codes(code_dict)
    result = ''
    current_node = huff_tree.root
    strn = strn + 'e'  # a hack to indicate end of line
    for i in strn:
        if current_node.node_type == 'leaf':
            result += chr(current_node.value)
            current_node = huff_tree.root
        if i == '0':
            current_node = current_node.left
        elif i == '1':
            current_node = current_node.right

    return result


def decompress(filename="",destination="."):
    last, codes = dict_from_header(filename)

    file_content = "".join([to_byte_str(b) for b in read_from_file(filename, mode="rb", start=last)])
    with open('{0}/{1}.decomp'.format(destination,remove_decomp_suffix(filename)), 'wb+') as file:
        file.write(bytes([ord(x) for x in decode(file_content, codes)]))
    return codes
