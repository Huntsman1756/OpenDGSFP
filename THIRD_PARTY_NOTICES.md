# Third-party notices

## Vendored / submodule dependencies

### fabio-rovai/insurance-register-ontology

- **Location:** `third_party/insurance-register-ontology` (git submodule)
- **Upstream:** https://github.com/fabio-rovai/insurance-register-ontology
- **Pinned commit:** `2f7f9dc8317aab1bf27a623832c218b2399aa88b`
- **License:** dual —
  - pipeline code (`pipeline/`, `scripts/`, `queries/`): **MIT**
  - ontology, SKOS registry, SHACL shapes, documentation: **CC BY 4.0**
- **Usage in OpenDGSFP:** reused mechanisms only — the EIOPA register
  export/postback approach and the ISO 7064 (MOD 97-10) LEI checksum.
  The Spanish DGSFP/BdE integration is OpenDGSFP-specific and is not
  derived from the donor.
- **Modifications:** none to the donor tree; OpenDGSFP code lives outside
  `third_party/`.

## Official data sources

`data/raw/` and `data/derived/` contain material captured from official
public registers for reproducibility of the frozen G0 snapshot. These
materials are **not** covered by the repository's MIT license; each
remains subject to its publisher's terms of use.

| Source | Material | Publisher terms |
|--------|----------|-----------------|
| DGSFP RRPP | 2,759 insurer detail pages (`data/raw/dgsfp/rrpp_details/`) | Dirección General de Seguros y Fondos de Pensiones — public register, ministerio de Economía; reuse per Spanish public-sector information rules (Ley 37/2007 / RD 1495/2011) |
| Banco de España | IC entity classification lists (`data/raw/bde/lista-ic-*.csv`) | Banco de España — statistical dissemination; attribution required; see bde.es "Aviso legal" |
| EIOPA | Register of insurance undertakings (`data/raw/eiopa/`) | EIOPA public register; reuse per EIOPA/EU reuse policy |
| GLEIF | LEI records (`data/raw/gleif/`) | GLEIF publishes LEI data under **CC0** |

No personal data is intentionally collected beyond what these official
registers publish (registry data of legal persons).
