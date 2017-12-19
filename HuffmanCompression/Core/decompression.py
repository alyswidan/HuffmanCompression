from HuffmanCompression.Helpers.general_helpers import *
from HuffmanCompression.Helpers.decompression_helpers import *


def decompress(file_path=""):
    last, codes = dict_from_header(file_path)
    file_content = "".join([to_byte_str(b) for b in read_from_file(file_path, mode="rb", start=last)])
    with open(remove_comp_suffix(file_path), 'wb+') as file:
        file.write(bytes([ord(x) for x in decode(file_content, codes)]))
    return codes


def decompress_dir(dir_path):
    """
    Decompresses a directory recursively
    :param dir_path: path of the directory to be compressed
    :return:
    """

    # split on / and get the last element
    # then split the last element on . and get all but the last word ie. .comp
    # join the resulting array using . again to obtain dir name without .comp
    dir_name = '.'.join(dir_path.split('/')[-1].split('.')[:-1])
    decompressed_dir_path = os.path.join(get_parent_dir(dir_path), dir_name)

    def decompress_and_remove(file_path):
        decompress(file_path)
        os.remove(file_path)

    clone_dir(dir_path, decompressed_dir_path)
    walk_dir(decompressed_dir_path,decompress_and_remove)





