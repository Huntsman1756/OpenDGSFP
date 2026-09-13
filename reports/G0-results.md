# G0 — RESULTS: SOURCE ACCESS + EXACT IDENTITY CROSSWALK

Ejecutado: 2026-09-13 · Proyecto: OpenDGSFP · Estado: **G0 CERRADO — VEREDICTO ACEPTADO Y CONGELADO (2026-09-13)**

---

## 1. Estado de cada gate

| Gate | Alcance | Resultado |
|---|---|---|
| **G0-A** — Entidades españolas | Población completa Activa C/M/P/R (137) + muestra estratificada 20 | **PASS** (todas las comprobaciones 100%) |
| **G0-B1** — Sucursales EEE en España | Población BdE E-rows (70) ↔ DGSFP E-claves + muestra 12 países | **PASS** (cadena exacta 57/57 donde hay código de matriz; residual documentado) |
| **G0-B2** — LPS | Población completa L (1.580); filtro: `situacion='Activa'` → 825 | **PASS_WITH_OFFICIAL_BRIDGE** (LEI exacto donde DGSFP lo publica) + **DOCUMENTED_GAP acotado** (616 claves sin LEI + 1 con LEI sin home: L1522) |
| **G0-C** — Pensiones | Muestra: 2 gestoras, 5 fondos, 3 planes | **PASS** (crosswalk exacto; IORP EIOPA 401 documentado) |
| **G0-D** — Intermediarios | Caracterización PUI completa (56.105 filas) | **PASS** (caracterización; `EIOPA_ENTITY_JOIN_EXPECTED = FALSE`) |

Criterio de salida: `A=PASS ✓ · B1=PASS ✓ · B2 cerrado con resultado permitido ✓ · no fuzzy→canonical ✓ · provenance completa ✓ · snapshots ✓ · reproducción documentada ✓`

## 2. Tablas de cobertura

### 2.1 G0-A — Activa C/M/P/R (población completa, n=137)

| Comprobación | C (104) | M (28) | P (2) | R (3) | Total |
|---|---|---|---|---|---|
| DGSFP_KEY_UNIQUE (clave→1 ficha, enumeración determinista) | 104 | 28 | 2 | 3 | **137/137** |
| DGSFP_KEY_BDE_SUPERVISOR_CODE_EXACT | 104 | 28 | 2 | 3 | **137/137** |
| DGSFP_KEY_EIOPA_ID_EXACT | 104 | 28 | 2 | 3 | **137/137** |
| DGSFP_LEI_AVAILABLE | 104 | 28 | 2 | 3 | **137/137** |
| BDE_LEI_AVAILABLE | 104 | 28 | 2 | 3 | **137/137** |
| EIOPA_LEI_AVAILABLE | 104 | 28 | 2 | 3 | **137/137** |
| BDE_LEI_EIOPA_LEI_EXACT | 104 | 28 | 2 | 3 | **137/137** |
| GLEIF_LEI_EXACT (registro + ISO 7064) | 104 | 28 | 2 | 3 | **137/137** |
| Diagnóstico nombre DGSFP vs EIOPA = *different* | 0 | 0 | 0 | 0 | **0** |

### 2.2 G0-B1 — Sucursales (n=70 filas BdE con código supervisor E)

