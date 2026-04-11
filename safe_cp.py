#!/data/data/com.termux/files/usr/bin/python
from dh import cpf

if __name__ == "__main__":
    infile = sys.argv[1]
    outfile = sys.argv[2]
    cpf(infile, outfile)
