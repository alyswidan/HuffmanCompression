from HuffmanCompression.helpers import *
import sys

if len(sys.argv) != 3:
    print('illegal usage: use as HuffmanCompression [compress|decompress] filename')
    exit(1)
if sys.argv[1] == 'compress':
    compression_ratio, code_dict = compress(sys.argv[2])
    print('compression ratio = ', compression_ratio)
    print('codes = ', code_dict)

elif sys.argv[1] == 'decompress':
    decompress(sys.argv[2])
else:
    print('illegal option ',sys.argv[2])