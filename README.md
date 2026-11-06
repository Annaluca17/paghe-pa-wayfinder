# paghe-pa-wayfinder

Wayfinding verso la specifica di un modello alternativo di elaborazione paghe per Enti Locali.

- Mappa: issue [#1](https://github.com/Annaluca17/paghe-pa-wayfinder/issues/1) (label `wayfinder:map`); ticket = sub-issue.
- Glossario: `CONTEXT.md`.
- Decisioni architetturali: `docs/adr/`.
- Findings delle ricerche: `docs/research/`.
- Nucleo eseguibile: `paghe/`, test in `tests/`.
- Note di prassi: `docs/prassi/`; senza dati personali.
- Normativa: le regole seguono la norma vigente per il periodo di competenza; consultare `vault-pa` in sola lettura prima di codificarle (ADR 0003).

## Nucleo eseguibile

Registro di fatti, importi con derivazione, esiti e differenze (ADR 0001 e 0002). La denuncia del mese (`calcola_denuncia`) somma nelle basi imponibili gli esiti pagati, con la loro data di pagamento (ADR 0006). La dimostrazione e i test del motore usano corpus **fittizi**. Il primo corpus reale, CPDEL e Fondo Credito del comparto dal 2026, è in `corpus/` (ADR 0007, nota di prassi 3). Serve Python 3.12 o successivo; il nucleo non ha dipendenze a runtime.

```bash
python -m paghe
```

```bash
pip install pytest lxml openpyxl
```

Il fisco del lavoro dipendente (`paghe/fisco.py`, ADR 0015 e 0019): categoria di reddito e anno d'imposta congelati nell'esito (`attribuisci_reddito`), imponibile fiscale per persona e anno, ritenuta del pagamento e conguaglio per persona, con la proiezione come avviso. Le regole fiscali stanno nel corpus (`[[categoria_reddito]]`, `[[reddito]]`, `[[ritenuta]]`, `[[conguaglio]]`) e i test usano parametri `fittizio:`: i valori reali attendono il ticket #47.

La vista ListaPosPA (`lista_pos_pa`) e la sua serializzazione (`paghe.uniemens.in_xml`) sono descritte nell'ADR 0008; un esempio fittizio, trasmissibile e valido sullo schema, è in `docs/esempi/` (ADR 0011). Lo schema XSD UniEmens 4.33.1 e l'Appendice G v15 si scaricano dalla scheda INPS «Trasmissione UniEmens per enti e amministrazioni» e non stanno nel repo: i test che li usano li cercano in `PAGHE_XSD_UNIEMENS` (file `.xsd`) e `PAGHE_APPENDICE_G` (file `.xlsx`), altrimenti vengono saltati.

```bash
python -m pytest
```

## Lavoro in locale

```bash
git clone https://github.com/Annaluca17/paghe-pa-wayfinder.git
cd paghe-pa-wayfinder
git checkout -b <ticket>      # un branch per ticket
# ... modifiche ...
git push -u origin <ticket>   # poi PR su main
```

Prima di lavorare un ticket: assegnarlo a sé su GitHub (claim), per evitare sovrapposizioni con sessioni cloud.
