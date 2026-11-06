# TFS: base propria, regole di cassa condizionate dal regime e fermo per valore

Il TFS ex INADEL ha una base propria, `tfs`, al 100% della retribuzione contributiva: ogni istituto dichiara se vi concorre, come per la CPDEL. La regola `imponibile_tfs` ne prende l'80% e lo arrotonda al centesimo. Il contributo è il 6,10% dell'imponibile: 2,50 a carico del lavoratore e 3,60 dell'ente (art. 11 L. 152/1968; msg INPS 2440/2019). Le quote seguono lo schema della CPDEL. Il TFS si calcola solo con il regime di fine servizio 3. Per questo il motore aggiunge due capacità:

- **Regola di cassa condizionata:** `applica_se = "tipo=codice"` vale anche per le regole sul periodo e sul mese. Fuori servizio il codice si legge sull'ultimo giorno di servizio prima del mese.
- **Fermo per valore:** un `[[fermo]]` con `codice` scatta solo se il fatto ha quel valore. Il regime 2, optante, ferma la denuncia.

Scelto perché le decisioni di Luca del 06/11/2026 (ticket #33) chiedono il TFS subito e lasciano fuori gli optanti. Un recupero su cessato deve recuperare anche il TFS, anche se il regime è registrato fino alla cessazione.

## Considered Options

- **Base TFS già all'80%, con un concorso «parziale»:** il concorso parziale ferma il calcolo (ADR 0005). Inoltre la ListaPosPA chiede anche la retribuzione al 100%, la `RetribValutabileTFR` della parte 2.
- **Una regola per ogni regime senza condizione, scelta dalla vista:** la denuncia esporrebbe contributi che non sono dovuti.
- **Condizione letta sul mese del recupero:** con il regime chiuso alla cessazione, il recupero su cessato perderebbe in silenzio la quota TFS.
- **Un fermo per ogni regime non modellato, per presenza:** il regime è obbligatorio per tutti, e il fermo per presenza fermerebbe anche il TFS.

## Consequences

- **Base `tfs`.** Il tabellare concorre per intero, anche la quota di comparto conglobata dal 2026. La quota residua di comparto è dichiarata esclusa (art. 33 c. 3 CCNL 22/01/2004). Un istituto nuovo senza dichiarazione per `tfs` ferma il calcolo.
- **Senza regime 3 la base c'è ma il contributo no.** Vale per il regime 1, TFR, che arriva con la parte 2, e per il regime assente, che la vista chiede (ADR 0008).
- **Imponibile arrotondato prima dell'aliquota:** l'imponibile esposto ha 2 decimali (nota di prassi 4).
- **La ListaPosPA resta una bozza.** Il fermo con ambito `vista` resta finché la parte 3 non espone `GestPrevidenziale`.
- **Fuori dal calcolo:** cambio di regime nell'anno, tredicesima con cambio di regime, riduzioni INADEL con codice motivo 6, eccedenza sul massimale. Il massimale ha già un fermo sulla base CPDEL, che contiene la base TFS.
