#!/data/data/com.termux/files/usr/bin/python

from pathlib import Path
from multiprocessing import get_context
import os
from dh import run_command


if __name__=="__main__":

    cwd =Path.cwd()
    for path in cwd.rglob("setup.py"):
        pardir=path.parent
        os.system(f"cd {str(pardir)}")
        os.chdir(str(pardir))
        cmd=f"python {str(path)} bdist_wheel"
        ret,_,_=run_command(cmd)
        if ret!=0:
            print("ok")
    for path in cwd.rglob("pyproject.toml"):
        pardir=path.parent
        distdir= pardir / "dist"
        whlfile=[p for p in pardir.rglob("*.whl")]
        if whlfile:
            continue
        os.system(f"cd {str(pardir)}")
        os.chdir(str(pardir))
        cmd=f"python -m build -w"
        ret,_,_=run_command(cmd)
        if not ret:
            print("ok")
            continue
    allwhl=[p for p in cwd.rglob("*.whl")]
    print(f"done {len(allwhl)} wheels crwated.")
