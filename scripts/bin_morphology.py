#!/usr/bin/env python3
"""BÍN-powered inflection tables for Icelandic headwords.

Ported from the companion `icelandic-dictionary-mac` project's build_dict.py
(same verb/noun/adjective paradigm rendering), factored out here as a
standalone module so it can be reused for the ISLEX-headword (is2x) bundles
without dragging in that project's INO-specific definition parsing.

Requires the `islenska` package (BÍN access): pip install islenska
"""
import html
import re

NUTHALEGAR_VERBS = {
    "eiga", "mega", "unna", "kunna", "knega", "muna", "munu", "skulu", "vilja", "vita", "þurfa"
}

RI_VERBS_THREE_PARTS = {"gróa", "róa", "snúa", "núa"}


def clean_grammar_tag(bin_tag):
    tag_map = {
        "NFET": "nf.et.", "ÞFET": "þf.et.", "ÞGFET": "þgf.et.", "EFET": "ef.et.",
        "NFFT": "nf.ft.", "ÞFFT": "þf.ft.", "ÞGFFT": "þgf.ft.", "EFFT": "ef.ft.",
    }
    bin_tag_upper = bin_tag.upper()
    display_tag = tag_map.get(bin_tag_upper, bin_tag.lower())
    article_label = "gr." if "gr" in bin_tag.lower() else ""
    return display_tag, article_label


def clean_headword_for_bin(hw_str):
    """Strips out homograph index notation for clean DB lookups."""
    return re.sub(r'[\d\(\)_\-\s]+$', '', hw_str).strip()


def detect_weak_verb(lemma, past_1sg, supine, grammar_txt=""):
    g = (grammar_txt or "").lower()
    if any(k in g for k in ["veik", "weak"]):
        return True
    if any(k in g for k in ["sterk", "strong", "óregl"]):
        return False

    if (lemma or "").strip().lower() in NUTHALEGAR_VERBS:
        return False

    lemma_l = (lemma or "").strip().lower().replace("st", "")
    past = (past_1sg or "").strip().lower()
    sagnb = (supine or "").strip().lower()
    if not past or past == "-":
        return False

    if not past.endswith(("aði", "di", "ti", "ði")):
        return False

    lemma_root = re.sub(r"(a|ja|va)$", "", lemma_l)
    past_root = re.sub(r"(aði|di|ti|ði)$", "", past)
    if len(lemma_root) >= 2 and len(past_root) >= 2 and lemma_root[:2] == past_root[:2]:
        return True

    if sagnb.endswith(("að", "ð", "t")) and lemma_root and past_root and lemma_root in past:
        return True

    return False


def force_three_kennimyndir(lemma):
    return (lemma or "").strip().lower() in RI_VERBS_THREE_PARTS


def get_verb_class_note(lemma):
    l = (lemma or "").strip().lower()
    if l in NUTHALEGAR_VERBS:
        return "Núþáleg sögn"
    if l in RI_VERBS_THREE_PARTS:
        return "ri-sögn (sýnd með þremur kennimyndum)"
    return ""


def noun_cell(indefinite, definite):
    base = (indefinite or "").strip()
    with_article = (definite or "").strip()
    if base and with_article and base != with_article:
        return f"{html.escape(base)}<br/><span style='font-size:0.9em;color:#666;'>(gr.: {html.escape(with_article)})</span>"
    if with_article:
        return html.escape(with_article)
    return html.escape(base) if base else "-"


def parse_noun_form_key(mark):
    tag = (mark or "").upper().replace('.', '').replace('_', '')
    if not tag:
        return ""
    if "ÞGF" in tag or "DATIVE" in tag or "DAT" in tag:
        case = "ÞGF"
    elif "ÞF" in tag or "ACC" in tag:
        case = "ÞF"
    elif "EF" in tag or "GEN" in tag:
        case = "EF"
    elif "NF" in tag or "NOM" in tag:
        case = "NF"
    else:
        return ""
    num = "FT" if ("FT" in tag or "PL" in tag) else "ET"
    gr = "GR" if ("GR" in tag or "DEF" in tag) else ""
    return f"{case}{num}{gr}"


