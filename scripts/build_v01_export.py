# -*- coding: utf-8 -*-
"""Build the OpenDGSFP v0.1 canonical dataset and write the deterministic
JSONL export + manifest under data/derived/v0.1/.

Usage: python -m scripts.build_v01_export  (from repo root)
"""
import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent.parent))

from opendgsfp.build import build_dataset
from opendgsfp.export import write_export


def main():
    ds = build_dataset()
    data_path, manifest_path = write_export(ds)
    print(f"schema_version : {ds['schema_version']}")
    print(f"generated_at   : {ds['generated_at']}  (derived from source snapshots)")
    print(f"entities       : {ds['counts']['entities']}  {ds['counts']['by_identity_status']}")
    print(f"relations      : {ds['counts']['relations']}")
    print(f"wrote          : {data_path}")
    print(f"wrote          : {manifest_path}")


if __name__ == "__main__":
    main()
