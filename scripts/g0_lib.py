# -*- coding: utf-8 -*-
"""G0 shared library: loaders, LEI arithmetic, name-normalization diagnostics.

Identity policy: canonical edges require EXACT identifiers (key / LEI / official code).
Name similarity is diagnostic-only and never produces a canonical edge.
"""
import csv
import json
import pathlib
import re
import sys
import unicodedata

sys.path.insert(0, str(pathlib.Path(__file__).parent))
from bde_loader import load_bde, norm_dgsfp_key  # noqa: E402

PARSER_VERSION = "g0_lib/0.3"
LEI_ALPHABET = {c: i for i, c in enumerate("0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZ")}


def lei_checksum_valid(lei):
    """ISO 17442 / ISO 7064 MOD 97-10 (implementation reused from donor
    fabio-rovai/insurance-register-ontology, pipeline/checksums.py, MIT)."""
    lei = (lei or "").strip().upper()
    if len(lei) != 20 or not lei.isalnum():
        return False
    try:
        expanded = "".join(str(int(c, 36)) for c in lei)
    except ValueError:
        return False
    return int(expanded) % 97 == 1


def load_dgsfp():
    path = pathlib.Path("data/derived/dgsfp_rrpp_entities.jsonl")
    return [json.loads(l) for l in path.open(encoding="utf-8")]


def load_bde_es():
    return load_bde("data/raw/bde/lista-ic-es.csv")


def load_bde_home(code):
    return load_bde(f"data/raw/bde/lista-ic-{code}.csv")


def load_eiopa():
    with open("data/raw/eiopa/eiopa_register.csv", encoding="utf-8-sig") as f:
        return list(csv.DictReader(f, delimiter=";"))


def load_gleif():
    path = pathlib.Path("data/raw/gleif/gleif_records.jsonl")
    out = {}
    if path.exists():
        for line in path.open(encoding="utf-8"):
            r = json.loads(line)
            out[r["lei"]] = r
    return out


def norm_name(s):
    """Aggressive normalization for DIAGNOSTIC name comparison only."""
    s = unicodedata.normalize("NFKD", s or "")
    s = "".join(c for c in s if not unicodedata.combining(c))
    s = s.upper()
    s = re.sub(r"[^A-Z0-9]+", " ", s)
    s = re.sub(r"\b(SA|S A|SL|SE|NV|AG|GMBH|DAC|PLC|LTD|LIMITED|INC|SUI|SOCIEDAD ANONIMA|"
               r"COMPA\w*IA|DE|DEL|LA|EL|Y|THE|COMPANY|CORP|GROUP|SEGUROS|REASEGUROS|"
               r"INSURANCE|REINSURANCE|VERSVICHERUNG)\b", " ", s)
    return re.sub(r"\s+", " ", s).strip()


def diag_name_agree(a, b):
    """Return diagnostic similarity: exact_norm | token_set | different. NON-CANONICAL."""
    na, nb = norm_name(a), norm_name(b)
    if not na or not nb:
        return "different"
    if na == nb:
        return "exact_norm"
    ta, tb = set(na.split()), set(nb.split())
    if ta and tb and (ta <= tb or tb <= ta):
        return "token_subset"
    return "different"


def manifest_entries():
    m = pathlib.Path("evidence/source-manifest.json")
    if m.exists():
        return json.loads(m.read_text(encoding="utf-8"))
    return []


def bde_publication_date():
    """BdE list publication timestamp (Last-Modified) as snapshot proxy."""
    entries = manifest_entries()
    if isinstance(entries, dict):
        entries = entries.get("fetch_events", [])
    for e in entries:
        if not isinstance(e, dict):
            continue
        if "lista-ic-es.csv" in (e.get("source_url") or ""):
            return e.get("response_headers", {}).get("last-modified")
    return None
