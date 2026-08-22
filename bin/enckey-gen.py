#!/usr/bin/env python3
"""enckey-gen.py — derive the endec char-substitution key from a password.

Deterministic derivation (same password always yields the same key):
  seed = hashlib.pbkdf2_hmac("sha256", password.encode(), b"endec-v1", 200000)
  rng  = random.Random(seed)
  char_map = shuffle of the 94 printable ASCII chars (0x21-0x7E)

The resulting 94-char permutation is written to bin/.encdec.key (chmod 600,
gitignored) — the key file consumed by endec.py. Never commit the key.

Password input (never taken from argv, to keep it out of process listings):
  --stdin        read password from stdin (no trailing-newline stripping issues:
                 the whole stdin blob minus a single trailing newline is used)
  (default)      interactive getpass prompt

Usage:
  enckey-gen.py [--stdin] [--stdout] [--key-out PATH]
    --stdout     print the derived key to stdout instead of writing the key file
    --key-out    target key file (default: bin/.encdec.key next to this script)

Interactive via make:  make env.keygen
"""
import argparse
import hashlib
import os
import random
import sys

SALT = b"endec-v1"
ITERATIONS = 200_000
CHARSET = "".join(chr(c) for c in range(0x21, 0x7F))  # 94 printable ASCII


def derive_key(password: str) -> str:
    seed = hashlib.pbkdf2_hmac("sha256", password.encode(), SALT, ITERATIONS)
    rng = random.Random(seed)
    chars = list(CHARSET)
    rng.shuffle(chars)
    return "".join(chars)


def main():
    ap = argparse.ArgumentParser(description="Derive endec key from a password")
    ap.add_argument("--stdin", action="store_true", help="read password from stdin")
    ap.add_argument("--stdout", action="store_true", help="print key instead of writing key file")
    ap.add_argument("--key-out", default=os.path.join(os.path.dirname(os.path.abspath(__file__)), ".encdec.key"),
                    help="key file to write (default: bin/.encdec.key)")
    args = ap.parse_args()

    if args.stdin:
        pw = sys.stdin.read()
        if pw.endswith("\n"):
            pw = pw[:-1]
    else:
        import getpass
        pw = getpass.getpass("endec derivation password: ")
    if not pw:
        sys.exit("empty password")

    key = derive_key(pw)

    if args.stdout:
        print(key)
        return

    fd = os.open(args.key_out, os.O_WRONLY | os.O_CREAT | os.O_TRUNC, 0o600)
    with os.fdopen(fd, "w") as fh:
        fh.write(key + "\n")
    os.chmod(args.key_out, 0o600)
    print("wrote %s (chmod 600)" % args.key_out)


if __name__ == "__main__":
    main()