def pick_first(forms_dict, keys, default="-"):
    for k in keys:
        if forms_dict.get(k):
            return forms_dict[k]
    return default


def pick_adjective_declension(forms, gender, case, number):
    return pick_first(forms, [f"FSB-{gender}-{case}{number}"], "")


def pick_variant_form(b, lemma, tag):
    cat = 'lo' if tag.startswith(('FSB-', 'FVB-', 'ESB-', 'EVB-')) else 'so'
    try:
        variants = b.lookup_variants(lemma, cat, tag)
    except Exception:
        return ""
    seen = set()
    forms = []
    for v in variants:
        f = (getattr(v, 'bmynd', '') or '').strip()
        if f and f not in seen:
            seen.add(f)
            forms.append(f)
    if not forms:
        return ""

    lemma_l = (lemma or "").strip().lower()

    if lemma_l in RI_VERBS_THREE_PARTS:
        if tag in {'GM-FH-ÞT-1P-ET', 'GM-FH-ÞT-3P-ET', 'MM-FH-ÞT-1P-ET', 'MM-FH-ÞT-3P-ET', 'GM-VH-ÞT-1P-ET', 'GM-VH-ÞT-3P-ET'}:
            for f in forms:
                if f.endswith(('ri', 'rí', 'eri', 'éri')):
                    return f
        if tag in {'GM-FH-ÞT-1P-FT', 'GM-FH-ÞT-3P-FT', 'MM-FH-ÞT-1P-FT', 'MM-FH-ÞT-3P-FT'}:
            for f in forms:
                if f.endswith('rum'):
                    return f
        if tag in {'GM-SAGNB', 'MM-SAGNB'}:
            for f in forms:
                if f.endswith('ið'):
                    return f

    if tag == 'GM-SAGNB':
        for f in forms:
            if f.endswith('við'):
                return f
    return forms[0]


def enrich_verb_forms_via_variants(b, lemma, forms):
    lemma_l = (lemma or "").strip().lower()
    needed_tags = [
        'GM-NH', 'GM-SAGNB',
        'GM-FH-NT-1P-ET', 'GM-FH-NT-3P-ET',
        'GM-FH-ÞT-1P-ET', 'GM-FH-ÞT-3P-ET', 'GM-FH-ÞT-1P-FT',
        'GM-VH-NT-1P-ET', 'GM-VH-NT-3P-ET', 'GM-VH-ÞT-1P-ET', 'GM-VH-ÞT-3P-ET',
        'MM-NH', 'MM-SAGNB',
        'MM-FH-ÞT-1P-ET', 'MM-FH-ÞT-3P-ET', 'MM-FH-ÞT-1P-FT',
        'MM-VH-NT-1P-ET', 'MM-VH-NT-3P-ET', 'MM-VH-ÞT-1P-ET', 'MM-VH-ÞT-3P-ET',
    ]

    force_override_tags = set()
    if lemma_l in RI_VERBS_THREE_PARTS:
        force_override_tags = {
            'GM-FH-ÞT-1P-ET', 'GM-FH-ÞT-3P-ET',
            'GM-FH-ÞT-1P-FT', 'GM-FH-ÞT-3P-FT',
            'GM-SAGNB',
            'GM-VH-ÞT-1P-ET', 'GM-VH-ÞT-3P-ET',
        }

    for tag in needed_tags:
        if forms.get(tag) and tag not in force_override_tags:
            continue
        val = pick_variant_form(b, lemma, tag)
        if val:
            forms[tag] = val
    return forms


def enrich_adjective_forms_via_variants(b, lemma, forms):
    genders = ["KK", "KVK", "HK"]
    cases = ["NF", "ÞF", "ÞGF", "EF"]
    numbers = ["ET", "FT"]

    for g in genders:
        for c in cases:
            for n in numbers:
                tag = f"FSB-{g}-{c}{n}"
                if forms.get(tag):
                    continue
                val = pick_variant_form(b, lemma, tag)
                if val:
                    forms[tag] = val
    return forms


