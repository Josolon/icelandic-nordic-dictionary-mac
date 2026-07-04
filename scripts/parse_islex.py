#!/usr/bin/env python3
"""Parse the ISLEX LMF-XML dump into a flat, language-indexed structure.

ISLEX (CC BY-NC-ND 4.0, Stofnun Árna Magnússonar/CLARIN Iceland) is
Icelandic-headword only: each <LexicalEntry> has one Icelandic lemma and,
scattered at various nesting depths under it, <Equivalent language="..."
writtenForm="..."/> tags for Danish, Norwegian (Bokmål/Nynorsk), Swedish,
Faroese and Finnish. Reverse (target-language -> Icelandic) lookups are
built later by inverting this structure, not by re-parsing.
"""
import xml.etree.ElementTree as ET
from collections import defaultdict

TARGET_LANGS = {
    "dan": "Danish",
    "nob": "Norwegian Bokmål",
    "nno": "Norwegian Nynorsk",
    "swe": "Swedish",
    "fao": "Faroese",
    "fin": "Finnish",
}


IDIOM_TAGS = {"SemanticIdiomaticity", "VerbPhrase", "SemanticCollocation"}


def local(tag):
    return tag.split("}")[-1]


def _first_isl_text(node):
    for t in node.iter():
        if local(t.tag) == "text" and t.attrib.get("language") == "isl" and t.text and t.text.strip():
            return t.text.strip()
    return ""


def parse_islex(xml_path):
    """Return a list of {id, lemma, pos, gender, equivalents, idioms, examples} dicts.

    `equivalents` only contains plain word/phrase-sense translations. Idiomatic
    expressions and collocations (SemanticIdiomaticity/VerbPhrase/SemanticCollocation)
    are kept separately in `idioms` since mixing them in produces misleading
    "translations" (e.g. "hestur" -> "sætte sig på den høje hest").
    """
    tree = ET.parse(xml_path)
    root = tree.getroot()

    entries = []
    for entry in root.iter():
        if local(entry.tag) != "LexicalEntry":
            continue

        entry_id = entry.attrib.get("id", "")
        pos = ""
        lemma = ""
        gender = ""

        for child in entry:
            tag = local(child.tag)
            if tag == "feat" and child.attrib.get("att") == "partOfSpeech":
                pos = child.attrib.get("val", "")
            elif tag == "Lemma":
                for f in child:
                    if local(f.tag) == "feat" and f.attrib.get("att") == "writtenForm":
                        lemma = f.attrib.get("val", "")
            elif tag == "WordForm":
                for f in child:
                    if local(f.tag) == "feat" and f.attrib.get("att") == "grammaticalGender":
                        gender = f.attrib.get("val", "")

        if not lemma:
            continue

        parent_map = {c: p for p in entry.iter() for c in p}

        def is_inside_idiom(node):
            curr = node
            while curr in parent_map:
                curr = parent_map[curr]
                if local(curr.tag) in IDIOM_TAGS:
                    return True
            return False

        equivalents = defaultdict(list)
        idioms = []
        examples = []

        for node in entry.iter():
            tag = local(node.tag)
            if tag == "Equivalent" and not is_inside_idiom(node):
                lang = node.attrib.get("language", "")
                form = node.attrib.get("writtenForm", "")
                if lang in TARGET_LANGS and form and form not in equivalents[lang]:
                    equivalents[lang].append(form)
            elif tag in IDIOM_TAGS:
                phrase = _first_isl_text(node) or lemma
                idiom_equivalents = defaultdict(list)
                for sub in node.iter():
                    if local(sub.tag) == "Equivalent":
                        lang = sub.attrib.get("language", "")
                        form = sub.attrib.get("writtenForm", "")
                        if lang in TARGET_LANGS and form and form not in idiom_equivalents[lang]:
                            idiom_equivalents[lang].append(form)
                if idiom_equivalents:
                    idioms.append({"phrase": phrase, "equivalents": dict(idiom_equivalents)})
            elif tag == "SenseExample" and not is_inside_idiom(node):
                for t in node.iter():
                    if local(t.tag) == "text" and t.text and t.text.strip():
                        text = t.text.strip()
                        if text not in examples:
                            examples.append(text)

        entries.append(
            {
                "id": entry_id,
                "lemma": lemma,
                "pos": pos,
                "gender": gender,
                "equivalents": dict(equivalents),
                "idioms": idioms,
                "examples": examples[:3],
            }
        )

    return entries


if __name__ == "__main__":
    import json
    import sys

    src = sys.argv[1] if len(sys.argv) > 1 else "data/ISLEX_dictionary_2023-12.xml"
    result = parse_islex(src)
    print(f"Parsed {len(result)} entries from {src}")
    print(json.dumps(result[:3], ensure_ascii=False, indent=2))