| Comprobación | Resultado |
|---|---|
| DGSFP_E_KEY_UNIQUE / RRPP_E_KEY_EXPOSED_LIVE | 70/70 (69 Activa en RRPP) |
| BDE_E_SUPERVISOR_CODE_MATCH (clave DGSFP == código BdE) | **70/70** |
| BDE_PARENT_EU_CODE_PRESENT (ENTIDAD MATRIZ) | 60/70 (85,7%) |
| BDE_PARENT_CODE_RESOLVES_HOME_ENTITY (lista del país de origen) | 57/60 con código (57/70 total) |
| BDE_PARENT_LEI_AVAILABLE | 57/70 (81,4%) |
| BDE_HOME_LEI_EIOPA_LEI_MATCH (LEI de matriz == EIOPA home) | **57/57 = 100%** de los resueltos |
| EIOPA ES operation row (LEI de matriz, cualquier estado) | 54/70 (46 `EEA branch` + 8 clasificadas `EEA FPS`) |
| GLEIF_LEI_EXACT (LEI de matriz) | 57/57 |
| `BDE_PARENT_CODE_EIOPA_ID_MATCH` (DIAGNÓSTICO, no load-bearing) | **0/70** — los esquemas nunca coinciden |
| ANEXO_III_E_KEY_MATCH (Anexo III de la memoria DGSFP) | **PENDIENTE DE LOCALIZACIÓN** — el artefacto no fue localizado en línea en esta sesión; el mapping E-clave queda soportado por BdE (T1) + RRPP (T2). Pendiente: descargar el PDF de la memoria anual y verificar. |
| LEI propio de sucursal — RRPP | 22/70 (31,4%) |
| LEI propio de sucursal — BdE fila ES | 11/70 (15,7%) |

Países de las matrices resueltas: FR 15, LU 11, DE 10, IE 9, BE 7, PT 2, SE/IT/MT/GB/MX/LI 1.

### 2.3 G0-B2 — LPS (población completa, 825 Activa)

**Filtro de universo**: De las 1.580 fichas L capturadas, se seleccionan únicamente las `situacion='Activa'` (825 registros). Las 755 restantes tienen situación `Inactiva`, `Cancelada` u otro estado no operativo. Este filtro es reproducible: `build_g0b2.py` aplica `e["situacion"] == "Activa"` sobre el JSONL parseado.

| Concepto | Resultado |
|---|---|
| RRPP_L_KEY_EXPOSED_LIVE | ✓ (fichas L capturadas; ejemplo documental: L0419, L1160) |
| RRPP_L_EXPORT_FIELDS | clave, denominación, país origen, LEI (25,3%), NIF (vacío), situación, dirección, fechas |
| RRPP_L_DETAIL_FIELDS | ídem — **sin home NCA ni home identification code**; sin export server-side |
| RRPP_L_LEI_AVAILABLE | 209/825 (25,3%) |
| EIOPA_HOME_EXACT_BY_LEI (entre las 209) | **208/209** |
| EIOPA_HOME_COUNTRY_MATCH (país RRPP == Home Country EIOPA) | 206/208 (99,0%) |
| EIOPA_ES_OPERATION_PRESENT (fila FTS en ES) | 168/825 |
| GLEIF_LEI_EXACT (entre las 209) | **209/209** |
| **Resultado** | 166 PASS_EXACT · 42 PASS_EXACT_NO_ES_OP · 616 DOCUMENTED_GAP (sin LEI) · 1 DOCUMENTED_GAP con LEI sin home (L1522) · **total sin resolución exacta = 617** |
| Diagnóstico nombre DGSFP vs EIOPA = *different* (entre LEI-junction) | 29/208 (13,9%) — DGSFP usa denominaciones comerciales; razón adicional para prohibir el nombre como identidad |

**Unidades de recuento (no mezclar)**: DGSFP L Activa = 825 *registros LPS en España*; EIOPA = 727 *LEI distintos con operación FTS hacia ES*; filas EIOPA EEA FPS ES = operaciones, no entidades.

### 2.4 G0-C — Pensiones (muestra)

| Unidad | Claves | Crosswalk exacto |
|---|---|---|
| Gestoras (DGSFP_MANAGER_KEY) | G0002, G0021 (de 49) | LEI en ficha ✓ · GLEIF ✓ · EIOPA home (insurer) `C0628`/`C0611` ✓ |
| Fondos (DGSFP_FUND_KEY) | F0050, F0016, F0131, F1131, F1989 (de 1.157) | LEI en ficha ✓ · BdE lista-pf-es por LEI **5/5** ✓ · GLEIF ✓ · clave gestora y depositaria exactas en ficha ✓ |
| Planes (DGSFP_PLAN_KEY) | N0002, N0003, N0007 | clave ✓ · enlace exacto plan→fondo (F0151, F0001, F0353) ✓ · sin LEI (los planes no son unidades de identidad jurídica) |

### 2.5 G0-D — PUI (universo completo, caracterización)

