# macOS Icelandic-Nordic Dictionary Builder

Compiles the **ISLEX** dataset (Icelandic ↔ Danish / Norwegian Bokmål /
Norwegian Nynorsk / Swedish / Faroese / Finnish) into local Apple Dictionary
bundles, so lookup works system-wide via macOS "Look Up".

## Important License Context

ISLEX is distributed under **CC BY-NC-ND 4.0** (Non-Commercial, No
Derivatives) by Stofnun Árna Magnússonar í íslenskum fræðum via CLARIN
Iceland. That means:

- You should build locally for private, non-commercial, personal use only.
- You should **not** redistribute compiled `.dictionary` bundles.
- You should **not** publish converted/modified copies of the source data.
- Always keep attribution.

Because of the ND clause, **pre-compiled `.dictionary` files cannot be hosted
or shared from this repository.** This repo is build tooling only — you fetch
the source data and compile it yourself.

Read [LICENSE](LICENSE) for the full summary and links.

## What gets built

ISLEX itself is Icelandic-headword only (Icelandic → 6 target languages, no
reverse index in the source data). This project builds **14 bundles**: one
Icelandic-headword and one reverse target-language-headword dictionary for
each of the 6 target languages, plus 2 combined "all Nordic languages at
once" editions.

| Language | Icelandic → Language | Language → Icelandic |
|---|---|---|
| Danish | IcelandicDanish | DanishIcelandic |
| Norwegian Bokmål | IcelandicNorwegianBokmål | NorwegianBokmålIcelandic |
| Norwegian Nynorsk | IcelandicNorwegianNynorsk | NorwegianNynorskIcelandic |
| Swedish | IcelandicSwedish | SwedishIcelandic |
| Faroese | IcelandicFaroese | FaroeseIcelandic |
| Finnish | IcelandicFinnish | FinnishIcelandic |
| **All 6 combined** | **IcelandicNordic** | **NordicIcelandic** |

**IcelandicNordic** keys entries by Icelandic headword and groups the
translations from all 6 target languages together under one entry (e.g.
looking up "hestur" shows Danish/Norwegian/Swedish/Faroese/Finnish side by
side, plus its BÍN declension table). **NordicIcelandic** merges the reverse
index across all 6 target languages into one lookup — e.g. "hus" shows every
Icelandic word it could mean, each tagged with which source language(s)
contributed it (`[Danish, Norwegian Bokmål, Swedish]`). Because it merges six
languages' worth of written forms, NordicIcelandic is the largest bundle by
far (~400K entries, ~320MB compiled) — expect it to take noticeably longer
to compile than the others.

The reverse (Language → Icelandic) bundles are built by inverting the
Icelandic-sourced data: every `writtenForm` in the target language becomes a
lookup entry pointing back to the Icelandic lemma(s) that translate to it.
Since ISLEX wasn't authored in that direction, coverage/granularity there is
necessarily coarser than the forward direction — this is documented and not
a limitation of the build script.

Every Icelandic-headword (`is2x`) entry that's a noun, verb, or adjective is
additionally enriched with a full **BÍN inflection table** (declensions for
nouns/adjectives, principal parts for verbs), and every inflected form is
indexed — so looking up e.g. "hestinum" resolves straight to "hestur". This
reuses the same `islenska`/BÍN approach as the companion
`icelandic-dictionary-mac` project. Reverse-direction (`x2is`) entries don't
get paradigm tables, since the headword there is a Danish/Swedish/etc. word,
not Icelandic.

## Project Structure

- `scripts/parse_islex.py`: Parses the ISLEX LMF-XML into a flat structure
  (lemma, part of speech, gender, equivalents per language, idioms, examples).
- `scripts/bin_morphology.py`: BÍN-powered inflection table renderer (ported
  from `icelandic-dictionary-mac`) — verb principal parts, noun declensions,
  adjective declensions.
- `scripts/build_dict.py`: Generates Apple Dictionary XML + plist for one or
  all (language, direction) combinations; enriches Icelandic-headword entries
  with BÍN paradigms unless `--no-morphology` is passed.
- `scripts/install_dictionary.sh`: One-command build + install for new users.
- `data/ISLEX_dictionary_2023-12.xml`: Source data you download (gitignored).
- `data/islex_parsed.json`: Cached parse output (gitignored, regenerate any
  time by deleting it).
