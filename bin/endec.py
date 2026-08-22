#!/usr/bin/env python3
"""Reflective cipher: same call encrypts and decrypts.

Key file search order (first match wins):
  1. R/scripts/.encdec.key (beside this script)
  2. repo-root/.encdec.key (legacy location)

Input is taken from argv[1] when provided, otherwise from stdin."""
import os
import sys


def find_encdec_key():
    script_dir = os.path.dirname(os.path.abspath(__file__))
    repo_root = os.path.dirname(os.path.dirname(script_dir))
    for candidate in (
        os.path.join(script_dir, ".encdec.key"),
        os.path.join(repo_root, ".encdec.key"),
    ):
        path = os.path.realpath(candidate)
        if os.path.isfile(path):
            return path
    sys.exit(
        ".encdec.key not found — place it at R/scripts/.encdec.key or repo root"
    )


def fuzz_str(f):
    def translate_char(x):
        i = char_map.find(x)
        return char_map[i ^ 1] if i >= 0 else x

    return "".join(map(translate_char, f))


with open(find_encdec_key()) as kf:
    char_map = kf.read().rstrip("\n")
text = sys.argv[1] if len(sys.argv) > 1 else sys.stdin.read()
print("%s" % (fuzz_str(text)), end="")
