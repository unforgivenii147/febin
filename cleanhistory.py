#!/data/data/com.termux/files/usr/bin/python
if __name__ == "__main__":
    fn = "/data/data/com.termux/files/home/.bash_history"
    nl = []
    with open(fn, encoding="utf-8") as f:
        nl.extend(line for line in f if 'cd "`printf' not in line)
    with open(fn, "w", encoding="utf-8") as fo:
        fo.writelines(nl)
    print("done.")
