# TFR: contributo sulla base TFS, ulteriori elementi a parte, riduzione del lordo fuori dalle basi

Con il regime di fine servizio 1 il TFR si calcola così:

- **Contributo TFR:** 6,10% dell'80% della base `tfs`, tutto a carico dell'ente (DPCM 20/12/1999 art. 1 c. 7; msg INPS 2440/2019).
- **Ulteriori elementi:** voci utili solo al TFR, in una base propria al 100%, con il 6,91% (msg 2440/2019; DPCM art. 1 c. 6).
- **Retribuzione valutabile TFR:** è una regola di cassa e somma le due basi al 100% (Circ. INPS 185/2021 § 2.2.1).
- **Riduzione del lordo:** pari al 2,50% soppresso, calcolato sull'80% delle voci utili al TFS (DPCM art. 1 c. 2-3). È una regola per competenza sul periodo e non entra in nessuna base.

La grammatica dei riferimenti ammette ora `urn:nir:presidente.consiglio.ministri:decreto:<data>`, senza numero: il DPCM 20/12/1999 non ne ha.

Scelto perché Luca ha chiesto di modellare subito la riduzione (ticket #33, 06/11/2026). Il c. 3 vuole invariate la retribuzione netta e quella utile «ai fini previdenziali e dell'applicazione delle norme sul trattamento di fine rapporto». Lasciare la riduzione fuori dalle basi produce proprio questo incremento figurativo, senza un istituto in più.

## Considered Options

- **Riduzione come istituto della retribuzione, con un concorso «escluso» per ogni base:** stesso risultato, ma un istituto in più e quattro dichiarazioni. Il motore tratta già come derivati, fuori dalle basi, gli importi sul periodo.
- **Riduzione più un istituto positivo di «incremento figurativo» nelle basi:** due importi che si annullano nel netto e in più rendono il calcolo meno leggibile.
- **Riduzione al 2% del lordo, senza passare dall'80%:** stesso valore a meno degli arrotondamenti. Il testo parla del contributo soppresso, che si calcola sull'80%.
- **Una base TFR separata per le voci comuni:** coinciderebbe con la base `tfs` (Circ. 185/2021: imponibile TFR sulle «voci utili anche ai fini TFS»).

## Consequences

- **La formula della riduzione elenca i tabellari.** La grammatica non somma per concorso: un test controlla che legga le stesse voci che concorrono per intero alla base `tfs`. Un istituto nuovo utile al TFS va aggiunto alla formula.
- **Il Fondo Credito resta sul lordo prima della riduzione.** Il DPCM non lo nomina: **prassi-interpretazione** (nota di prassi 5). Il fiscale resta fuori dal modello: il c. 2 esclude effetti sull'imponibile fiscale. *Precisato dall'ADR 0015: la riduzione resta senza effetti fiscali, ma il fiscale entra nel modello con la categoria di reddito.* *Corretto dall'ADR 0037: il c. 2 vuole invariato l'imponibile fiscale, quindi la riduzione lo riduce come faceva il contributo soppresso.*
- **La riduzione si arrotonda come la quota TFS del lavoratore,** prima l'80% e poi il 2,50%. Si calcola per periodo dichiarato sui tabellari del periodo. Un recupero su cessato ricalcola anche la riduzione.
- **Gli ulteriori elementi non hanno ancora una voce.** Né il tabellare né il comparto sono ulteriori elementi; la retribuzione di posizione lo sarà quando entrerà nel corpus. Base e regola sono pronte.
- **`RetribTeoricaTabellareTFR` passa alla parte 3.** Non dipende dai pagamenti: va esposta anche con la valutabile a zero e nel V1 causale 5 (Circ. 185/2021). Il suo contenuto è la domanda 5 del ticket, ancora aperta.
- **La ListaPosPA resta una bozza** finché la parte 3 non espone `GestPrevidenziale`.