56.105 registros · campos: `clave, claveRegistro, razonSocial, claseMediador, situacion, sLEI, descripcion` · clases: Agente exclusivo PF 39.202, Agente exclusivo PJ 10.901, Corredor PJ 3.859, Corredor PF 1.398, vinculados 624, OBS 45, corredor de reaseguros 76 · **sLEI presente en 195 (0,35%)** · situacion=0 en todas las filas devueltas · `EIOPA_ENTITY_JOIN_EXPECTED = FALSE` registrado.

## 3. Residuos y excepciones

1. **BdE lista sin matriz (10/70)**: 7 sucursales nuevas (E0253-E0261, autorizadas recientemente) + E0155, E0189, E0212, E0234 — la lista de estadísticas BdE (2026-09-11) va por detrás del registro DGSFP (2026-09-13). Desfase de snapshot, no fallo de identidad.
2. **Matrices no EEE (3)**: E0223 (MX), E0235 (GB), E0218 (LI) — fuera de las listas UE de BdE (LI tampoco tiene lista). Resolución futura vía EIOPA/GLEIF por LEI si la fuente lo publica.
3. **L1522 — desacuerdo LEI (TT Club Mutual Insurance N.V.)**: RRPP publica `7245004QN0BFE9Q9EV42` (GLEIF: INACTIVE); EIOPA lista la misma entidad con `724500D3EHHJWKLWY913`. Ambos exactos por separado; **no se fusionan silenciosamente**; el desacuerdo queda representado.
4. **L1319 — país de origen en desacuerdo (USAA EU DAC)**: RRPP dice Irlanda; EIOPA home por LEI es Luxemburgo (CAA). Re-domiciliación o dato obsoleto en DGSFP. Documentado.
5. **42 PASS_EXACT_NO_ES_OP**: LEI resuelve la home en EIOPA, pero EIOPA no tiene fila de operación hacia ES (ej. Generali S.p.A. "SUC. LUXEMBURGO" — la operación ES corre bajo la filial luxemburguesa, no bajo el LEI de la matriz italiana). Clase estructural identificada: DGSFP a veces publica el LEI del grupo, no el de la entidad operadora.
6. **Search endpoint del RRPP de aseguradoras no reproducible por HTTP crudo** (error genérico del servidor ante 12+ variantes de payload). Las secciones pensiones/PUI sí devuelven arrays JSON completos. Mitigado con enumeración por clave (oráculo 200/500).
7. **23 filas BdE ES sin código de supervisor**: mutualidades catalanas pequeñas presentes en estadística BdE sin clave DGSFP publicada.
8. **Población**: RRPP contiene tipos adicionales (`RE` Reaseg. Extranjeras — espacio de claves vacío; situación `Otro` en 18 claves C/M). Requiere revisión en fase siguiente.

## 4. Hashes de fuentes (extracto; lista completa en `reports/g0-source-hashes.json` y `evidence/source-manifest.json`)

| Fuente | SHA-256 |
|---|---|
| DGSFP RRPP home (2026-09-13) | `9d2fafe1da39014c59b4528f3139cb6860a767bcaace40bae1429a5a5e373890` |
| DGSFP capture log (2.759 fichas) | `ba6c5653cd9e7879b6cda2e0859d988a227fc649fe7eaa9997f52770b687bf35` |
| DGSFP PUI universe JSON (10,7 MB) | `a515fc9839ff4277abbbf09ee47ea157453d156cd59dd6962b7efc7b0f6490e9` |
| DGSFP fondos JSON (1.157) | `d234c49425b2f4f4130b198afaf4743daba4583bb07a21d357026da46725b650` |
| BdE lista-ic-es.csv | `b504b6ac1634dc54b9c15ee029fca93e3a7513df967579d5d7b08068276d377b` |
| BdE lista-ic-de.csv | `f736262c399871cc536f54b96ccfe3b6824d26fc97c9fb258f42950355d9ba9b` |
| BdE lista-ic-fr.csv | `74a9c5b111dd31da9fb632c3b40ef3619e25a48850b4754cf64abe736e544f68` |
| BdE lista-ic-lu.csv | `50cc33c3bfcad2dabf3357aa08cc3fc0a8adb8c0266490ad8254a6b0371300cf` |
| BdE lista-ic-ie.csv | `22eba3ecf89bdca0e4c99da1e3dc8ca70d0cc59403b0f3ae4838a6cca59bace5` |
| BdE lista-pf-es.csv | `7e8b70a4a312710325076973ca4f712edbb351009046f8b8e8a1ab4df97b64b3` |
| EIOPA register CSV (34.166 filas) | `8431647b41893e6c6431c19064445b541c56ae082d41ce22bb38580eb604995a` |
| GLEIF records JSONL (383) | `272a60203901016637d4df55bdb25bf674fdced39e007c478f05093493fdc206` |
| Evidence ledger (123 edges) | `9182ea06318c0ae28bf15a55d4410c26945dca9dace4582e9933646d5181134a` |