- `data/bin_paradigms_cache.json`: Cached BÍN lookups keyed by lemma+POS
  (gitignored) — avoids re-querying BÍN for the same Icelandic word across
  multiple target-language builds.
- `src/shared/Nordic.css`: Shared stylesheet used by every bundle.
- `src/generated/`: Build output — per-bundle XML + plist (gitignored).
- `src/objects/`: Compiled `.dictionary` bundles (gitignored).
- `Makefile`: Builds/installs every bundle listed in `src/generated/bundles.txt`.

## Prerequisites

1. macOS with Xcode Additional Tools installed.
2. DictionaryDevelopmentKit available at:
   `/Applications/XcodeAdditionalTools/Utilities/DictionaryDevelopmentKit`
3. Python 3 with the `islenska` package (for BÍN morphology):
   ```bash
   python3 -m venv .venv
   source .venv/bin/activate
   pip install islenska
   ```
   Not required if you build with `--no-morphology`.

### Important: Remove Spaces From The Xcode Tools Folder Name

```bash
sudo mv "/Applications/Additional Tools for Xcode" "/Applications/XcodeAdditionalTools"
```

## Getting the source data

1. Download `ISLEX_dictionary_2023-12.xml.zip` from CLARIN Iceland:
   https://repository.clarin.is/repository/xmlui/handle/20.500.12537/319
2. Unzip it so that `data/ISLEX_dictionary_2023-12.xml` exists in this repo.
   (This directory is gitignored — the file stays local to your machine.)

## Build

Build everything (all 6 per-language bundles + the 2 combined editions, 14 total):

```bash
python3 scripts/build_dict.py --all
```

Or build a single pair, e.g. just Icelandic→Danish:

```bash
python3 scripts/build_dict.py --lang dan --direction is2x
```

Or just the combined edition:

```bash
python3 scripts/build_dict.py --lang all --direction is2x   # IcelandicNordic
python3 scripts/build_dict.py --lang all --direction x2is   # NordicIcelandic
```

`--direction is2x` = Icelandic headword; `--direction x2is` = target-language
headword.

## Install into Dictionary.app

Beginner one-command path (builds + installs all 14):

```bash
./scripts/install_dictionary.sh
```

Manual path:

```bash
python3 scripts/build_dict.py --all
make install
```

This compiles and copies every `.dictionary` bundle listed in
`src/generated/bundles.txt` into `~/Library/Dictionaries/`.

Then:
1. Open Dictionary.app.
2. Open Settings.
3. Enable whichever language pairs you want.
4. Restart Dictionary.app if it was already open.

### Troubleshooting: "unable to parse objects/dict.plist" mid-build

Apple's `build_dict.sh` fetches `PropertyList-1.0.dtd` from apple.com on every
invocation. A transient network hiccup during a long `make install` run (14
bundles, one of them ~400K entries) can truncate that fetch and abort the
build partway through with a DTD parse error — it's not a problem with this
project's plist files. Just re-run `make install`; it doesn't track partial
progress, so it rebuilds all 14 bundles again from scratch, which is safe
but takes the full time again.

## Update Workflow

When source data changes, delete the cache and rebuild:

```bash
rm data/islex_parsed.json
python3 scripts/build_dict.py --all
make install
```

## Scope Notes

- BÍN inflection tables only cover the Icelandic-headword (`is2x`) direction.
  Reverse (`x2is`) entries show translations only, no paradigm — the headword
  there isn't Icelandic, so BÍN doesn't apply.
- English is intentionally out of scope for this project — see the separate
  effort to build Icelandic↔English from Wiktionary/Kaikki data instead of
  ND-licensed sources.

## Attribution

- Lexical source data: Stofnun Árna Magnússonar í íslenskum fræðum, via
  CLARIN Iceland.
- Build/integration tooling in this repository: Jónatan Sólon and contributors.

See [CREDITS.md](CREDITS.md) for full attribution.

## Release Assets Policy

- Do not upload prebuilt `.dictionary` bundles or the ISLEX XML to GitHub
  Releases — ND terms forbid it.
- Only build scripts and documentation may be published/distributed.
