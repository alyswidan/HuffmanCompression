from HuffmanCompression.Helpers.general_helpers import *


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
            file.write(bytes(node.code, 'ascii'))
            if i < num_codes - 1:
                file.write(bytes('.', 'ascii'))
        file.write(bytes('_.', 'ascii'))  # terminate header with _. this can't occur in actual header


def pack_bits(filename, code_dict):
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
    file_codes = file_codes + '0' * (remaining if remaining != 8 else 0)
    size = len(file_codes)
    x = [int(file_codes[i:i + 8], 2) for i in range(0, size, 8)]
    for i in x:
        yield i