## 5. Aristas demostradas (ledger completo: `evidence/evidence-ledger.json`, 123 registros)

**Desglose**: A 44 + B1 48 + B2 12 + C 17 = **121 aristas de gate** + 2 mecanismos (T4_DONOR) = 123 totales. De las 121 de gate, **118 son canónicas** y 3 son DOCUMENTED_GAP (B2: L0419, L1160, L1522 — sin resolución exacta). Los 2 mecanismos son canónicos. **Total canónico = 120**.

- **G0-A (44 edges)** — 20 entidades estratificadas (C12/M4/P2/R2), 4 aristas canónicas cada una:
  - `DGSFP clave → LEI` (T2, ficha viva, hash por fichero)
  - `DGSFP clave == BdE CÓDIGO DE SUPERVISOR` (T3, exacto, normalizado)
  - `DGSFP clave == EIOPA Identification code (+ LEI igual)` (T3)
  - `LEI → GLEIF record` (T0, ISO 7064 + registro)
- **G0-B1 (48 edges)** — 12 sucursales (DE/FR/LU/IE/BE/PT), cadena completa:
  - `clave E == BdE supervisor code` → `ENTIDAD MATRIZ == CÓDIGO EUROPEO en lista del país` → `LEI de matriz (BdE home) == LEI en EIOPA home` → `GLEIF`.
  - Cadenas reproducidas idénticas a la evidencia previa: E0193→DEA00PQ→AGCS SE→`F240A7PWJB2BLKELB442`; E0210→DEA3J2C→ARAG SE→`391200QKNZJ8J1XWFE16`; E0238→FR722057460→AXA France IARD→`969500798WFE82RZZU93`; E0226→LURCSB0218806→AIG Europe S.A.→`213800SCCLMKOWSSX732` (tests automatizados).
- **G0-B2 (12 edges)** — 9 PASS_EXACT multi-país (clave L + LEI exacto → EIOPA home → GLEIF) + 3 registros DOCUMENTED_GAP (L0419, L1160, L1522).
- **G0-C (17 edges)** — fondo→gestora por clave exacta; fondo LEI == BdE PF LEI; gestora LEI == EIOPA insurer row; plan→fondo por clave exacta.
- **Mecanismos (2, T4_DONOR)** — replay postback EIOPA y harvest GLEIF reutilizados de `fabio-rovai/insurance-register-ontology`.
- Política verificada por test: **ningún edge canónico sin identificador exacto**; el nombre solo aparece como `diagnostic`.

## 6. Gaps documentados (resumen; detalle en ledger)

| ID | Alcance | Naturaleza |
|---|---|---|
| GAP-B2-DGSFP-LPS-NO-IDENTIFIER | 616/825 L Activa | DGSFP no publica identificador para unir la clave L con la empresa de origen. Únicamente nombre+país → prohibido promocionar. Nota de recuento: 825 = 209 con LEI + 616 sin LEI; el total sin resolución exacta es 617 (616 + L1522, fila siguiente). |
| GAP-B2-L1522-STALE-LEI | 1 | LEI obsoleto en RRPP vs EIOPA; desacuerdo explícito representado. |
| GAP-B1-BDE-PARENT-CODE-COVERAGE | 13/70 | Sin matriz en BdE (10) o matriz no-UE (3). |
| GAP-C-EIOPA-IORP-REGISTER-401 | fondos | Registro IORP de EIOPA devuelve 401 desde este entorno. |
| GAP-D-EIOPA-NO-MEDIATOR-DATASET | PUI | No existe dataset europeo equivalente; join no esperado. |

