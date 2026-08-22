#!/usr/bin/env python3
"""envdec.py — decrypt env files with enc1: inline-encrypted values.

Counterpart of endec.py (reflective char-substitution cipher; the key lives
at bin/.encdec.key and is NEVER committed). Decrypted output goes to stdout
only — never write it back into tracked files.

Formats recognised (everything else passes through unchanged):
  KEY=enc1:<cipher>         env-style line ('export ' prefix optional);
                            the value part is the encrypted secret
  enc1:<cipher>             whole-line encryption (ssh/kube config lines)

Usage:
  envdec.py FILE              print decrypted file content to stdout
  envdec.py --value CIPHER    decrypt a single enc1:-less cipher value
"""
import os
import re
import subprocess
import sys

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
ENDEC = os.path.join(SCRIPT_DIR, "endec.py")
PREFIX = "enc1:"

KV_RE = re.compile(r"^(\s*(?:export\s+)?[A-Za-z_]\w*\s*=\s*)(.*)$")
# chars safe to leave unquoted when re-emitting a decrypted value
SAFE_RE = re.compile(r"^[A-Za-z0-9@%+=:,./_-]*$")


def decrypt_value(cipher):
    """Decrypt one cipher string via endec.py (reflective => same call)."""
    r = subprocess.run(
        [sys.executable, ENDEC, cipher],
        capture_output=True,
        text=True,
        check=True,
    )
    return r.stdout


def decrypt_text(text):
    out = []
    for line in text.splitlines():
        if line.startswith(PREFIX):
            out.append(decrypt_value(line[len(PREFIX):]))
            continue
        m = KV_RE.match(line)
        if m:
            val = m.group(2)
            quoted = len(val) >= 2 and val[0] == val[-1] and val[0] in ('"', "'")
            inner = val[1:-1] if quoted else val
            if inner.startswith(PREFIX):
                plain = decrypt_value(inner[len(PREFIX):])
                if SAFE_RE.match(plain):
                    out.append(m.group(1) + plain)
                else:
                    out.append(m.group(1) + '"%s"' % plain)
                continue
        out.append(line)
    nl = "\n" if text.endswith("\n") else ""
    return "\n".join(out) + nl


def main():
    if len(sys.argv) == 3 and sys.argv[1] == "--value":
        sys.stdout.write(decrypt_value(sys.argv[2]))
        return
    if len(sys.argv) != 2:
        sys.exit(__doc__)
    with open(sys.argv[1]) as fh:
        sys.stdout.write(decrypt_text(fh.read()))


if __name__ == "__main__":
    main()
