#!/usr/bin/env python3
"""Build Apple Dictionary source XML + plist bundles from ISLEX.

Generates, for each requested (target language, direction) pair, an
Apple-Dictionary-format XML file plus a matching .plist under
src/generated/. Direction "is2x" keys entries by the Icelandic headword
(showing target-language translations); "x2is" inverts that into a
target-language-headword index pointing back to Icelandic.

Usage:
    python scripts/build_dict.py --lang dan --direction is2x
    python scripts/build_dict.py --all
"""
import argparse
import html
import json
import os
import sys
from collections import defaultdict

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from parse_islex import TARGET_LANGS, parse_islex

SOURCE_XML = "data/ISLEX_dictionary_2023-12.xml"
CACHE_JSON = "data/islex_parsed.json"
BIN_CACHE_JSON = "data/bin_paradigms_cache.json"
OUT_DIR = "src/generated"

# ISLEX partOfSpeech values that BÍN can render a paradigm table for.
BIN_POS_MAP = {
    "noun": "no",
    "verb": "so",
    "adjective": "lo",
}

DISPLAY_NAMES = {
    ("dan", "is2x"): "Íslensk-dönsk orðabók (ISLEX)",
    ("dan", "x2is"): "Dönsk-íslensk orðabók (ISLEX)",
    ("nob", "is2x"): "Íslensk-norsk (bókmál) orðabók (ISLEX)",
    ("nob", "x2is"): "Norsk (bókmál)-íslensk orðabók (ISLEX)",
    ("nno", "is2x"): "Íslensk-norsk (nýnorska) orðabók (ISLEX)",
    ("nno", "x2is"): "Norsk (nýnorska)-íslensk orðabók (ISLEX)",
    ("swe", "is2x"): "Íslensk-sænsk orðabók (ISLEX)",
    ("swe", "x2is"): "Sænsk-íslensk orðabók (ISLEX)",
    ("fao", "is2x"): "Íslensk-færeysk orðabók (ISLEX)",
    ("fao", "x2is"): "Færeysk-íslensk orðabók (ISLEX)",
    ("fin", "is2x"): "Íslensk-finnsk orðabók (ISLEX)",
    ("fin", "x2is"): "Finnsk-íslensk orðabók (ISLEX)",
    ("all", "is2x"): "Íslensk-norræn orðabók (ISLEX)",
    ("all", "x2is"): "Norræn-íslensk orðabók (ISLEX)",
}

PLIST_TEMPLATE = """<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>CFBundleDevelopmentRegion</key>
    <string>{region}</string>
    <key>CFBundleIdentifier</key>
    <string>com.apple.dictionary.{bundle_id}</string>
    <key>CFBundleName</key>
    <string>{display_name}</string>
    <key>CFBundleDisplayName</key>
    <string>{display_name}</string>
    <key>CFBundleShortVersionString</key>
    <string>1.0</string>
    <key>DCSDictionaryCopyright</key>
    <string>Contains data from Stofnun Árna Magnússonar/CLARIN Iceland - ISLEX (CC BY-NC-ND 4.0). Personal, non-commercial use only. Do not redistribute this bundle or converted data.</string>
    <key>DCSDictionaryManufacturerName</key>
    <string>Jónatan Sólon and contributors</string>
    <key>DCSDictionaryFrontMatterWindowSize</key>
    <string>0.5</string>
</dict>
</plist>
"""


def ensure_bin_paradigms(entries):
    """Attach `paradigm_html`/`paradigm_forms` to each noun/verb/adjective entry
    by looking it up in BÍN via the `islenska` package. Results are cached by
    (lemma, pos_cat) in BIN_CACHE_JSON since the same Icelandic lemma is looked
    up once regardless of how many target languages are being built.

    Silently no-ops (leaving entries unenriched) if `islenska` isn't installed.
    """
    try:
        from islenska import Bin
    except ImportError:
        print("  [!] `islenska` not installed — skipping BÍN morphology (pip install islenska)")
        return entries

    import bin_morphology

    cache = {}
    if os.path.exists(BIN_CACHE_JSON):
        with open(BIN_CACHE_JSON, encoding="utf-8") as f:
            cache = json.load(f)

    b = Bin()
    dirty = False
    for e in entries:
        pos_cat = BIN_POS_MAP.get(e.get("pos", ""))
        if not pos_cat:
            continue
        key = f"{e['lemma']}|{pos_cat}"
        if key not in cache:
            paradigm_html, forms = bin_morphology.build_paradigm(b, e["lemma"], pos_cat)
            cache[key] = {"html": paradigm_html, "forms": sorted(forms)}
            dirty = True
        e["paradigm_html"] = cache[key]["html"]
        e["paradigm_forms"] = cache[key]["forms"]

    if dirty:
        os.makedirs(os.path.dirname(BIN_CACHE_JSON), exist_ok=True)
        with open(BIN_CACHE_JSON, "w", encoding="utf-8") as f:
            json.dump(cache, f, ensure_ascii=False)

    return entries