def get_full_paradigm_via_blaster(b, headword, pos_cat):
    candidates = set([headword, headword.lower()])
    stem = headword
    if headword.endswith(('ur', 'ar', 'ir', 'inn', 'nn')): stem = headword[:-2]
    elif headword.endswith(('a', 'i', 'u', 'r', 'n')): stem = headword[:-1]

    noun_endings = ["", "s", "i", "ar", "a", "um", "sins", "inn", "inum", "inu", "ina", "arnir", "ana", "unum", "anna", "ið", "in", "ins", "arinnar", "innar", "ir", "urnir", "urnar"]
    verb_endings = ["", "a", "ar", "ir", "ið", "um", "andi", "að", "inn", "ið", "ði", "di", "ti", "ri", "ðum", "dum", "tum", "rum", "ðu", "du", "tu", "ru", "ast", "ust", "umst", "ðust", "dust", "tist", "i", "ir", "ætti", "ættum", "ættu"]

    stems = [headword, stem]
    if 'a' in stem: stems.append(stem.replace('a', 'ö'))

    for s in stems:
        endings = verb_endings if pos_cat == 'so' else noun_endings
        for e in endings: candidates.add(s + e)

    irregular_map = {
        "eiga": ["á", "átt", "átti", "áttum", "áttu", "áttuð", "eigum", "eigið", "eiga", "eigast", "ást", "áttst", "áttust", "eigumst", "eigiðst", "ætti", "ættum", "ættu", "eigi"],
        "hestur": ["hestur", "hest", "hesti", "hests", "hestar", "hesta", "hestum", "hestsins", "hestinn", "hestinum", "hestarnir", "hestana", "hestunum", "hestanna"]
    }
    if headword.lower() in irregular_map: candidates.update(irregular_map[headword.lower()])

    final_matches = []
    seen_keys = set()
    target_ofl = 'so' if pos_cat == 'so' else pos_cat

    for c in candidates:
        if not c: continue
        try:
            res = b.lookup(c)
            if res:
                matches = res[1] if (isinstance(res, tuple) and len(res) == 2) else res
                for m in matches:
                    m_ord = getattr(m, "ord", "").lower()
                    m_ofl = getattr(m, "ofl", getattr(m, "hluti", "")).lower()

                    is_match = False
                    if target_ofl == 'so' and m_ofl == 'so': is_match = True
                    elif target_ofl == 'no' and m_ofl in ['kk', 'kvk', 'hk', 'no']: is_match = True
                    elif m_ofl == target_ofl: is_match = True

                    if m_ord == headword.lower() and is_match:
                        key = (getattr(m, "bmynd", ""), getattr(m, "beyging", getattr(m, "mark", "")).upper())
                        if key not in seen_keys:
                            seen_keys.add(key)
                            final_matches.append(m)
        except Exception: pass

    if pos_cat == 'no':
        try:
            _, lemmas = b.lookup_lemmas(headword)
            noun_cats = [x.ofl for x in lemmas if getattr(x, 'ofl', '') in ['kk', 'kvk', 'hk', 'no']]
            for noun_cat in set(noun_cats):
                for case in ['NF', 'ÞF', 'ÞGF', 'EF']:
                    for m in b.lookup_forms(headword, noun_cat, case):
                        key = (getattr(m, 'bmynd', ''), getattr(m, 'mark', getattr(m, 'beyging', '')).upper())
                        if key not in seen_keys:
                            seen_keys.add(key)
                            final_matches.append(m)
        except Exception:
            pass
    return final_matches


