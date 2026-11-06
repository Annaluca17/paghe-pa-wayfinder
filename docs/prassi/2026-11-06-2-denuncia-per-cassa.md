# Nota di prassi 2: esposizione nella denuncia per cassa

Riferimento: `prassi:immedia:nota:2026-11-06;2`. Fonte: dichiarazione dell'operatore del 06/11/2026 e scelte di progetto confermate dall'operatore, come indicato in ogni sezione. Nessun flusso reale è conservato nel repo.

## Periodo giuridico

**Dichiarazione dell'operatore.** Assunzione il 24/08, primo pagamento a settembre con i giorni di agosto e settembre. Agosto si espone con V1 causale 5 per l'assunzione, come periodo solo giuridico. Imponibili e contributi di entrambi i mesi stanno nell'E0 di settembre.

**Regola.** Il modello produce sempre il V1 causale 5 nella denuncia del primo pagamento, anche se l'assunzione era già nota all'invio del mese. L'E0 a zero si accetta in lettura ma non si genera. Se un fatto di assenza non retribuita copre il mese, non nasce un periodo giuridico. Se il mese non è ancora pagato resta un avviso.

**Limiti.** La causale 2 non è più utilizzabile da 07/2019 (allegato tecnico UniEmens), ma nessuna fonte ufficiale letta descrive il V1 causale 5 solo giuridico.

## Più periodi nello stesso mese

**Scelta di progetto.** Il fisso resta sul periodo a cui appartengono i giorni. Il resto va nel periodo che contiene la data di pagamento, oppure nell'ultimo del mese se il servizio è già finito. La Circ. INPS 105/2012 parla di compensi liquidati nel periodo, senza regolare questo caso.

## Contributo dell'1%

**Scelta di progetto.** Si calcola sul totale del mese e si espone sull'ultimo periodo. La Circ. INPS 6/2014 § 22.1 fissa la cadenza mensile, salvo conguaglio, ma non dice su quale periodo esporlo.

## Pagamenti entro il 12 gennaio

**Dichiarazione dell'operatore.** Il criterio fiscale è diverso da quello contributivo: nella denuncia queste somme stanno sempre nell'E0 di gennaio. La Circ. INPS 105/2012 § 2.1 richiama la regola del 12 gennaio ma non indica la denuncia.

## Progressioni economiche

**Dichiarazione dell'operatore.** Nei vecchi contratti esiste un elenco di codici qualifica per le progressioni, che quindi aprono un periodo. I differenziali stipendiali attuali non si espongono nella denuncia, perché ci sono i nuovi livelli, e non aprono un periodo. Il file INPS delle correlazioni tra qualifica e contratto non è stato letto.

## Recupero in servizio

**Scelta di progetto confermata dall'operatore.** Si detrae dall'imponibile e dal contributo dell'E0 del mese, anche se riguarda un anno precedente. Il fiscale segue una strada propria. Una fonte interna descrive la detrazione algebrica solo per l'ex INADEL: l'estensione agli altri recuperi è un'interpretazione.

## Quando rivedere

Se un messaggio INPS, il manuale ListaPosPA o un errore del controllo INPS indicano altro, oppure quando il file delle correlazioni viene letto.
