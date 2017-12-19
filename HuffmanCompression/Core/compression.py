from collections import Counter

from HuffmanCompression.DataStructures.HuffmanTree import HuffmanTree
from HuffmanCompression.Helpers.compression_helpers import *
from HuffmanCompression.Helpers.general_helpers import *


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

    """
    This compresses the directory by first cloning the directory tree of the original directory
    it then recursively compresses each file in the tree and then removes the original file
    resulting in a directory tree equivalent to the original one but with each file replaced
    by its compressed version.

    :param dir_path: path to the directory to be compressed
    :return:
    """
    def compress_and_remove(file_path):
        """
        compress the file then remove it
        :param file_path: path to the file to be compressed within the directory tree
        :return:
        """
        compress(file_path)
        os.remove(file_path)

    dir_name = dir_path.split('/')[-1]
    compressed_dir_path = os.path.join(get_parent_dir(dir_path), dir_name) + '.comp'
    clone_dir(dir_path, compressed_dir_path)
    walk_dir(compressed_dir_path,compress_and_remove)