def load_entries():
    if os.path.exists(CACHE_JSON):
        with open(CACHE_JSON, encoding="utf-8") as f:
            return json.load(f)
    if not os.path.exists(SOURCE_XML):
        raise FileNotFoundError(
            f"Missing {SOURCE_XML}. Download ISLEX_dictionary_2023-12.xml.zip from "
            "https://repository.clarin.is/repository/xmlui/handle/20.500.12537/319 "
            "and unzip it into data/."
        )
    entries = parse_islex(SOURCE_XML)
    os.makedirs(os.path.dirname(CACHE_JSON), exist_ok=True)
    with open(CACHE_JSON, "w", encoding="utf-8") as f:
        json.dump(entries, f, ensure_ascii=False)
    return entries


def bundle_name(lang_code, direction):
    if lang_code == "all":
        return "IcelandicNordic" if direction == "is2x" else "NordicIcelandic"
    lang_name = TARGET_LANGS[lang_code].replace(" ", "").replace("(", "").replace(")", "")
    return f"Icelandic{lang_name}" if direction == "is2x" else f"{lang_name}Icelandic"


def render_entry(idx, headword, gram, items_html, extra_html="", extra_index_forms=None):
    gram_html = f" <span class='gram'>({html.escape(gram)})</span>" if gram else ""
    index_tags = f'<d:index d:value="{html.escape(headword)}"/>'
    for form in extra_index_forms or []:
        if form != headword:
            index_tags += f'<d:index d:value="{html.escape(form)}"/>'
    return f"""
    <d:entry id="entry_{idx}" d:title="{html.escape(headword)}">
        {index_tags}
        <h1>{html.escape(headword)}{gram_html}</h1>
        <ol class="translations">{items_html}</ol>
        {extra_html}
    </d:entry>
    """


def build_is_to_target(entries, lang_code, out_path):
    xml_out = [
        '<?xml version="1.0" encoding="UTF-8"?>',
        '<d:dictionary xmlns="http://www.w3.org/1999/xhtml" xmlns:d="http://www.apple.com/DTDs/DictionaryService-1.0.rng">',
    ]
    idx = 0
    for e in entries:
        forms = e["equivalents"].get(lang_code)
        if not forms:
            continue
        idx += 1
        gram = ", ".join(x for x in [e.get("pos", ""), e.get("gender", "")] if x)
        items_html = "".join(f"<li>{html.escape(f)}</li>" for f in forms)
        examples_html = ""
        if e.get("examples"):
            ex_items = "".join(f"<li>{html.escape(ex)}</li>" for ex in e["examples"])
            examples_html = f'<details class="examples"><summary>Dæmi</summary><ul>{ex_items}</ul></details>'
        idioms_html = ""
        idiom_forms = [i for i in e.get("idioms", []) if i["equivalents"].get(lang_code)]
        if idiom_forms:
            idiom_items = "".join(
                f"<li><b>{html.escape(i['phrase'])}</b>: {html.escape(', '.join(i['equivalents'][lang_code]))}</li>"
                for i in idiom_forms
            )
            idioms_html = f'<details class="idioms"><summary>Orðasambönd</summary><ul>{idiom_items}</ul></details>'
        paradigm_html = e.get("paradigm_html", "")
        xml_out.append(
            render_entry(
                idx, e["lemma"], gram, items_html,
                examples_html + idioms_html + paradigm_html,
                extra_index_forms=e.get("paradigm_forms"),
            )
        )
    xml_out.append("</d:dictionary>")
    _write(out_path, xml_out)
    return idx


