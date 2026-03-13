import os
from dh import read_lines


def process_file(fp):
    lines=read_lines(fp)
    nl=[]
    if lines[0].startswith('#!') and lines[1].startswith('#!'):
        nl=lines[0]+lines[2:]
        print(f'{fp} have 2 shebang')
    else:
        nl=lines
    with open(fp,'w') as f:
        for k in nl:
            f.write(k)

if __name__=='__main__':

    for k in os.listdir('.'):
        if k.endswith('.py'):
            process_file(k)
