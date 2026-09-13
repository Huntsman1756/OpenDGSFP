# -*- coding: utf-8 -*-
"""Loaders for the four G0 sources + provenance blocks (contract SS7).

Reads only frozen inputs under data/ (raw + derived parse of RRPP details).
Snapshot dates come from evidence/source-manifest.json fetch events
(Last-Modified / registered_at); every provenance block carries content_sha256
computed from the file itself.
"""
import csv
import hashlib
import json
import pathlib
import re
import unicodedata

ROOT = pathlib.Path(__file__).parent.parent

URLS = {
    "DGSFP_RRPP": "https://rrpp.dgsfp.mineco.es/Aseguradora/GetAseguradora/",
    "BDE": "https://www.bde.es/wbe/es/estadisticas/otras-clasificaciones/clasificacion-entidades/listas-instituciones-financieras/listas-empresas-seguros-pais/",
    "EIOPA": "https://register.eiopa.europa.eu/registers/register-of-insurance-undertakings",
    "GLEIF": "https://api.gleif.org/api/v1/lei-records",
}

TIERS = {"DGSFP_RRPP": "T2_PRIMARY_UI", "BDE": "T1_PRIMARY_DOCUMENT",
         "EIOPA": "T0_PRIMARY_DIRECT", "GLEIF": "T0_PRIMARY_DIRECT"}

# DGSFP pais_origen (Spanish label) -> ISO 3166 alpha-2. Same map as G0-B2.
COUNTRY_ES2ISO = {
    "Alemania": "DE", "Francia": "FR", "Irlanda": "IE", "Luxemburgo": "LU",
    "Belgica": "BE", "Malta": "MT", "Paises Bajos": "NL", "Suecia": "SE",
    "Italia": "IT", "Liechtenstein": "LI", "Portugal": "PT", "Austria": "AT",
    "Dinamarca": "DK", "Finlandia": "FI", "Grecia": "EL", "Hungria": "HU",
    "Noruega": "NO", "Polonia": "PL", "Reino Unido": "GB", "Chipre": "CY",
    "Croacia": "HR", "Eslovaquia": "SK", "Eslovenia": "SI", "Bulgaria": "BG",
    "Republica Checa": "CZ", "Rumania": "RO", "Estonia": "EE", "Letonia": "LV",
    "Lituania": "LT", "Islandia": "IS", "Espana": "ES",
}


def strip_accents(s):
    s = unicodedata.normalize("NFKD", s or "")
    return "".join(c for c in s if not unicodedata.combining(c))


def pais_to_iso(s):
    return COUNTRY_ES2ISO.get(strip_accents(s))


def sha256_of(path):
    return hashlib.sha256(pathlib.Path(path).read_bytes()).hexdigest()


def norm_dgsfp_key(code):
    """Normalize BdE 'Codigo de supervisor' / EIOPA ES id to a DGSFP clave."""
    c = re.sub(r"\s+", "", (code or "")).upper()
    m = re.match(r"^([A-Z]+)0*(\d+)$", c)
    return f"{m.group(1)}{int(m.group(2)):04d}" if m else c


LEI_ALPHABET_I36 = None


def lei_checksum_valid(lei):
    """ISO 17442 / ISO 7064 MOD 97-10 (donor mechanism, MIT)."""
    lei = (lei or "").strip().upper()
    if len(lei) != 20 or not lei.isalnum():
        return False
    try:
        expanded = "".join(str(int(c, 36)) for c in lei)
    except ValueError:
        return False
    return int(expanded) % 97 == 1


def load_dgsfp(root=ROOT):
    path = pathlib.Path(root) / "data/derived/dgsfp_rrpp_entities.jsonl"
    return [json.loads(l) for l in path.open(encoding="utf-8")]


def _norm_key(k):
    return re.sub(r"\s+", " ", k).strip().upper()


def load_bde(path):
    with open(path, encoding="utf-8-sig") as f:
        rdr = csv.reader(f)
        cols = [_norm_key(c) for c in next(rdr)]
        return [{cols[i]: (r[i] if i < len(r) else "").strip()
                 for i in range(len(cols))}
                for r in rdr if any(x.strip() for x in r)]


def load_eiopa(root=ROOT):
    p = pathlib.Path(root) / "data/raw/eiopa/eiopa_register.csv"
    with open(p, encoding="utf-8-sig") as f:
        return list(csv.DictReader(f, delimiter=";"))


def load_gleif(root=ROOT):
    path = pathlib.Path(root) / "data/raw/gleif/gleif_records.jsonl"
    out = {}
    for line in path.open(encoding="utf-8"):
        r = json.loads(line)
        out[r["lei"]] = r
    return out


def load_manifest(root=ROOT):
    p = pathlib.Path(root) / "evidence/source-manifest.json"
    return json.loads(p.read_text(encoding="utf-8"))


def manifest_index(manifest):
    """raw_file -> {content_sha256, registered_at} from the G0 manifest."""
    return {e["raw_file"]: e for e in manifest.get("files", [])}


def bde_snapshot_date(manifest, filename):
    """Per-list snapshot date via Last-Modified fetch event (fallback G0 date)."""
    for e in manifest.get("fetch_events", []):
        if filename in (e.get("source_url") or ""):
            lm = (e.get("response_headers") or {}).get("last-modified") or ""
            m = re.search(r"(\d{2}) (\w{3}) (\d{4})", lm)
            if m:
                months = {"Jan": 1, "Feb": 2, "Mar": 3, "Apr": 4, "May": 5, "Jun": 6,
                          "Jul": 7, "Aug": 8, "Sep": 9, "Oct": 10, "Nov": 11, "Dec": 12}
                return f"{m.group(3)}-{months[m.group(2)]:02d}-{m.group(1)}"
    return "2026-09-11"  # documented G0 BdE snapshot


def make_prov(system, jurisdiction, raw_file, manifest_idx, snapshot_date,
              parser_version, url=None):
    """Full provenance block per contract SS7."""
    e = manifest_idx.get(raw_file, {})
    return {
        "source_system": system,
        "jurisdiction": jurisdiction,
        "source_url": url or URLS.get(system),
        "source_snapshot_date": snapshot_date,
        "retrieved_at": e.get("registered_at"),
        "content_sha256": sha256_of(ROOT / raw_file),
        "parser_version": parser_version,
        "raw_file": raw_file,
        "evidence_tier": TIERS[system],
    }


def norm_name(s):
    """Aggressive normalization for DIAGNOSTIC comparison only (never canonical)."""
    s = strip_accents(s).upper()
    s = re.sub(r"[^A-Z0-9]+", " ", s)
    s = re.sub(r"\b(SA|S A|SL|SE|NV|AG|GMBH|DAC|PLC|LTD|LIMITED|INC|SUI|SOCIEDAD ANONIMA|"
               r"COMPA\w*IA|DE|DEL|LA|EL|Y|THE|COMPANY|CORP|GROUP|SEGUROS|REASEGUROS|"
               r"INSURANCE|REINSURANCE|VERSICHERUNG|VERSVICHERUNG)\b", " ", s)
    return re.sub(r"\s+", " ", s).strip()


def diag_name_agree(a, b):
    na, nb = norm_name(a), norm_name(b)
    if not na or not nb:
        return "different"
    if na == nb:
        return "exact_norm"
    ta, tb = set(na.split()), set(nb.split())
    if ta and tb and (ta <= tb or tb <= ta):
        return "token_subset"
    return "different"