def build_target_to_is(entries, lang_code, out_path):
    reverse = defaultdict(list)
    for e in entries:
        forms = e["equivalents"].get(lang_code)
        if not forms:
            continue
        for form in forms:
            reverse[form].append(e)

    xml_out = [
        '<?xml version="1.0" encoding="UTF-8"?>',
        '<d:dictionary xmlns="http://www.w3.org/1999/xhtml" xmlns:d="http://www.apple.com/DTDs/DictionaryService-1.0.rng">',
    ]
    idx = 0
    for headword in sorted(reverse.keys(), key=str.lower):
        idx += 1
        items_html = "".join(
            "<li>{lemma}{gram}</li>".format(
                lemma=html.escape(e["lemma"]),
                gram=(
                    " <span class='gram'>(" + html.escape(", ".join(x for x in [e.get("pos", ""), e.get("gender", "")] if x)) + ")</span>"
                    if e.get("pos") or e.get("gender")
                    else ""
                ),
            )
            for e in reverse[headword]
        )
        xml_out.append(render_entry(idx, headword, "", items_html))
    xml_out.append("</d:dictionary>")
    _write(out_path, xml_out)
    return idx


def build_is_to_all(entries, out_path):
    """Combined 'IcelandicNordic' edition: one Icelandic-headword entry per
    word, with translations grouped by target language underneath."""
    xml_out = [
        '<?xml version="1.0" encoding="UTF-8"?>',
        '<d:dictionary xmlns="http://www.w3.org/1999/xhtml" xmlns:d="http://www.apple.com/DTDs/DictionaryService-1.0.rng">',
    ]
    idx = 0
    for e in entries:
        if not e.get("equivalents"):
            continue
        idx += 1
        gram = ", ".join(x for x in [e.get("pos", ""), e.get("gender", "")] if x)
        gram_html = f" <span class='gram'>({html.escape(gram)})</span>" if gram else ""

        lang_blocks = []
        for lang_code, lang_name in TARGET_LANGS.items():
            forms = e["equivalents"].get(lang_code)
            if not forms:
                continue
            items = "".join(f"<li>{html.escape(f)}</li>" for f in forms)
            lang_blocks.append(f"<div class='lang-block'><h4>{html.escape(lang_name)}</h4><ul>{items}</ul></div>")
        translations_html = f"<div class='lang-grid'>{''.join(lang_blocks)}</div>"

        examples_html = ""
        if e.get("examples"):
            ex_items = "".join(f"<li>{html.escape(ex)}</li>" for ex in e["examples"])
            examples_html = f'<details class="examples"><summary>Dæmi</summary><ul>{ex_items}</ul></details>'

        idioms_html = ""
        idiom_blocks = []
        for idiom in e.get("idioms", []):
            lang_lines = [
                f"<b>{html.escape(lang_name)}:</b> {html.escape(', '.join(idiom['equivalents'][lang_code]))}"
                for lang_code, lang_name in TARGET_LANGS.items()
                if idiom["equivalents"].get(lang_code)
            ]
            if lang_lines:
                idiom_blocks.append(f"<li><b>{html.escape(idiom['phrase'])}</b><br/>{'<br/>'.join(lang_lines)}</li>")
        if idiom_blocks:
            idioms_html = f'<details class="idioms"><summary>Orðasambönd</summary><ul>{"".join(idiom_blocks)}</ul></details>'

        paradigm_html = e.get("paradigm_html", "")
        index_tags = f'<d:index d:value="{html.escape(e["lemma"])}"/>'
        for form in e.get("paradigm_forms") or []:
            if form != e["lemma"]:
                index_tags += f'<d:index d:value="{html.escape(form)}"/>'

        xml_out.append(f"""
        <d:entry id="entry_{idx}" d:title="{html.escape(e['lemma'])}">
            {index_tags}
            <h1>{html.escape(e['lemma'])}{gram_html}</h1>
            {translations_html}
            {examples_html}
            {idioms_html}
            {paradigm_html}
        </d:entry>
        """)
    xml_out.append("</d:dictionary>")
    _write(out_path, xml_out)
    return idx


