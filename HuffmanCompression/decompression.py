from HuffmanCompression.Helpers.general_helpers import *
from HuffmanCompression.Helpers.decompression_helpers import *


def decompress_dir(dir_path):

    # split on / and get the last element
    # then split the last element on . and get all but the last word ie. .comp
    # join the resulting array using . again to obtain dir name without .comp
    dir_name = '.'.join(dir_path.split('/')[-1].split('.')[:-1])
    decompressed_dir_path = os.path.join(get_parent_dir(dir_path), dir_name)

    clone_dir(dir_path, decompressed_dir_path)
    decompress_recursively(decompressed_dir_path)


def decompress_recursively(dir_path):
    directory = os.fsencode(dir_path)
    print('exploring: ', dir_path)

    for file in os.listdir(directory):
        filename = os.fsdecode(file)
        file_path = os.path.join(dir_path,filename)
        print('current file: ',file_path)
        if os.path.isdir(os.fsencode(file_path)):
            print('file is a dir')
            decompress_recursively(file_path)
        elif os.path.isfile(file_path):
            print('file is a normal file in dir ',dir_path,filename)
            decompress(file_path)
            os.remove(file_path)


def decompress(file_path=""):
    last, codes = dict_from_header(file_path)
    file_content = "".join([to_byte_str(b) for b in read_from_file(file_path, mode="rb", start=last)])
    with open(remove_comp_suffix(file_path), 'wb+') as file:
        file.write(bytes([ord(x) for x in decode(file_content, codes)]))
    return codes
