# notes

quick notes from the terminal. python 3.10+, no deps.

```
python -m notes.cli add "call dentist" -t health
python -m notes.cli list
python -m notes.cli find dentist
python -m notes.cli rm 1
```

storage: one json file, `~/.notes.json` (override with env NOTES_FILE). see NOTES_dev.txt for why.

## changelog
- 0.3 rm returns exit 1 + message on unknown id (was traceback)
- 0.2 find got -t tag filter; tags dedup + sorted on add
- 0.1 add/list/find/rm
