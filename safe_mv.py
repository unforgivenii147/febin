#!/data/data/com.termux/files/usr/bin/python
from dh import move_file
import sys

if __name__ == "__main__":
    infile = sys.argv[1]
    outfile = sys.argv[2]
    move_file(infile, outfile)
