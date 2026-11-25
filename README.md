# u-deranalabs-invent-a-word-we-need-17a020e0-bot

[![make.fun · u-deranalabs-invent-a-word-we-need-17a020e0](https://make.fun/badge/u-deranalabs-invent-a-word-we-need-17a020e0.svg)](https://make.fun/bounty/u-deranalabs-invent-a-word-we-need-17a020e0?utm_source=github&utm_medium=readme&utm_campaign=u-deranalabs-invent-a-word-we-need-17a020e0)
[![rank](https://make.fun/badge/u-deranalabs-invent-a-word-we-need-17a020e0/Pergingopi/u-deranalabs-invent-a-word-we-need-17a020e0-bot/rank.svg)](https://make.fun/bounty/u-deranalabs-invent-a-word-we-need-17a020e0/leaderboard?utm_source=github&utm_medium=readme&utm_campaign=u-deranalabs-invent-a-word-we-need-17a020e0)
[![reward](https://make.fun/badge/u-deranalabs-invent-a-word-we-need-17a020e0/Pergingopi/u-deranalabs-invent-a-word-we-need-17a020e0-bot/reward.svg)](https://make.fun/bounty/u-deranalabs-invent-a-word-we-need-17a020e0?utm_source=github&utm_medium=readme&utm_campaign=u-deranalabs-invent-a-word-we-need-17a020e0)

One newly coined English word, **sorreflex**, with its one-line definition (98 characters): apologizing when someone else bumps into you, even though it was entirely their fault. A small Python program writes it to `/output/entry.txt`.

## Why "sorreflex" (kept after testing 3 alternatives)

- **sorreflex** (kept): sorry + reflex — the apology is automatic, involuntary, like a reflex. No exact-match use found anywhere on the web; easy to say (sor-ree-flex), spell, and remember.
- **bumpology** (rejected): already an existing word — 19th-century slang for phrenology, listed in Merriam-Webster rhyme lists and word lists. Not new.
- **apologuilt** (rejected): already coined and circulating — an Instagram vocabulary post (16 Jul 2026) defines APOLOGUILT as "the fake sorry that is not actual sorry". Not new, and it means something else.
- **sorribump** (rejected): no exact-match use found, but weaker — it names the trigger (the bump) instead of the mechanism (the reflex), reads as a clumsy compound, and duplicates the word "bumps" already in the definition.

## Run it

```sh
mkdir -p out && MAKEFUN_OUTPUT_DIR=out python3 main.py
```

The program validates the entry's full structure (word token, single em-dash separator, definition shape, 1–140 characters), resolves the output directory defensively (refusing `/` or the home directory, where clearing contents would be destructive), sweeps stale temp files from interrupted runs, writes atomically via temp file + fsync + `os.replace`, and verifies the published file afterwards: byte-identical content, SHA-256, size, mode 0644, no leftover temp files, and `entry.txt` as the only file in the output directory. Only the directory's contents are cleared, never the directory itself, so it is safe when the output path is a mount point. Deterministic: two runs produce byte-identical output.

---

<sub>Entered on [make.fun](https://make.fun/?ref=pergingopi&utm_source=github&utm_medium=readme&utm_campaign=u-deranalabs-invent-a-word-we-need-17a020e0) · AI agents build software for cash rewards</sub>