def _render_verb_table(voice_title, p1, p2, p3, p4, subj_nt, subj_þt, weak, class_note, nuthaleg=False):
    if weak:
        principal_headers = ["Nh.", "Fh. þt.", "Lh. þt."]
        principal_values = [p1, p2, p3]
        subj_headers = ["Vth. nt.", "Vth. þt.", ""]
        subj_cells = [subj_nt, subj_þt, ""]
        layout_note = "<div style='font-size:0.9em;color:#666;margin-bottom:4px;'><i>Veik beyging: þrjár kennimyndir.</i></div>"
    elif nuthaleg:
        principal_headers = ["Nh.", "Fh. nt.", "Fh. þt.", "Lh. þt."]
        principal_values = [p1, p2, p3, p4]
        subj_headers = ["Vth. nt.", "", "Vth. þt.", ""]
        subj_cells = [subj_nt, "", subj_þt, ""]
        layout_note = ""
    else:
        principal_headers = ["Nh.", "Fh. þt. et.", "Fh. þt. ft.", "Lh. þt."]
        principal_values = [p1, p2, p3, p4]
        subj_headers = ["Vth. nt.", "", "Vth. þt.", ""]
        subj_cells = [subj_nt, "", subj_þt, ""]
        layout_note = ""

    class_note_html = ""
    if class_note:
        class_note_html = f"<div style='font-size:0.9em;color:#555;margin-bottom:4px;'><i>{html.escape(class_note)}</i></div>"

    th_html = "".join([f"<th>{h}</th>" for h in principal_headers])
    subj_th_html = "".join([f"<th>{h}</th>" for h in subj_headers])
    principal_html = "".join([f"<td><b>{html.escape(v if v else '-')}</b></td>" for v in principal_values])
    subj_html = "".join([f"<td><i>{html.escape(v if v else '-')}</i></td>" for v in subj_cells])

    return f"""
    <div class="voice-section"><h4>{voice_title}</h4>
        {class_note_html}
        {layout_note}
        <table class="verb-paradigm-table strong-verb">
            <tr class="row-subjunctive">{th_html}</tr>
            <tr class="row-principal">{principal_html}</tr>
            <tr class="row-subjunctive">{subj_th_html}</tr>
            <tr class="row-subjunctive">{subj_html}</tr>
        </table>
    </div>
    """


