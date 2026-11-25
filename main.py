#!/usr/bin/env python3
"""Write the coined word and its one-line definition to entry.txt.

Stdlib only, deterministic. The entry is one line of at most 140
characters: the new word "sorreflex" plus its definition. The program
validates the entry's full structure (word token, single em-dash
separator, definition shape), resolves the output directory
defensively, sweeps stale temp files, writes via a temp file in the
output directory, fsyncs, chmods 0644, then atomically replaces
entry.txt, fsyncs the directory, and finally verifies the published
file (byte content, SHA-256, size, mode 0644, no stray temp files, and
entry.txt as the only file in the directory), so a short write, a
wrong file, or a leftover temp file can never pass silently. Only the
contents of the output directory are cleared, never the directory
itself, so the program is safe when the output path is a mount point.
"""

import hashlib
import os
import shutil
import tempfile

LINE = "sorreflex \u2014 apologizing when someone else bumps into you, even though it was entirely their fault."

WORD = "sorreflex"
SEPARATOR = " \u2014 "  # space, U+2014 EM DASH, space

TMP_PREFIX = ".entry-"
TMP_SUFFIX = ".tmp"
OUTPUT_NAME = "entry.txt"
DEFAULT_OUT_DIR = "/output"

# Directories that must never be cleared, even if requested: clearing
# them would destroy the system or the user's home.
FORBIDDEN_DIRS = ("/", os.path.expanduser("~"))


def _validate(text: str) -> None:
    """Gate validation: the entry must be exactly one line, 1-140
    characters, shaped as "<word> <em dash> <definition>." """
    assert isinstance(text, str)
    assert text.strip(), "entry is only whitespace"
    assert text == text.strip(), "entry has leading or trailing whitespace"
    assert "\n" not in text and "\r" not in text, "entry must be one line"
    assert "\t" not in text, "entry must not contain tabs"
    assert 1 <= len(text) <= 140, f"length {len(text)} outside 1-140"
    assert text.endswith("."), "entry must end in '.'"
    assert text.count(SEPARATOR) == 1, "entry must contain exactly one em-dash separator"
    word, definition = text.split(SEPARATOR)
    assert word == WORD, f"word token is {word!r}, expected {WORD!r}"
    assert word.isascii() and word.isalpha() and word.islower(), (
        "word must be lowercase ASCII letters only"
    )
    assert 3 <= len(word) <= 20, f"word length {len(word)} outside 3-20"
    assert definition, "definition is empty"
    assert definition[0].islower(), "definition must start lowercase"
    assert "  " not in definition, "definition must not contain double spaces"
    assert not any(ord(ch) < 0x20 for ch in text), "entry must not contain control characters"
    assert definition.count(".") == 1, "definition must contain exactly one period (the final one)"
    text.encode("utf-8")


def _resolve_output_dir() -> str:
    """Resolve MAKEFUN_OUTPUT_DIR defensively.

    An empty value falls back to the default. A path that exists as a
    file, or that resolves (through symlinks) to a forbidden directory
    such as the filesystem root or the user's home, is refused: the
    program clears the directory's contents, so pointing it at "/"
    would be catastrophic.
    """
    raw = os.environ.get("MAKEFUN_OUTPUT_DIR", "")
    out_dir = raw.strip() or DEFAULT_OUT_DIR
    real = os.path.realpath(out_dir)
    if real in (os.path.realpath(p) for p in FORBIDDEN_DIRS):
        raise ValueError(f"refusing to use forbidden output directory {out_dir!r}")
    if os.path.exists(out_dir) and not os.path.isdir(out_dir):
        raise ValueError(f"output path {out_dir!r} exists and is not a directory")
    os.makedirs(out_dir, exist_ok=True)
    if not os.path.isdir(out_dir):
        raise ValueError(f"output path {out_dir!r} is not a directory after makedirs")
    return out_dir


def _clear_contents(out_dir: str) -> None:
    """Remove the contents of out_dir, never out_dir itself."""
    for name in os.listdir(out_dir):
        path = os.path.join(out_dir, name)
        if os.path.islink(path) or os.path.isfile(path):
            os.unlink(path)
        elif os.path.isdir(path):
            shutil.rmtree(path)
        else:
            # Sockets, FIFOs, devices: unlink, never follow.
            os.unlink(path)


def _sweep_stale_tmp(out_dir: str) -> list:
    """Remove leftover temp files from an interrupted earlier run and
    return their names, so a crashed run can never leave debris that a
    later run mistakes for output. Only our own prefix is swept."""
    swept = []
    for name in os.listdir(out_dir):
        if name.startswith(TMP_PREFIX) and name.endswith(TMP_SUFFIX):
            os.unlink(os.path.join(out_dir, name))
            swept.append(name)
    return swept


def _fsync_dir(path: str) -> None:
    fd = os.open(path, os.O_RDONLY)
    try:
        os.fsync(fd)
    finally:
        os.close(fd)


def _verify_published(out_dir: str, target: str, expected: bytes) -> None:
    """Post-publish verification: the published file must be a regular
    file (not a symlink) whose bytes, size, SHA-256 and mode are
    exactly as expected, entry.txt must be the only file left in the
    output directory, and no temp file may remain. Any mismatch fails
    loudly instead of passing silently."""
    assert os.path.isfile(target) and not os.path.islink(target), (
        "entry.txt is missing or is a symlink"
    )
    st = os.stat(target)
    assert st.st_mode & 0o777 == 0o644, "entry.txt mode is not 0644"
    with open(target, "rb") as f:
        written = f.read()
    assert len(written) == len(expected), (
        f"short write: {len(written)} bytes on disk, expected {len(expected)}"
    )
    assert written == expected, "read-back mismatch"
    assert hashlib.sha256(written).hexdigest() == hashlib.sha256(expected).hexdigest(), (
        "SHA-256 mismatch"
    )
    leftovers = [n for n in os.listdir(out_dir)
                 if n.startswith(TMP_PREFIX) and n.endswith(TMP_SUFFIX)]
    assert not leftovers, f"stale temp files remain after publish: {leftovers}"
    contents = sorted(os.listdir(out_dir))
    assert contents == [OUTPUT_NAME], (
        f"output directory must contain only {OUTPUT_NAME}, found {contents}"
    )


def main() -> None:
    _validate(LINE)
    expected = LINE.encode("utf-8")
    out_dir = _resolve_output_dir()
    _clear_contents(out_dir)
    _sweep_stale_tmp(out_dir)
    target = os.path.join(out_dir, OUTPUT_NAME)
    fd, tmp = tempfile.mkstemp(dir=out_dir, prefix=TMP_PREFIX, suffix=TMP_SUFFIX)
    try:
        with os.fdopen(fd, "w", encoding="utf-8", newline="") as f:
            f.write(LINE)
            f.flush()
            os.fsync(f.fileno())
        os.chmod(tmp, 0o644)
        os.replace(tmp, target)
        os.chmod(target, 0o644)
        _fsync_dir(out_dir)
    except BaseException:
        try:
            os.unlink(tmp)
        except OSError:
            pass
        raise
    _verify_published(out_dir, target, expected)


if __name__ == "__main__":
    main()
