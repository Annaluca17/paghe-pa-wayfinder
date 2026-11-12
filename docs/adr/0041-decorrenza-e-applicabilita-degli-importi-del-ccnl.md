# Decorrenza e applicabilità degli importi del CCNL, arretrati automatici

Il CCNL 28/10/2026 ha incrementi con decorrenza 01/01/2025, 01/01/2026 e 01/01/2027, ma gli effetti partono dal giorno dopo la firma. Il corpus applicava il tabellare 2026 anche a pagamenti fatti prima della firma. Decisioni di Luca del 12/11/2026 (ticket #126) e sua conferma sui tre punti di questo ADR.

## Decisioni

1. **Due date per ogni importo del CCNL** nel corpus: la **decorrenza** (`dal`: da quando spetta) e l'**applicabilità** (`applicabile_dal`: da quando un pagamento lo usa). Applicabilità: **29/10/2026**, giorno dopo la firma del 28/10 (art. 2 c. 2). Un pagamento fino al 28/10 usa il tabellare precedente più la vacanza contrattuale; dal 29/10 il nuovo.
2. **La vigenza si sceglie per data di pagamento**: `calcola(..., pagamento=data)` salta le vigenze non ancora applicabili a quella data e vale la precedente. Senza `pagamento` l'applicabilità non conta (corpus fittizi e confronti per competenza). Senza una vigenza applicabile il calcolo si ferma (`ParametroMancante`).
3. **Arretrati automatici** (`arretrati_ccnl`) nel primo pagamento dopo la firma: per ogni mese di competenza già pagato, dalla prima decorrenza applicabile, dovuto alla data di pagamento meno quanto risulta dagli esiti, per istituto. La **vacanza contrattuale riassorbita** si toglie da sé: il suo importo si azzera alla stessa data e la sua differenza è negativa. Il comparto già pagato oltre la tab. C (quota conglobata nella tab. B) si toglie allo stesso modo, perché la differenza è per istituto. Pagati gli arretrati le differenze sono zero: il secondo pagamento non li ripete. Un mese mai pagato non è un arretrato.
4. **Fisco e contributi**: per competenza (le righe portano il mese originario). Gli anni precedenti a tassazione separata passano dalla causa del pagamento tardivo già esistente (ADR 0018), con causa «contratto collettivo».
5. **Cessati** tra decorrenza e firma: gli arretrati sono un **pagamento a parte** nella prima elaborazione dopo la firma. Il nucleo **segnala** il ricalcolo della base di fine servizio (`ricalcolo_fine_servizio`, con le decorrenze maturate alla cessazione in `scaglionamenti`) e non rifà la liquidazione TFS/TFR.

## Fonti e livello di certezza

Testo firmato del CCNL Funzioni Locali 28/10/2026, letto sul PDF (non solo sul vault, che è «da rivedere»):

- **Norma certa**: art. 2 c. 2 (effetti dal giorno dopo la stipulazione, salvo diversa prescrizione) e c. 3 (istituti automatici applicati entro 30 giorni, cioè entro il 27/11/2026); art. 35 c. 1-2 e tab. A e B (tre scaglioni dal 01/01/2025, 2026, 2027, ognuno assorbe il precedente); art. 35 c. 3 (gli incrementi comprendono l'anticipazione dell'art. 47-bis c. 2 D.Lgs. 165/2001, L. 207/2024 art. 1 c. 128: riassorbimento della vacanza contrattuale); art. 36 c. 2 (per i cessati con diritto a pensione contano tutte le decorrenze ai fini previdenziali; per indennità di fine servizio, preavviso, TFR e art. 2122 c.c. «solo gli scaglionamenti maturati alla data di cessazione»); nota 1 della tab. B (dal 2026 il tabellare comprende la quota di comparto conglobata dall'art. 60 CCNL 23/02/2026).
- **Decisione di Luca**: il diritto agli arretrati anche per i cessati è un dato certo. L'art. 36 dice come contano le decorrenze per i cessati, ma non dice in modo esplicito che gli arretrati vadano pagati ai cessati senza diritto a pensione.
- **Da verificare, da fornire con due fonti indipendenti**: tabellare del CCNL 23/02/2026, importo della vacanza contrattuale 2025 e 2026 (la ricerca `docs/research/voci-fisse-comparto.md` segna il 2026 «da verificare»), valore del comparto pagato prima della firma, tab. B 2025 (primo scaglione). Finché mancano, il corpus reale **non li contiene**: un pagamento reale prima della firma si ferma con `ParametroMancante` invece di usare il tabellare nuovo, e gli arretrati 2025 non sono calcolabili (copertura del corpus dal 01/01/2026). Gli arretrati dopo la firma non hanno bisogno dei valori vecchi: il pagato sta negli esiti.
- **Prassi-interpretazione**: la data 29/10 come «applicabilità» (la norma dice «effetti», il termine di 30 giorni è per l'ente); il netto della vacanza e del comparto ottenuto con le differenze per istituto.

## Considered Options

- **Il corpus fotografa solo il nuovo tabellare e gli arretrati sono un fatto a mano**: lascia pagamenti prima della firma sbagliati in silenzio.
- **Applicabilità come campo della regola invece che del parametro**: il tabellare è una formula stabile; cambia il parametro. Scartato.
- **Arretrati come regola del corpus**: dipendono dal pagato (esiti), non dalla competenza; stanno accanto a `differenze`.

## Consequences

- Nel corpus reale il tabellare 2026 (tab. B) ha `applicabile_dal = 2026-10-29`; quello 2027 no, perché decorre dopo la firma. Una vigenza con applicabilità prima della decorrenza è rifiutata.
- `applicabile_dal` entra nell'impronta del corpus solo se presente.
- Chi calcola un pagamento reale prima della firma deve passare `pagamento` a `calcola`, altrimenti vale la decorrenza. Dopo il 29/10/2026 ogni vigenza è applicabile e non cambia nulla. Un controllo nella proposta, che rifiutasse gli importi calcolati senza `pagamento`, è stato provato e tolto: il mese di prova simula pagamenti del 2026 prima della firma con il corpus reale e perderebbe il tabellare di quei mesi.
- Per un mese già pagato in un anno precedente serve la causa del pagamento tardivo («contratto collettivo») per la tassazione separata: se manca il calcolo fiscale si ferma, come per ogni arretrato.
- Il mese di prova usa un corpus fittizio senza applicabilità: invariato.