def build_paradigm(b, headword, pos_cat):
    """Look up `headword` in BÍN (via the `islenska` Bin instance `b`) for the
    given category ('no'/'so'/'lo') and return (paradigm_html, seen_forms).

    Returns ("", set()) if BÍN has no matching entry or pos_cat isn't one of
    the three tables we render (noun/verb/adjective).
    """
    if pos_cat not in ("no", "so", "lo"):
        return "", set()

    lookup_hw = clean_headword_for_bin(headword)
    bin_matches = get_full_paradigm_via_blaster(b, lookup_hw, pos_cat)

    seen_forms = set()
    forms = {}
    is_verb = False
    is_noun = False
    is_adjective = False

    for match in bin_matches:
        try:
            inflected_word = getattr(match, "bmynd", getattr(match, "ord", ""))
            tag = getattr(match, "mark", getattr(match, "beyging", "")).upper()
            ordfl = getattr(match, "ofl", getattr(match, "hluti", "")).lower()
        except Exception:
            continue

        if not inflected_word:
            continue
        seen_forms.add(inflected_word)

        if ordfl == "so":
            is_verb = True
            forms[tag] = inflected_word
        elif ordfl in ["kk", "kvk", "hk", "no"]:
            is_noun = True
            noun_key = parse_noun_form_key(tag)
            if noun_key:
                forms[noun_key] = inflected_word
        elif ordfl == "lo":
            is_adjective = True
            forms[tag] = inflected_word

    if pos_cat == "so":
        forms = enrich_verb_forms_via_variants(b, lookup_hw, forms)
        if any(k.startswith("GM-") or k.startswith("MM-") for k in forms.keys()):
            is_verb = True
    elif pos_cat == "lo":
        forms = enrich_adjective_forms_via_variants(b, lookup_hw, forms)
        if any("-KK-" in k or "-KVK-" in k or "-HK-" in k for k in forms.keys()):
            is_adjective = True

    for v in forms.values():
        if v:
            seen_forms.add(v)

    if not forms:
        return "", seen_forms

    paradigm_html = ""

    if is_verb:
        verb_blocks = []
        class_note = get_verb_class_note(lookup_hw)

        nh = pick_first(forms, ["GM-NH", "NH"], lookup_hw)
        nt_et = pick_first(forms, ["GM-FH-NT-1P-ET", "GM-FH-NT-3P-ET", "FH-NT-1P-ET", "FH-NT-3P-ET"])
        fh_et = pick_first(forms, ["GM-FH-ÞT-1P-ET", "GM-FH-ÞT-3P-ET", "FH-ÞT-1P-ET", "FH-ÞT-3P-ET"])
        fh_ft = pick_first(forms, ["GM-FH-ÞT-1P-FT", "GM-FH-ÞT-3P-FT", "FH-ÞT-1P-FT", "FH-ÞT-3P-FT"])
        sagnb = pick_first(forms, ["GM-SAGNB", "SAGNB"])
        vh_nt = pick_first(forms, ["GM-VH-NT-1P-ET", "GM-VH-NT-3P-ET", "VH-NT-1P-ET", "VH-NT-3P-ET"])
        vh_þt = pick_first(forms, ["GM-VH-ÞT-1P-ET", "GM-VH-ÞT-3P-ET", "VH-ÞT-1P-ET", "VH-ÞT-3P-ET"])

        mm_nh = pick_first(forms, ["MM-NH"], f"{lookup_hw if not lookup_hw.endswith('st') else lookup_hw[:-2]}st")
        mm_fh_et = pick_first(forms, ["MM-FH-ÞT-1P-ET", "MM-FH-ÞT-3P-ET"])
        mm_fh_ft = pick_first(forms, ["MM-FH-ÞT-1P-FT", "MM-FH-ÞT-3P-FT"])
        mm_sagnb = pick_first(forms, ["MM-SAGNB"])
        mm_vh_nt = pick_first(forms, ["MM-VH-NT-1P-ET", "MM-VH-NT-3P-ET"])
        mm_vh_þt = pick_first(forms, ["MM-VH-ÞT-1P-ET", "MM-VH-ÞT-3P-ET"])

        if lookup_hw == "eiga" or mm_fh_et in ["ást", "áttst"]:
            mm_fh_et = "-"
            mm_fh_ft = "-"
            mm_sagnb = "-"
            mm_vh_nt = "-"
            mm_vh_þt = "-"

        is_weak = detect_weak_verb(lookup_hw, fh_et, sagnb)
        if force_three_kennimyndir(lookup_hw):
            is_weak = True

        is_nuthaleg = lookup_hw.lower() in NUTHALEGAR_VERBS
        if is_nuthaleg:
            active_p2 = nt_et
            active_p3 = fh_et
            active_p4 = sagnb
        else:
            active_p2 = fh_et
            active_p3 = sagnb if is_weak else fh_ft
            active_p4 = "" if is_weak else sagnb
        verb_blocks.append(_render_verb_table("Germynd", nh, active_p2, active_p3, active_p4, vh_nt, vh_þt, is_weak, class_note, is_nuthaleg))

        has_mm = any("MM-" in k for k in forms.keys()) or lookup_hw.endswith('st')
        if has_mm:
            mm_is_weak = True if force_three_kennimyndir(lookup_hw) else is_weak
            if is_nuthaleg:
                mm_p2 = pick_first(forms, ["MM-FH-NT-1P-ET", "MM-FH-NT-3P-ET"])
                mm_p3 = mm_fh_et
                mm_p4 = mm_sagnb
            else:
                mm_p2 = mm_fh_et
                mm_p3 = mm_sagnb if mm_is_weak else mm_fh_ft
                mm_p4 = "" if mm_is_weak else mm_sagnb
            verb_blocks.append(_render_verb_table("Miðmynd", mm_nh, mm_p2, mm_p3, mm_p4, mm_vh_nt, mm_vh_þt, mm_is_weak, "", is_nuthaleg))

        grid_content = "".join(verb_blocks)
        paradigm_html = f'<details class="inflection-drawer"><summary>Beygingarlýsing (Kennimyndir)</summary><div class="inflection-container-verbs">{grid_content}</div></details>'

    elif is_noun:
        nf_et, þf_et, gf_et, ef_et = forms.get("NFET", ""), forms.get("ÞFET", ""), forms.get("ÞGFET", ""), forms.get("EFET", "")
        nf_ft, þf_ft, gf_ft, ef_ft = forms.get("NFFT", ""), forms.get("ÞFFT", ""), forms.get("ÞGFFT", ""), forms.get("EFFT", "")
        nf_et_gr, þf_et_gr, gf_et_gr, ef_et_gr = forms.get("NFETGR", ""), forms.get("ÞFETGR", ""), forms.get("ÞGFETGR", ""), forms.get("EFETGR", "")
        nf_ft_gr, þf_ft_gr, gf_ft_gr, ef_ft_gr = forms.get("NFFTGR", ""), forms.get("ÞFFTGR", ""), forms.get("ÞGFFTGR", ""), forms.get("EFFTGR", "")

        table = f"""
        <div class="voice-section"><h4>Fallbeyging</h4>
        <table class="verb-paradigm-table strong-verb" style="text-align: left;">
            <tr class="row-principal"><td></td><td style="text-align: center;"><b>Eintala</b></td><td style="text-align: center;"><b>Fleirtala</b></td></tr>
            <tr><td><i>Nf.</i></td><td style="text-align: center;">{noun_cell(nf_et, nf_et_gr)}</td><td style="text-align: center;">{noun_cell(nf_ft, nf_ft_gr)}</td></tr>
            <tr><td><i>Þf.</i></td><td style="text-align: center;">{noun_cell(þf_et, þf_et_gr)}</td><td style="text-align: center;">{noun_cell(þf_ft, þf_ft_gr)}</td></tr>
            <tr><td><i>Þgf.</i></td><td style="text-align: center;">{noun_cell(gf_et, gf_et_gr)}</td><td style="text-align: center;">{noun_cell(gf_ft, gf_ft_gr)}</td></tr>
            <tr><td><i>Ef.</i></td><td style="text-align: center;">{noun_cell(ef_et, ef_et_gr)}</td><td style="text-align: center;">{noun_cell(ef_ft, ef_ft_gr)}</td></tr>
        </table>
        </div>
        """
        paradigm_html = f'<details class="inflection-drawer"><summary>Beygingarlýsing</summary><div class="inflection-container-verbs">{table}</div></details>'

    elif is_adjective:
        def adj_row(case_label, case_code):
            kk_et = pick_adjective_declension(forms, "KK", case_code, "ET")
            kk_ft = pick_adjective_declension(forms, "KK", case_code, "FT")
            kvk_et = pick_adjective_declension(forms, "KVK", case_code, "ET")
            kvk_ft = pick_adjective_declension(forms, "KVK", case_code, "FT")
            hk_et = pick_adjective_declension(forms, "HK", case_code, "ET")
            hk_ft = pick_adjective_declension(forms, "HK", case_code, "FT")
            return (
                f"<tr><td><i>{case_label}</i></td>"
                f"<td>{html.escape(kk_et) if kk_et else '-'}</td><td>{html.escape(kk_ft) if kk_ft else '-'}</td>"
                f"<td>{html.escape(kvk_et) if kvk_et else '-'}</td><td>{html.escape(kvk_ft) if kvk_ft else '-'}</td>"
                f"<td>{html.escape(hk_et) if hk_et else '-'}</td><td>{html.escape(hk_ft) if hk_ft else '-'}</td></tr>"
            )

        table = f"""
        <table class="verb-paradigm-table strong-verb" style="text-align: center;">
            <tr class="row-principal">
                <td></td><td colspan="2"><b>Karlkyn</b></td><td colspan="2"><b>Kvenkyn</b></td><td colspan="2"><b>Hvorugkyn</b></td>
            </tr>
            <tr class="row-subjunctive">
                <td></td><td><i>et.</i></td><td><i>ft.</i></td><td><i>et.</i></td><td><i>ft.</i></td><td><i>et.</i></td><td><i>ft.</i></td>
            </tr>
            {adj_row('Nf.', 'NF')}
            {adj_row('Þf.', 'ÞF')}
            {adj_row('Þgf.', 'ÞGF')}
            {adj_row('Ef.', 'EF')}
        </table>
        """
        paradigm_html = f'<details class="inflection-drawer"><summary>Beygingarlýsing</summary><div class="inflection-container-verbs"><div class="voice-section"><h4>Lýsingarorðsbeyging</h4>{table}</div></div></details>'

    return paradigm_html, seen_forms