def build_all_to_is(entries, out_path):
    """Combined 'NordicIcelandic' edition: any Danish/Norwegian/Swedish/
    Faroese/Finnish word looked up together, each tagged with which
    language(s) it came from and which Icelandic word(s) it maps to."""
    reverse = defaultdict(list)  # headword -> [(entry, lang_code), ...]
    for e in entries:
        for lang_code, forms in e.get("equivalents", {}).items():
            for form in forms:
                reverse[form].append((e, lang_code))

    xml_out = [
        '<?xml version="1.0" encoding="UTF-8"?>',
        '<d:dictionary xmlns="http://www.w3.org/1999/xhtml" xmlns:d="http://www.apple.com/DTDs/DictionaryService-1.0.rng">',
    ]
    idx = 0
    for headword in sorted(reverse.keys(), key=str.lower):
        idx += 1
        grouped = defaultdict(list)  # (lemma, gram) -> [lang_name, ...]
        for e, lang_code in reverse[headword]:
            gram = ", ".join(x for x in [e.get("pos", ""), e.get("gender", "")] if x)
            grouped[(e["lemma"], gram)].append(TARGET_LANGS[lang_code])

        items = []
        for (lemma, gram), langs in grouped.items():
            uniq_langs = list(dict.fromkeys(langs))
            gram_html = f" <span class='gram'>({html.escape(gram)})</span>" if gram else ""
            langs_html = f" <span class='src-lang'>[{html.escape(', '.join(uniq_langs))}]</span>"
            items.append(f"<li>{html.escape(lemma)}{gram_html}{langs_html}</li>")

        xml_out.append(render_entry(idx, headword, "", "".join(items)))
    xml_out.append("</d:dictionary>")
    _write(out_path, xml_out)
    return idx


def _write(path, lines):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        f.write("\n".join(lines))


def write_plist(bundle, display_name, out_path):
    region = "is" if bundle.startswith("Icelandic") else "en"
    content = PLIST_TEMPLATE.format(region=region, bundle_id=bundle, display_name=display_name)
    with open(out_path, "w", encoding="utf-8") as f:
        f.write(content)


def build_one(entries, lang_code, direction):
    bundle = bundle_name(lang_code, direction)
    xml_path = os.path.join(OUT_DIR, f"{bundle}.xml")
    plist_path = os.path.join(OUT_DIR, f"{bundle}.plist")

    if lang_code == "all":
        count = build_is_to_all(entries, xml_path) if direction == "is2x" else build_all_to_is(entries, xml_path)
    elif direction == "is2x":
        count = build_is_to_target(entries, lang_code, xml_path)
    else:
        count = build_target_to_is(entries, lang_code, xml_path)

    write_plist(bundle, DISPLAY_NAMES[(lang_code, direction)], plist_path)
    print(f"  {bundle}: {count} entries -> {xml_path}")
    return bundle


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--lang", choices=list(TARGET_LANGS) + ["all"], help="Single target language code, or 'all' for the combined Nordic edition")
    parser.add_argument("--direction", choices=["is2x", "x2is"], help="is2x = Icelandic headword, x2is = target-language headword")
    parser.add_argument("--all", action="store_true", help="Build all 6 per-language bundles x 2 directions, plus the 2 combined 'all Nordic' bundles (14 bundles)")
    parser.add_argument("--no-morphology", action="store_true", help="Skip BÍN inflection tables (faster, no `islenska` dependency)")
    args = parser.parse_args()

    entries = load_entries()
    print(f"Loaded {len(entries)} ISLEX entries")

    directions_requested = {"is2x", "x2is"} if args.all else {args.direction}
    if not args.no_morphology and "is2x" in directions_requested:
        print("Enriching Icelandic headwords with BÍN inflection tables (cached by lemma, runs once)...")
        entries = ensure_bin_paradigms(entries)

    built = []
    if args.all:
        for lang_code in list(TARGET_LANGS) + ["all"]:
            for direction in ("is2x", "x2is"):
                built.append(build_one(entries, lang_code, direction))
    else:
        if not args.lang or not args.direction:
            parser.error("Specify --lang and --direction, or use --all")
        built.append(build_one(entries, args.lang, args.direction))

    os.makedirs(OUT_DIR, exist_ok=True)
    with open(os.path.join(OUT_DIR, "bundles.txt"), "w") as f:
        f.write("\n".join(built) + "\n")
    print(f"Done. {len(built)} bundle(s) ready in {OUT_DIR}/")


if __name__ == "__main__":
    main()
