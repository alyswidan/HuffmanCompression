from collections import Counter

from HuffmanCompression.Helpers.compression_helpers import *
from HuffmanCompression.Helpers.general_helpers import *
from HuffmanCompression.HuffmanTree import HuffmanTree


def compress(file_path=""):
    file_content = [b for b in read_from_file(file_path, mode="rb")]
    byte_freq = Counter(file_content)

    huff_tree = HuffmanTree.from_frequencies(byte_freq)
    before = [x for x in pack_bits(file_path, huff_tree.codes)]
    encoded_file = bytes(before)

    write_header(file_path, huff_tree)
    with open(append_comp_suffix(file_path), "ab") as out:
        out.write(encoded_file)

    compression_ratio = len(encoded_file) / len(file_content)

    return compression_ratio, huff_tree.codes


def compress_dir(dir_path):

    dir_name = dir_path.split('/')[-1]
    compressed_dir_path = os.path.join(get_parent_dir(dir_path),dir_name) + '.comp'
    clone_dir(dir_path, compressed_dir_path)
    _compress_recursively(compressed_dir_path)


def _compress_recursively(dir_path):

    directory = os.fsencode(dir_path)
    print('exploring: ',dir_path)

    for file in os.listdir(directory):
        filename = os.fsdecode(file)
        file_path = os.path.join(dir_path,filename)
        print('current file: ',file_path)
        if os.path.isdir(os.fsencode(file_path)):
            print('file is a dir')
            _compress_recursively(file_path)
        elif os.path.isfile(file_path):
            print('file is a normal file')
            compress(file_path)
            os.remove(file_path)