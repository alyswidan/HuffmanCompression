from HuffmanCompression.DataStructures.HuffmanTree import HuffmanTree
from HuffmanCompression.Helpers.general_helpers import read_from_file


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
        elif c in [48, 49]:  # ascii value of 0 and 1 respictively
            code += chr(c)
        prev = c

    return idx, code_dict

