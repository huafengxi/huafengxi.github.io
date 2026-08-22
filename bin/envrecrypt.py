#!/usr/bin/env python3
"""envrecrypt.py — re-encrypt all tracked enc1: files under a new derived key.

Flow (all steps in one run):
  a. discover tracked files containing real enc1: ciphers (`git grep -l`)
  b. decrypt each file with the CURRENT key (bin/envdec.py) -> plaintext
     baseline written to --baseline-dir
  c. derive the new key from the password (same PBKDF2 scheme as
     enckey-gen.py) and overwrite bin/.encdec.key
  d. re-encrypt every enc1: value/line under the new key, preserving the
     original line format (KEY=enc1:... / whole-line enc1:...)
  e. verify: envdec-decrypting each rewritten file must byte-match the
     baseline from step b

Password input (never argv): --password-file PATH, ENDEC_PASSWORD env var,
or interactive getpass.

Usage:
  envrecrypt.py [--baseline-dir DIR] [--password-file PATH] [--files F ...]
"""
import argparse
import os
import re
import subprocess
import sys
import tempfile

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
REPO_ROOT = os.path.dirname(SCRIPT_DIR)
ENDEC = os.path.join(SCRIPT_DIR, "endec.py")
ENVDEC = os.path.join(SCRIPT_DIR, "envdec.py")
KEY_PATH = os.path.join(SCRIPT_DIR, ".encdec.key")
PREFIX = "enc1:"

import importlib.util  # noqa: E402

_spec = importlib.util.spec_from_file_location(
    "enckey_gen", os.path.join(SCRIPT_DIR, "enckey-gen.py"))
_mod = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_mod)
derive_key = _mod.derive_key

KV_RE = re.compile(r"^(\s*(?:export\s+)?[A-Za-z_]\w*\s*=\s*)(.*)$")
# docstrings/docs/source files merely *describe* the format; never recrypt them
SKIP_SUFFIXES = (".py", ".md", ".sh", ".yml", ".yaml", ".json", ".toml")


def enc1_forms(line):
    if line.startswith(PREFIX):
        return "whole", "", line[len(PREFIX):]
    m = KV_RE.match(line)
    if m:
        val = m.group(2)
        quoted = len(val) >= 2 and val[0] == val[-1] and val[0] in ('"', "'")
        inner = val[1:-1] if quoted else val
        if inner.startswith(PREFIX):
            q = val[0] if quoted else ""
            return "kv", m.group(1) + q, inner[len(PREFIX):]
    return None


def run(cmd, inp=None):
    r = subprocess.run(cmd, input=inp, capture_output=True, text=True, check=True)
    return r.stdout


def discover_files():
    out = run(["git", "-C", REPO_ROOT, "grep", "-l", "enc1:"]).split()
    files = []
    for rel in out:
        if rel.startswith("bin/") or rel.endswith(SKIP_SUFFIXES):
            continue
        path = os.path.join(REPO_ROOT, rel)
        if not os.path.isfile(path):
            continue
        with open(path) as fh:
            if any(enc1_forms(l) for l in fh.read().splitlines()):
                files.append(rel)
    return sorted(files)


def main():
    ap = argparse.ArgumentParser(description="Re-encrypt enc1: files under a new derived key")
    ap.add_argument("--baseline-dir", default=None,
                    help="dir for plaintext baseline (default: mkdtemp)")
    ap.add_argument("--password-file", default=None)
    ap.add_argument("--files", nargs="*", default=None)
    ap.add_argument("--verify-only", action="store_true",
                    help="skip key rotation; just diff current decryptions against --baseline-dir")
    args = ap.parse_args()

    if args.verify_only:
        if not args.baseline_dir:
            sys.exit("--verify-only requires --baseline-dir")
        files = args.files or discover_files()
        sys.exit(verify(files, args.baseline_dir))

    if args.password_file:
        pw = open(args.password_file).read()
    elif os.environ.get("ENDEC_PASSWORD"):
        pw = os.environ["ENDEC_PASSWORD"]
    else:
        import getpass
        pw = getpass.getpass("new endec derivation password: ")
    if pw.endswith("\n"):
        pw = pw[:-1]
    if not pw:
        sys.exit("empty password")

    files = args.files or discover_files()
    if not files:
        sys.exit("no enc1: files found")
    print("files to recrypt: %s" % ", ".join(files))

    bdir = args.baseline_dir or tempfile.mkdtemp(prefix="envrecrypt-baseline-")
    os.makedirs(bdir, exist_ok=True)

    # --- step a: plaintext baseline with the CURRENT key ---
    entries = []  # (rel, lineno, form, prefix, cipher)
    for rel in files:
        path = os.path.join(REPO_ROOT, rel)
        plain = run([sys.executable, ENVDEC, path])
        bpath = os.path.join(bdir, rel.replace("/", "__"))
        with open(bpath, "w") as fh:
            fh.write(plain)
        with open(path) as fh:
            for i, line in enumerate(fh.read().splitlines()):
                f = enc1_forms(line)
                if f:
                    entries.append((rel, i, f[0], f[1], f[2]))
    print("baseline written to %s (%d enc1: entries)" % (bdir, len(entries)))

    # --- decrypt all ciphers under the OLD key (still in place) ---
    plains = [run([sys.executable, ENDEC, cipher]) for (_, _, _, _, cipher) in entries]

    # --- step b: derive new key and overwrite ---
    key = derive_key(pw)
    fd = os.open(KEY_PATH, os.O_WRONLY | os.O_CREAT | os.O_TRUNC, 0o600)
    with os.fdopen(fd, "w") as fh:
        fh.write(key + "\n")
    os.chmod(KEY_PATH, 0o600)
    print("new password-derived key installed at %s" % KEY_PATH)

    # --- step c: re-encrypt under the NEW key, rewrite files ---
    new_ciphers = [run([sys.executable, ENDEC, p]) for p in plains]
    by_file = {}
    for (rel, lineno, form, prefix, _), cipher in zip(entries, new_ciphers):
        by_file.setdefault(rel, {})[lineno] = prefix + PREFIX + cipher
    for rel in files:
        path = os.path.join(REPO_ROOT, rel)
        with open(path) as fh:
            text = fh.read()
        nl = "\n" if text.endswith("\n") else ""
        lines = text.splitlines()
        for lineno, newline in by_file[rel].items():
            lines[lineno] = newline
        with open(path, "w") as fh:
            fh.write("\n".join(lines) + nl)
    print("rewrote %d files" % len(files))

    # --- step d: loop verification ---
    sys.exit(verify(files, bdir))


def verify(files, bdir):
    ok = True
    for rel in files:
        path = os.path.join(REPO_ROOT, rel)
        bpath = os.path.join(bdir, rel.replace("/", "__"))
        new_plain = run([sys.executable, ENVDEC, path])
        base = open(bpath).read()
        if new_plain == base:
            print("VERIFY OK   %s" % rel)
        else:
            ok = False
            print("VERIFY FAIL  %s" % rel)
            sys.stderr.write("--- baseline vs new-decrypt diff (%s) ---\n" % rel)
            import difflib
            sys.stderr.writelines(difflib.unified_diff(
                base.splitlines(True), new_plain.splitlines(True), "baseline", "new"))
    return 0 if ok else 1


if __name__ == "__main__":
    main()
