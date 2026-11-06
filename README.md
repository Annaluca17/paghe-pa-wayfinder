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

Registro di fatti, importi con derivazione, esiti e differenze (ADR 0001 e 0002). Il corpus usato finora è **fittizio**: nessun valore è una norma reale. Serve Python 3.12 o successivo; il nucleo non ha dipendenze a runtime.

```bash
python -m paghe
```

```bash
pip install pytest
```

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
