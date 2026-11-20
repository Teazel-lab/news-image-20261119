#!/usr/bin/env python3
"""Copy the pre-rendered entry.png to the output directory. No network, deterministic."""
import os
import shutil
import sys

HERE = os.path.dirname(os.path.abspath(__file__))


def main():
    src = os.path.join(HERE, "entry.png")
    out_dir = os.environ.get("MAKEFUN_OUTPUT_DIR") or "/output"
    if not os.path.isfile(src):
        sys.exit("entry.png not found next to main.py")
    os.makedirs(out_dir, exist_ok=True)
    dst = os.path.join(out_dir, "entry.png")
    shutil.copyfile(src, dst)
    print(dst)


if __name__ == "__main__":
    main()