## 7. Recomendación final

## `BUILD_WITH_BOUNDED_GAPS`

Justificación: el *identity fabric* es sólido — A con cobertura total 100% exacta a tres registros más GLEIF; B1 con cadena exacta al 100% donde la fuente publica la matriz; B2 con puente oficial exacto en todo el subconjunto con LEI y un gap **claramente delimitado, causado por la fuente y representado honestamente** (616 claves L sin identificador + L1522 con LEI sin home = 617 sin resolución exacta). Ningún edge se promocionó por nombre. La infraestructura de acceso está verificada y reproducible (22 tests, hashes, snapshots).

Condiciones para v0.1:
1. Mantener `DOCUMENTED_GAP` como estado de primera clase para las claves L sin identificador.
2. Resolver el desfase de snapshots BdE↔DGSFP con doble ingesta antes de comparar poblaciones.
3. Tratar los LEI de grupo vs entidad operadora (clase PASS_EXACT_NO_ES_OP) como aristas distintas, nunca fusionadas.
4. Decidir en la siguiente fase si se persigue un mecanismo de captura navegador-real del endpoint de búsqueda del RRPP (o negociación formal con DGSFP), dado que la enumeración por clave ya es funcional y reproducible.

## 8. Aceptación formal y cierre (2026-09-13)

Las tres relaciones de consistencia se han reconciliado contra los datos derivados y quedan fijadas como invariantes automatizadas en `tests/test_arithmetic_invariants.py` (fallan si reaparece la discrepancia):

1. **B2**: `825 Activa = 209 con LEI + 616 sin LEI`. Los `617` sin resolución exacta = 616 sin identificador (`GAP-B2-DGSFP-LPS-NO-IDENTIFIER`) + 1 con LEI sin home (`GAP-B2-L1522-STALE-LEI`).
2. **Edges**: `A 44 + B1 48 + B2 12 + C 17 = 121` aristas de gate + 2 mecanismos T4_DONOR = 123 totales; 118 canónicas de gate + 3 DOCUMENTED_GAP (L0419, L1160, L1522) + 2 mecanismos canónicos = 120 canónicas.
3. **Universo L**: `1.580` fichas L capturadas → filtro `situacion='Activa'` → `825` (aplicado en `build_g0b2.py`; las 755 restantes son Inactiva/Cancelada/otro estado no operativo).

```text
VERDICT:              BUILD_WITH_BOUNDED_GAPS
G0-A:                 PASS
G0-B1:                PASS
G0-B2:                PASS_WITH_OFFICIAL_BRIDGE + DOCUMENTED_GAP
G0-C:                 PASS
G0-D:                 PASS
IDENTITY POLICY:      PASS — exact identifiers only for canonical edges
PRODUCT DECISION:     BUILD
```

**Alcance v0.1 (estrecho)**: núcleo read-only de entidades `C/M/P/R/E/L`; modelo identidad/provenance/conflicts; fuentes DGSFP + BdE + EIOPA + GLEIF; consultas por clave/LEI y passporting; snapshots reproducibles; export machine-readable. Excluidos: frontend, agentes/LLM, MCP, mediadores completos, analítica Solvency II.

Los gaps son una característica de primera clase del modelo:

```text
identity_status:    EXACT | CONFLICT | UNRESOLVED | SOURCE_ONLY
resolution_method:  DGSFP_KEY | LEI | BDE_PARENT_CODE | OFFICIAL_BRIDGE | NONE
```

No se fabrica crosswalk para las L sin identificador: la respuesta «identidad europea no resoluble de forma exacta con las fuentes públicas disponibles» es preferible a un 99% por fuzzy matching.

**G0 CONGELADO — autorizado avance a v0.1.**
