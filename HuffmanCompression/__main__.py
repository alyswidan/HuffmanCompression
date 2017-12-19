from HuffmanCompression.helpers import *
import sys
import time
if len(sys.argv) != 3:
    print('illegal usage: use as HuffmanCompression [compress|decompress] filename')
    exit(1)
if sys.argv[1] == 'compress':
    start = time.time()
    compression_ratio, code_dict = compress(sys.argv[2])
    end = time.time()
    print('compression time = ',end-start)
    print('compression ratio = ', compression_ratio)
    print('codes = ', code_dict)

elif sys.argv[1] == 'decompress':
    decompress(sys.argv[2])
elif sys.argv[1] == 'all':
    compression_ratio, code_dict = compress(sys.argv[2])
    print('done compressing')
    print(len(code_dict.keys()))
    header_dict = decompress(sys.argv[2]+'.comp')
    print('done decompressing')
    print(len(header_dict.keys()))
    for i in code_dict.keys():
        if i not in header_dict.keys():
            print('codes[{0}] = {1} not found'.format(i,code_dict[i]))
else:
    print('illegal option ', sys.argv[1])