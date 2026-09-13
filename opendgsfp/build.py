# -*- coding: utf-8 -*-
"""Build the v0.1 canonical dataset from frozen G0 inputs.

Merging rule (auditable): records merge iff they share an authority-scoped
identifier. Every merge/attach event is recorded in entity["merge_basis"] with
basis in {SHARED_LEI, SHARED_DGSFP_KEY, SHARED_AUTHORITY_SCOPED_ID,
OFFICIAL_BRIDGE} — name similarity is diagnostic-only and can only produce
UNRESOLVED candidate relations (e.g. IDENTIFIER_SUCCESSOR_CANDIDATE), never a
canonical merge.
"""
import collections
import pathlib

from . import PARSER_VERSION, SCHEMA_VERSION, model as M
from .sources import (TIERS, load_dgsfp, load_bde, load_eiopa, load_gleif,
                      load_manifest, manifest_index, bde_snapshot_date,
                      make_prov, norm_dgsfp_key, lei_checksum_valid, pais_to_iso,
                      norm_name, diag_name_agree, ROOT)

DGSFP_KIND = {"C": "INSURANCE_UNDERTAKING", "M": "INSURANCE_UNDERTAKING",
              "P": "INSURANCE_UNDERTAKING", "R": "REINSURANCE_UNDERTAKING",
              "E": "EEA_BRANCH", "L": "UNDERTAKING"}

FTS_STATUSES = {"EEA FPS", "FPS for EEA Branches"}          # freedom of services (LPS)
BRANCH_STATUSES = {"EEA branch", "3rd country branch"}      # branch presence
PRESENCE_SYSTEMS = {"DGSFP_RRPP", "BDE", "EIOPA"}           # GLEIF validates, not presence

MERGE_BASES = ("SHARED_LEI", "SHARED_DGSFP_KEY",
               "SHARED_AUTHORITY_SCOPED_ID", "OFFICIAL_BRIDGE")


def _add_ident(ent, scheme, value, aid, country=None):
    for i in ent["identifiers"]:
        if i["scheme"] == scheme and i["value"] == value and i.get("country") == country:
            if aid and aid not in i["asserted_by"]:
                i["asserted_by"].append(aid)
            return i
    ident = {"scheme": scheme, "value": value, "asserted_by": [aid] if aid else []}
    if country:
        ident["country"] = country
    if scheme == M.NS_LEI:
        ident["iso7064_valid"] = lei_checksum_valid(value)
    ent["identifiers"].append(ident)
    return ident


def _lei_of(ent):
    return [i["value"] for i in ent["identifiers"] if i["scheme"] == M.NS_LEI]


