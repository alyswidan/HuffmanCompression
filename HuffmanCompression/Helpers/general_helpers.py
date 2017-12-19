from distutils import dir_util
import os


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


def to_byte_str(num):
    return '{:08b}'.format(num)


def append_comp_suffix(filename):
    return '{}.comp'.format(filename)


def remove_comp_suffix(filename):
    split_name = filename.split('.')
    return '.'.join(split_name[:-1])


def get_parent_dir(dir_path):
    return dir_path.split('/')[-2]


def clone_dir(src,compressed_dir_path):
    """
    :param src: the path of the directory to be cloned
    :return:
    Clone the directory pointed at by src into a new directory with the same content
    but with the root having the original name (.comp)
    """
    os.makedirs(compressed_dir_path)
    dir_util.copy_tree(src, compressed_dir_path)

def walk_dir(root_str,action_at_leaf):
    """

    :param root_str: the path to the root of the directory
    :param action_at_leaf: a function to be executed at every file
    :return:
    """
    directory = os.fsencode(root_str)
    print('exploring: ', root_str)

    for file in os.listdir(directory):
        filename = os.fsdecode(file)
        file_path = os.path.join(root_str, filename)
        print('current file: ', file_path)
        if os.path.isdir(os.fsencode(file_path)):
            print('file is a dir')
            walk_dir(file_path,action_at_leaf)
        elif os.path.isfile(file_path):
            print('file is a normal file')
            action_at_leaf(file_path)