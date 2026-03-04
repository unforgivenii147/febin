#!/data/data/com.termux/files/usr/bin/env python
if __name__ == "__main__":
    fn = "/data/data/com.termux/files/home/.bash_history"
    nl = []
    with open(fn, "r", encoding="utf-8") as f:
        for line in f:
            if not 'cd "`printf' in line:
                nl.append(line)
    with open(fn, "w") as fo:
        for k in nl:
            fo.write(k)
    print("done.")