def build_dataset(root=ROOT):
    root = pathlib.Path(root)
    dgsfp = load_dgsfp(root)
    manifest = load_manifest(root)
    midx = manifest_index(manifest)
    gleif = load_gleif(root)
    eiopa = load_eiopa(root)
    dgsfp_by_clave = {e["clave"]: e for e in dgsfp}

    entities = {}
    by_clave = {}
    by_lei = {}
    relations = {}
    observations = []

    def anchor_for(identifiers):
        for scheme in (M.NS_DGSFP, M.NS_LEI, M.NS_BDE_EU, M.NS_EIOPA):
            ids = [i for i in identifiers if i["scheme"] == scheme]
            if ids:
                i = sorted(ids, key=lambda x: (x["value"], x.get("country") or ""))[0]
                c = f"{i['country']}:" if i.get("country") else ""
                return f"ent:{scheme}:{c}{i['value']}"
        return None

    def log_merge(ent, basis, identifier, evidence):
        if basis not in MERGE_BASES:
            raise ValueError(f"non-exact merge basis: {basis}")
        for m in ent["merge_basis"]:
            if m["basis"] == basis and m["identifier"] == identifier:
                m["evidence"] = sorted(set(m["evidence"]) | set(evidence))
                return
        ent["merge_basis"].append({"basis": basis, "identifier": identifier,
                                   "evidence": sorted(set(evidence))})

    def register(ent):
        ent["entity_id"] = anchor_for(ent["identifiers"]) or M.content_id("ent", ent)
        entities[ent["entity_id"]] = ent
        for i in ent["identifiers"]:
            if i["scheme"] == M.NS_DGSFP:
                by_clave[i["value"]] = ent
            elif i["scheme"] == M.NS_LEI:
                by_lei.setdefault(i["value"], ent)
        return ent

    def merge_into(dst, src, basis, identifier, evidence):
        """Merge src into dst. basis MUST be an exact shared-identifier ground."""
        if basis not in MERGE_BASES:
            raise ValueError(f"non-exact merge basis: {basis}")
        for i in src["identifiers"]:
            di = _add_ident(dst, i["scheme"], i["value"], None, i.get("country"))
            for a in i["asserted_by"]:
                if a not in di["asserted_by"]:
                    di["asserted_by"].append(a)
        for k in ("registrations", "cross_border_operations", "source_assertions",
                  "conflicts", "snapshots", "diagnostics"):
            dst[k].extend(src[k])
        log_merge(dst, basis, identifier, evidence)
        entities.pop(src["entity_id"], None)
        for i in src["identifiers"]:
            if i["scheme"] == M.NS_LEI:
                by_lei[i["value"]] = dst

    def add_lei(ent, lei, aid):
        """Attach an LEI identifier; if another entity already claims it, merge."""
        other = by_lei.get(lei)
        if other is not None and other is not ent:
            merge_into(ent, other, "SHARED_LEI", f"lei:{lei}", [aid])
        _add_ident(ent, M.NS_LEI, lei, aid)
        by_lei[lei] = ent

    def add_rel(rel):
        relations[rel["edge_id"]] = rel

    # ---------------- provenance blocks ----------------
    prov_bde = make_prov("BDE", "ES", "data/raw/bde/lista-ic-es.csv", midx,
                         bde_snapshot_date(manifest, "lista-ic-es.csv"),
                         "bde_ic_list/0.1")
    prov_eiopa = make_prov("EIOPA", "EU", "data/raw/eiopa/eiopa_register.csv", midx,
                           "2026-09-13", "eiopa_register/0.1")
    prov_gleif = make_prov("GLEIF", "global", "data/raw/gleif/gleif_records.jsonl",
                           midx, "2026-09-13", "gleif_harvest/0.1")

    # ---------------- 1. DGSFP universe ----------------
    for e in dgsfp:
        clave, tipo = e["clave"], e["tipo"]
        prov = dict(e["source"])
        prov["jurisdiction"] = "ES"
        prov["evidence_tier"] = TIERS["DGSFP_RRPP"]
        prov["raw_file"] = "data/" + prov["raw_file"].replace("\\", "/")

        ent = M.empty_entity(DGSFP_KIND[tipo])
        subj = {"scheme": M.NS_DGSFP, "value": clave}

        a_reg = M.make_assertion(
            subj, "REGISTERED_AS",
            {"clave": clave, "tipo": tipo, "denominacion": e["denominacion"],
             "situacion": e["situacion"],
             "pais_origen": e.get("pais_origen") or None,
             "nif": e.get("nif") or None,
             "fecha_autorizacion": e.get("fecha_autorizacion") or None,
             "fecha_cancelacion": e.get("fecha_cancelacion") or None}, prov)
        a_name = M.make_assertion(subj, "PUBLISHES_NAME", e["denominacion"], prov)
        ent["source_assertions"] += [a_reg, a_name]
        ent["registrations"].append({"system": "DGSFP_RRPP", "register_key": clave,
                                     "register_type": tipo,
                                     "situacion": e["situacion"],
                                     "assertion": a_reg["assertion_id"]})
        _add_ident(ent, M.NS_DGSFP, clave, a_reg["assertion_id"])
        if (e.get("nif") or "").strip():
            _add_ident(ent, M.NS_NIF, e["nif"].strip(), a_reg["assertion_id"])
        lei = (e.get("lei") or "").strip().upper()
        if lei:
            a_lei = M.make_assertion(subj, "PUBLISHES_IDENTIFIER",
                                     {"scheme": M.NS_LEI, "value": lei}, prov)
            ent["source_assertions"].append(a_lei)
            add_lei(ent, lei, a_lei["assertion_id"])
        if tipo in ("E", "L"):
            a_hc = M.make_assertion(subj, "PUBLISHES_HOME_COUNTRY",
                                    {"pais_origen": e.get("pais_origen") or None,
                                     "iso": pais_to_iso(e.get("pais_origen"))}, prov)
            ent["source_assertions"].append(a_hc)
        if tipo == "L":
            a_op = M.make_assertion(subj, "ASSERTS_OPERATION",
                                    {"country": "ES", "regime": "LPS"}, prov)
            ent["source_assertions"].append(a_op)
            ent["cross_border_operations"].append(
                {"direction": "INTO_ES", "regime": "LPS", "country": "ES",
                 "asserted_by": "DGSFP_RRPP", "assertion": a_op["assertion_id"]})
            add_rel(M.make_relation(
                "OPERATES_IN_ES",
                [{"entity_id": None, "identifier": f"dgsfp:clave:{clave}"}],
                "EXACT", ["DGSFP_KEY"], [a_op["assertion_id"]],
                "DGSFP L-registration asserts freedom-of-services operation in ES"))
        ent["snapshots"].append({"raw_file": prov["raw_file"],
                                 "source_snapshot_date": prov["source_snapshot_date"]})
        register(ent)

    # ---------------- 2. BdE lista-ic-es ----------------
    e_matriz = {}
    bde_lei_pending = {}      # entity_id -> (lei, assertion_id)
    for r in load_bde(root / "data/raw/bde/lista-ic-es.csv"):
        sup = norm_dgsfp_key(r.get("CÓDIGO DE SUPERVISOR", ""))
        euc = r.get("CÓDIGO EUROPEO", "").strip()
        lei = r.get("LEI", "").strip().upper()
        a_row = M.make_assertion(
            {"scheme": M.NS_BDE_EU, "value": euc, "country": "ES"},
            "LISTS_ROW",
            {"list": "lista-ic-es", "nombre": r.get("NOMBRE"),
             "tipo_de_seguro": r.get("TIPO DE SEGURO") or None,
             "supervisor_code_raw": r.get("CÓDIGO DE SUPERVISOR") or None,
             "lei": lei or None,
             "entidad_matriz": r.get("ENTIDAD MATRIZ") or None}, prov_bde)
        ent = by_clave.get(sup) if sup else None
        if ent is None:
            ent = M.empty_entity("INSURANCE_UNDERTAKING")
            ent["source_assertions"].append(a_row)
            ent["registrations"].append(
                {"system": "BDE", "register_key": euc, "register_type": "IC_LIST_ES",
                 "situacion": None, "assertion": a_row["assertion_id"]})
            _add_ident(ent, M.NS_BDE_EU, euc, a_row["assertion_id"], "ES")
            if lei:
                add_lei(ent, lei, a_row["assertion_id"])
            register(ent)
            continue
        ent["source_assertions"].append(a_row)
        ent["registrations"].append(
            {"system": "BDE", "register_key": euc, "register_type": "IC_LIST_ES",
             "situacion": None, "assertion": a_row["assertion_id"]})
        _add_ident(ent, M.NS_BDE_SUP, sup, a_row["assertion_id"])
        _add_ident(ent, M.NS_BDE_EU, euc, a_row["assertion_id"], "ES")
        log_merge(ent, "SHARED_DGSFP_KEY", f"dgsfp:clave:{sup}",
                  [a_row["assertion_id"]])
        if lei:
            prior = _lei_of(ent)
            if not prior or lei in prior:
                add_lei(ent, lei, a_row["assertion_id"])
            else:
                # divergent LEI on the same register record: keep it in the
                # assertion (evidence) but out of canonical identifiers until
                # the subject is determined (see section 4 for branches).
                bde_lei_pending[ent["entity_id"]] = (lei, a_row["assertion_id"])
        add_rel(M.make_relation(
            "DGSFP_KEY_BDE_SUPERVISOR_CODE_EXACT",
            [{"entity_id": ent["entity_id"],
              "identifier": f"dgsfp:clave:{sup} == bde:european_code:ES:{euc}"}],
            "EXACT", ["DGSFP_KEY", "OFFICIAL_BRIDGE"], [a_row["assertion_id"]],
            "lista-ic-es row carries supervisor code + european code in one artifact"))
        matriz = (r.get("ENTIDAD MATRIZ") or "").strip()
        if matriz:
            e_matriz[ent["entity_id"]] = matriz

    # ---------------- 3. EIOPA register ----------------
    ei_home_by_lei = collections.defaultdict(list)
    ei_es_domestic = collections.defaultdict(list)
    ei_es_ops = collections.defaultdict(list)
    for r in eiopa:
        lei = r["LEI"].strip().upper()
        status = r["Cross border status"].strip()
        if status == "Domestic undertaking":
            if lei:
                ei_home_by_lei[lei].append(r)
            if r["Home Country"].strip() == "ES":
                ei_es_domestic[norm_dgsfp_key(r["Identification code"])].append(r)
        elif r["EU Country where the entity operates"].strip() == "ES" and lei:
            ei_es_ops[lei].append(r)

    def attach_eiopa_home(ent, h):
        """Attach the EIOPA home-undertaking row to ent (idempotent)."""
        lei = h["LEI"].strip().upper()
        subj = {"scheme": M.NS_EIOPA,
                "value": h["Identification code"].strip(),
                "country": h["Home Country"].strip()}
        existing = {a["assertion_id"] for a in ent["source_assertions"]}
        a = M.make_assertion(
            subj, "REGISTERED_AS",
            {"identification_code": h["Identification code"].strip(),
             "nca": h["Name of NCA"].strip(),
             "home_country": h["Home Country"].strip(),
             "official_name": h["Official name of the entity"].strip()}, prov_eiopa)
        if a["assertion_id"] not in existing:
            ent["source_assertions"] += [
                a,
                M.make_assertion(subj, "PUBLISHES_NAME",
                                 h["Official name of the entity"].strip(), prov_eiopa),
                M.make_assertion(subj, "PUBLISHES_HOME_COUNTRY",
                                 {"pais_origen": None,
                                  "iso": h["Home Country"].strip()}, prov_eiopa)]
            ent["registrations"].append(
                {"system": "EIOPA",
                 "register_key": h["Identification code"].strip(),
                 "register_type": "HOME_UNDERTAKING", "situacion": None,
                 "assertion": a["assertion_id"]})
            _add_ident(ent, M.NS_EIOPA, h["Identification code"].strip(),
                       a["assertion_id"], h["Home Country"].strip())
            _add_ident(ent, M.NS_LEI, lei, a["assertion_id"])
        return a

    def eiopa_home_entity(lei):
        """Get the entity for an EIOPA home LEI, creating it if needed."""
        ent = by_lei.get(lei)
        homes = sorted(ei_home_by_lei.get(lei, []),
                       key=lambda r: r["Identification code"])
        if ent is None:
            if not homes:
                return None
            ent = M.empty_entity("INSURANCE_UNDERTAKING")
            a = attach_eiopa_home(ent, homes[0])
            register(ent)
            return ent
        if homes:
            a = attach_eiopa_home(ent, homes[0])
            log_merge(ent, "SHARED_LEI", f"lei:{lei}", [a["assertion_id"]])
        return ent

    # ES domestic rows -> merge into DGSFP entities by clave
    for k, rows in ei_es_domestic.items():
        ent = by_clave.get(k)
        if not ent:
            continue
        h = sorted(rows, key=lambda r: r["LEI"])[0]
        lei = h["LEI"].strip().upper()
        a = attach_eiopa_home(ent, h)
        log_merge(ent, "SHARED_DGSFP_KEY", f"dgsfp:clave:{k}", [a["assertion_id"]])
        prior = _lei_of(ent)
        if lei and prior and lei not in prior:
            ent["conflicts"].append(M.make_conflict(
                "IDENTIFIER_LIFECYCLE_CONFLICT", M.CL_IDENTITY,
                [a["assertion_id"]],
                f"EIOPA asserts LEI {lei}; other source asserts {prior}"))
        if lei:
            add_lei(ent, lei, a["assertion_id"])
        add_rel(M.make_relation(
            "DGSFP_KEY_EIOPA_ID_EXACT",
            [{"entity_id": ent["entity_id"],
              "identifier": f"dgsfp:clave:{k} == "
                            f"eiopa:identification_code:{h['Identification code'].strip()}"}],
            "EXACT", ["DGSFP_KEY"], [a["assertion_id"]],
            "EIOPA identification code equals DGSFP clave (ES domestic only)"))
        dname = dgsfp_by_clave.get(k, {}).get("denominacion", "")
        if diag_name_agree(dname, h["Official name of the entity"]) == "different":
            ent["diagnostics"].append(
                {"kind": "NAME_DIFFERS_SAME_ID", "dgsfp": dname,
                 "eiopa": h["Official name of the entity"].strip()})

    # ---------------- 4. BdE parent resolution (E branches) ----------------
    home_lists = {}

    def bde_home_list(cc):
        if cc not in home_lists:
            p = root / f"data/raw/bde/lista-ic-{cc}.csv"
            if p.exists():
                home_lists[cc] = (
                    load_bde(p),
                    make_prov("BDE", cc.upper(), f"data/raw/bde/lista-ic-{cc}.csv",
                              midx,
                              bde_snapshot_date(manifest, f"lista-ic-{cc}.csv"),
                              "bde_ic_list/0.1"))
            else:
                home_lists[cc] = ([], None)
        return home_lists[cc]

    for eid, matriz in e_matriz.items():
        branch = entities[eid]
        cc = matriz[:2].lower()
        rows, prov_h = bde_home_list(cc)
        hits = [h for h in rows if h.get("CÓDIGO EUROPEO", "").strip() == matriz]
        beuc = next((i["value"] for i in branch["identifiers"]
                     if i["scheme"] == M.NS_BDE_EU), None)
        a_par = M.make_assertion(
            {"scheme": M.NS_BDE_EU, "value": beuc or eid},
            "ASSERTS_PARENT", {"entidad_matriz": matriz}, prov_bde)
        branch["source_assertions"].append(a_par)
        if not hits:
            observations.append(
                {"kind": "PARENT_NOT_RESOLVED", "entity_id": eid,
                 "entidad_matriz": matriz,
                 "detail": "parent code not found in BdE home list "
                           "(non-EEA country or snapshot lag)"})
            continue
        h = hits[0]
        plei = h.get("LEI", "").strip().upper()
        # assertion for the home-list row: always emitted, so every edge that
        # used the second artifact cites it.
        a_h = M.make_assertion(
            {"scheme": M.NS_BDE_EU, "value": matriz, "country": cc.upper()},
            "LISTS_ROW",
            {"list": f"lista-ic-{cc}", "nombre": h.get("NOMBRE"),
             "tipo_de_seguro": h.get("TIPO DE SEGURO") or None,
             "lei": plei or None}, prov_h)

        parent = by_lei.get(plei) if plei else None
        if parent is None:
            parent = M.empty_entity("INSURANCE_UNDERTAKING")
            parent["source_assertions"].append(a_h)
            parent["registrations"].append(
                {"system": "BDE", "register_key": matriz,
                 "register_type": f"IC_LIST_{cc.upper()}", "situacion": None,
                 "assertion": a_h["assertion_id"]})
            _add_ident(parent, M.NS_BDE_EU, matriz, a_h["assertion_id"], cc.upper())
            register(parent)
            if plei:
                add_lei(parent, plei, a_h["assertion_id"])
        else:
            if a_h["assertion_id"] not in {a["assertion_id"]
                                           for a in parent["source_assertions"]}:
                parent["source_assertions"].append(a_h)
                parent["registrations"].append(
                    {"system": "BDE", "register_key": matriz,
                     "register_type": f"IC_LIST_{cc.upper()}", "situacion": None,
                     "assertion": a_h["assertion_id"]})
            _add_ident(parent, M.NS_BDE_EU, matriz, a_h["assertion_id"], cc.upper())
            if plei:
                log_merge(parent, "SHARED_LEI", f"lei:{plei}",
                          [a_h["assertion_id"]])

        same_legal_person = parent is branch
        if same_legal_person:
            # branch ficha published the home undertaking's LEI: one legal
            # person, two registrations. No self-edge.
            branch["diagnostics"].append(
                {"kind": "BRANCH_FICHA_PUBLISHES_HOME_LEI", "lei": plei,
                 "note": "DGSFP E-ficha LEI equals resolved parent LEI — "
                         "branch and home are the same legal person"})
        else:
            add_rel(M.make_relation(
                "BRANCH_OF",
                [{"entity_id": eid}, {"entity_id": parent["entity_id"]}],
                "EXACT", ["BDE_PARENT_CODE"] + (["LEI"] if plei else []),
                [a_par["assertion_id"], a_h["assertion_id"]],
                "branch -> home undertaking"))
        # single-endpoint edge when the resolution lands on the same legal
        # person (branch ficha published the home LEI); two endpoints otherwise
        endpoints = ([{"entity_id": eid,
                      "identifier": f"bde:european_code:{cc.upper()}:{matriz}"}]
                     if same_legal_person else
                     [{"entity_id": eid,
                       "identifier": f"bde:european_code:{cc.upper()}:{matriz}"},
                      {"entity_id": parent["entity_id"]}])
        add_rel(M.make_relation(
            "BRANCH_PARENT_CODE_RESOLVES_HOME_ENTITY", endpoints,
            "EXACT", ["BDE_PARENT_CODE"],
            [a_par["assertion_id"], a_h["assertion_id"]],
            "ENTIDAD MATRIZ resolves to one row in the home-country IC list"))

        # parent LEI -> EIOPA home undertaking (exact)
        if plei and plei in ei_home_by_lei:
            eh = eiopa_home_entity(plei)
            if eh is not parent:
                merge_into(parent, eh, "SHARED_LEI", f"lei:{plei}",
                           [a_h["assertion_id"]])
            eiopa_aid = next((r["assertion"] for r in parent["registrations"]
                              if r["system"] == "EIOPA"), None)
            eiopa_code = next((r["register_key"] for r in parent["registrations"]
                               if r["system"] == "EIOPA"), None)
            if eiopa_aid:
                add_rel(M.make_relation(
                    "HOME_LEI_MATCHES_EIOPA_HOME_UNDERTAKING",
                    [{"entity_id": parent["entity_id"],
                      "identifier": f"lei:{plei} == eiopa:{eiopa_code}"}],
                    "EXACT", ["LEI"], [a_h["assertion_id"], eiopa_aid],
                    "home-list row LEI equals EIOPA home undertaking LEI"))

    # divergent BdE-ES LEIs whose subject could not be determined
    for eid, (lei, aid) in bde_lei_pending.items():
        ent = entities.get(eid)
        if ent is None:
            continue
        leis = _lei_of(ent)
        if lei in leis:
            continue
        parent_leis = set()
        for r in relations.values():
            if (r["relation_type"] == "BRANCH_PARENT_CODE_RESOLVES_HOME_ENTITY"
                    and r["endpoints"][0]["entity_id"] == eid):
                # two endpoints -> distinct parent entity; one -> same subject
                peid = (r["endpoints"][1]["entity_id"] if len(r["endpoints"]) > 1
                        else eid)
                parent_leis |= set(_lei_of(entities.get(peid, {"identifiers": []})))
        parent_leis |= set(leis)
        if lei in parent_leis:
            _add_ident(ent, M.NS_LEI, lei, aid)
        else:
            ent["conflicts"].append(M.make_conflict(
                "IDENTIFIER_SUBJECT_UNDETERMINED", M.CL_IDENTIFIER_ASSIGNMENT,
                [aid], f"BdE lista-ic-es asserts LEI {lei} for this register "
                       f"key, but DGSFP/other sources identify the subject as "
                       f"{leis or parent_leis}; subject of {lei} undetermined "
                       f"(possibly a branch-establishment LEI)"))

    # ---------------- 5. LPS (L entities) ----------------
    ei_by_name = collections.defaultdict(list)
    for lei_, rows in ei_home_by_lei.items():
        h = sorted(rows, key=lambda r: r["Identification code"])[0]
        ei_by_name[(norm_name(h["Official name of the entity"]),
                    h["Home Country"].strip())].append((lei_, h))

    for e in dgsfp:
        if e["tipo"] != "L":
            continue
        ent = by_clave[e["clave"]]
        lei = (e.get("lei") or "").strip().upper()
        if not lei:
            continue  # UNRESOLVED: registered entity, identity not resolvable
        home_rows = ei_home_by_lei.get(lei, [])
        if home_rows:
            eh = eiopa_home_entity(lei)
            h0 = sorted(home_rows, key=lambda r: r["Identification code"])[0]
            iso = pais_to_iso(e.get("pais_origen"))
            home_cc = h0["Home Country"].strip()
            if iso and home_cc and iso != home_cc:
                ids = [a["assertion_id"] for a in ent["source_assertions"]
                       if a["predicate"] == "PUBLISHES_HOME_COUNTRY"]
                ent["conflicts"].append(M.make_conflict(
                    "HOME_COUNTRY_DISAGREEMENT", M.CL_ATTRIBUTE, ids,
                    f"DGSFP asserts {e.get('pais_origen')} ({iso}); "
                    f"EIOPA home country is {home_cc}"))
            off = h0["Official name of the entity"].strip()
            if diag_name_agree(e["denominacion"], off) == "different":
                ent["diagnostics"].append({"kind": "NAME_DIFFERS_SAME_ID",
                                           "dgsfp": e["denominacion"],
                                           "eiopa": off})
            add_rel(M.make_relation(
                "LPS_REGISTER_KEY_PUBLISHES_LEI",
                [{"entity_id": ent["entity_id"],
                  "identifier": f"dgsfp:clave:{e['clave']} == lei:{lei}"}],
                "EXACT", ["OFFICIAL_BRIDGE", "LEI"],
                [a["assertion_id"] for a in ent["source_assertions"]
                 if a["predicate"] == "PUBLISHES_IDENTIFIER"],
                "RRPP L-ficha publishes LEI; same LEI on EIOPA home undertaking"))
            if lei not in ei_es_ops:
                ids = [a["assertion_id"] for a in ent["source_assertions"]
                       if a["predicate"] in ("PUBLISHES_IDENTIFIER",
                                             "ASSERTS_OPERATION")]
                ent["conflicts"].append(M.make_conflict(
                    "GROUP_LEI_VS_OPERATOR", M.CL_IDENTIFIER_ASSIGNMENT, ids,
                    "LEI resolves to an EIOPA home with no FTS operation into ES; "
                    "DGSFP may publish the group LEI, not the operator's"))
        else:
            # Possible identifier lifecycle: an EIOPA home undertaking with the
            # same normalized name + home country operates into ES under a
            # different LEI. This is a CANDIDATE, not a merge: names never
            # create canonical identity.
            iso = pais_to_iso(e.get("pais_origen"))
            cands = [(l2, h) for l2, h in
                     ei_by_name.get((norm_name(e["denominacion"]), iso or ""), [])
                     if l2 != lei and l2 in ei_es_ops]
            if cands:
                other_lei, h = sorted(cands)[0]
                other = eiopa_home_entity(other_lei)
                own_aids = [a["assertion_id"] for a in ent["source_assertions"]
                            if a["predicate"] in ("PUBLISHES_IDENTIFIER",
                                                  "PUBLISHES_NAME",
                                                  "PUBLISHES_HOME_COUNTRY")]
                other_aids = [a["assertion_id"] for a in other["source_assertions"]
                              if a["predicate"] in ("REGISTERED_AS",
                                                    "PUBLISHES_NAME",
                                                    "PUBLISHES_HOME_COUNTRY")]
                ent["conflicts"].append(M.make_conflict(
                    "IDENTIFIER_LIFECYCLE_CONFLICT", M.CL_IDENTITY,
                    own_aids + other_aids,
                    f"DGSFP publishes LEI {lei} (stale/inactive); EIOPA lists a "
                    f"same-named {iso} undertaking operating into ES under LEI "
                    f"{other_lei} ({h['Identification code'].strip()}). "
                    f"Candidate successor only — no exact bridge in snapshot."))
                ent["diagnostics"].append(
                    {"kind": "SAME_SUBJECT_DIFFERENT_IDENTIFIER",
                     "dgsfp_lei": lei, "eiopa_lei": other_lei,
                     "basis": "identical normalized name + home country + ES "
                              "operation (documented G0 gap; diagnostic only)"})
                add_rel(M.make_relation(
                    "IDENTIFIER_SUCCESSOR_CANDIDATE",
                    [{"entity_id": ent["entity_id"],
                      "identifier": f"lei:{lei}"},
                     {"entity_id": other["entity_id"],
                      "identifier": f"lei:{other_lei}"}],
                    "UNRESOLVED", ["NONE"], own_aids + other_aids,
                    "same normalized name + home country + ES operation; "
                    "requires an official LEI-successor bridge to merge"))

    # ---------------- 6. EIOPA operations into ES ----------------
    for lei_, ops in ei_es_ops.items():
        ent = eiopa_home_entity(lei_)
        if ent is None:
            ent = M.empty_entity("UNDERTAKING")
            register(ent)
            add_lei(ent, lei_, None)
        for r in ops:
            a = M.make_assertion(
                {"scheme": M.NS_LEI, "value": lei_}, "ASSERTS_OPERATION",
                {"country": "ES", "regime": r["Cross border status"].strip(),
                 "operation_start": r["Operation Start Date"] or None}, prov_eiopa)
            ent["source_assertions"].append(a)
            ent["cross_border_operations"].append(
                {"direction": "INTO_ES", "regime": r["Cross border status"].strip(),
                 "country": "ES", "asserted_by": "EIOPA",
                 "assertion": a["assertion_id"]})
            add_rel(M.make_relation(
                "OPERATES_IN_ES",
                [{"entity_id": ent["entity_id"], "identifier": f"lei:{lei_}"}],
                "EXACT", ["LEI"], [a["assertion_id"]],
                f"EIOPA {r['Cross border status'].strip()} operation into ES"))
        has_l = any(i["scheme"] == M.NS_DGSFP and i["value"].startswith("L")
                    for i in ent["identifiers"])
        has_branch_child = any(
            r2["relation_type"] == "BRANCH_OF"
            and r2["endpoints"][1]["entity_id"] == ent["entity_id"]
            for r2 in relations.values())
        if (not has_l and any(o["regime"] in FTS_STATUSES
                              for o in ent["cross_border_operations"]
                              if o["asserted_by"] == "EIOPA")):
            add_rel(M.make_relation(
                "LPS_REGISTRATION_LINK",
                [{"entity_id": ent["entity_id"]},
                 {"identifier": "dgsfp:clave:L????",
                  "note": "expected DGSFP LPS registration, not found in snapshot"}],
                "UNRESOLVED", ["NONE"], [],
                "EIOPA asserts FTS operation into ES but no L-key can be "
                "exactly linked"))
        if (not has_branch_child
                and any(o["regime"] in BRANCH_STATUSES
                        for o in ent["cross_border_operations"]
                        if o["asserted_by"] == "EIOPA")):
            add_rel(M.make_relation(
                "BRANCH_REGISTRATION_LINK",
                [{"entity_id": ent["entity_id"]},
                 {"identifier": "dgsfp:clave:E????",
                  "note": "expected DGSFP branch registration, not found in snapshot"}],
                "UNRESOLVED", ["NONE"], [],
                "EIOPA asserts branch presence into ES but no E-key can be "
                "exactly linked"))

    # ---------------- 7. GLEIF resolution ----------------
    for ent in list(entities.values()):
        for i in ent["identifiers"]:
            if i["scheme"] != M.NS_LEI:
                continue
            g = gleif.get(i["value"])
            if not g:
                continue
            a = M.make_assertion(
                {"scheme": M.NS_LEI, "value": i["value"]}, "LEI_RECORD",
                {"entityStatus": g.get("entityStatus"),
                 "legalName": g.get("legalName"),
                 "jurisdiction": g.get("jurisdiction"),
                 "regStatus": g.get("regStatus")}, prov_gleif)
            ent["source_assertions"].append(a)
            if a["assertion_id"] not in i["asserted_by"]:
                i["asserted_by"].append(a["assertion_id"])
            log_merge(ent, "SHARED_LEI", f"lei:{i['value']}", [a["assertion_id"]])
            add_rel(M.make_relation(
                "LEI_RESOLVES_GLEIF",
                [{"entity_id": ent["entity_id"], "identifier": f"lei:{i['value']}"}],
                "EXACT", ["LEI"], [a["assertion_id"]],
                f"GLEIF record present; status {g.get('entityStatus')}"))

    # ---------------- 8. status + deterministic ordering ----------------
    for ent in entities.values():
        # an entity merged with a home-undertaking registration is the legal
        # person itself (e.g. an E-branch whose ficha carries the home LEI):
        # branch-ness then lives in registrations, not in entity_kind.
        if (ent["entity_kind"] in ("EEA_BRANCH", "UNDERTAKING")
                and any(r["register_type"] == "HOME_UNDERTAKING"
                        or r["register_type"].startswith("IC_LIST_")
                        and r["register_type"] != "IC_LIST_ES"
                        for r in ent["registrations"])):
            ent["entity_kind"] = "INSURANCE_UNDERTAKING"
        id_conflict = any(c["level"] == M.CL_IDENTITY for c in ent["conflicts"])
        has_lei = bool(_lei_of(ent))
        is_l_registration_only = (
            ent["entity_kind"] == "UNDERTAKING" and not has_lei
            and any(i["scheme"] == M.NS_DGSFP and i["value"].startswith("L")
                    for i in ent["identifiers"]))
        if id_conflict:
            ent["identity_status"] = "CONFLICT"
        elif has_lei or (not is_l_registration_only and any(
                i["scheme"] in (M.NS_DGSFP, M.NS_BDE_EU, M.NS_EIOPA)
                for i in ent["identifiers"])):
            ent["identity_status"] = "EXACT"
        else:
            ent["identity_status"] = "UNRESOLVED"
        systems = ({r["system"] for r in ent["registrations"]}
                   | {o["asserted_by"] for o in ent["cross_border_operations"]})
        ent["source_coverage"] = ("MULTI_SOURCE"
                                  if len(systems & PRESENCE_SYSTEMS) >= 2
                                  else "SOURCE_ONLY")
        ent["identifiers"].sort(key=lambda i: (i["scheme"], i.get("country") or "",
                                               i["value"]))
        for i in ent["identifiers"]:
            i["asserted_by"].sort()
        ent["source_assertions"].sort(key=lambda a: a["assertion_id"])
        ent["conflicts"].sort(key=lambda c: c["conflict_id"])
        ent["merge_basis"].sort(key=lambda m: (m["basis"], m["identifier"]))
        ent["registrations"].sort(key=lambda r: (r["system"], r["register_key"]))
        ent["cross_border_operations"].sort(key=lambda o: (o["country"], o["regime"],
                                                           o["asserted_by"]))
        snaps = {(a["provenance"]["raw_file"],
                  a["provenance"]["source_snapshot_date"])
                 for a in ent["source_assertions"]}
        snaps |= {(s["raw_file"], s["source_snapshot_date"])
                  for s in ent["snapshots"] if isinstance(s, dict)}
        ent["snapshots"] = [{"raw_file": f, "source_snapshot_date": d}
                            for f, d in sorted(snaps)]

    entities_list = sorted(entities.values(),
                           key=lambda e: (e["entity_kind"], e["entity_id"]))
    relations_list = sorted(relations.values(),
                            key=lambda r: (r["relation_type"], r["edge_id"]))
    observations.sort(key=lambda o: (o["kind"], o.get("entity_id") or ""))

    snapshot_dates = sorted({a["provenance"]["source_snapshot_date"]
                             for e in entities_list for a in e["source_assertions"]
                             if a["provenance"]["source_snapshot_date"]})
    return {
        "schema_version": SCHEMA_VERSION,
        "generated_at": max(snapshot_dates) if snapshot_dates else None,
        "parser_version": PARSER_VERSION,
        "entities": entities_list,
        "relations": relations_list,
        "observations": observations,
        "counts": {
            "entities": len(entities_list),
            "relations": len(relations_list),
            "by_identity_status": dict(collections.Counter(
                e["identity_status"] for e in entities_list)),
            "by_source_coverage": dict(collections.Counter(
                e["source_coverage"] for e in entities_list)),
            "by_kind": dict(collections.Counter(e["entity_kind"]
                                              for e in entities_list)),
        },
    }
