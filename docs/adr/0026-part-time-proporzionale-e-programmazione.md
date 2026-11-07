# Part-time: trattamento dichiarato dall'istituto, calcolo mensilizzato, programmazione per la denuncia

Il **part-time** è un fatto datato del rapporto, che nasce dall'atto di trasformazione, con due valori distinti: la **percentuale** e il **tipo** (orizzontale, verticale, misto). Un cambio di percentuale o di tipo apre una frazione e un periodo dichiarato, come già prevede l'ADR 0005.

**Calcolo.** Il calcolo è lo stesso per tutti e tre i tipi. Il verticale e il misto si pagano mensilizzati, con la stessa riduzione dell'orizzontale: il tipo non cambia il calcolo, cambia solo ciò che si dichiara. L'importo ridotto è l'importo pieno della frazione per la percentuale, arrotondato come dice la regola dell'istituto. La derivazione conserva l'importo pieno.

**Trattamento nel part-time.** Ogni istituto dichiara nel corpus, con date e riferimento, come si comporta nel part-time:
- **proporzionale:** si riduce alla percentuale (competenze fisse e periodiche);
- **intero:** non si riduce (per esempio le aggiunte di famiglia);
- **da integrativo:** la misura la fissa l'ente con un input da atto, come per gli accessori legati a obiettivi o progetti; senza l'atto il calcolo si ferma.

Un istituto senza dichiarazione ferma il calcolo di un rapporto in part-time e nomina l'istituto.

**Programmazione.** La **programmazione del part-time** è un input da atto del rapporto: il periodo che copre (un mese, un trimestre, un anno) e, per ogni giorno, se è lavorativo e con quante ore. Ciò che si dichiara è la programmazione, non il lavorato: le assenze sono altri fatti. Se per un mese la programmazione manca, è un dato mancante: la ListaPosPA è una bozza non trasmissibile, mentre calcolo e pagamento proseguono.

Scelto da Luca il 07/11/2026 nel grilling del ticket #72, domande 1-9. Sulla domanda 4 Luca ha precisato la prassi degli enti: il verticale si paga sempre mensilizzato con la riduzione, ma si dichiarano i giorni e le ore di lavoro, secondo una programmazione mensile, trimestrale o annuale fissata prima. Il misto è raro ma possibile.

## Considered Options

- **Riduzione decisa dalla regola di ogni istituto:** la stessa scelta si ripeterebbe in ogni formula, senza una dichiarazione da controllare.
- **Tutti gli istituti proporzionali salvo eccezioni:** un accessorio dell'integrativo sarebbe ridotto in silenzio.
- **Verticale pagato solo nei mesi lavorati:** non è la prassi degli enti.
- **Giorni e ore dalle presenze effettive:** il part-time è un'obbligazione dell'atto; le assenze hanno i loro fatti e i loro lettori.
- **Fermo del calcolo senza programmazione:** bloccherebbe il pagamento per un dato che serve solo alla denuncia.

## Consequences

**Norma da rileggere sulla fonte.** CCNL Funzioni Locali 16/11/2022, art. 62, letto solo nel vault (pista):
- c. 10: proporzionali tutte le competenze fisse e periodiche;
- c. 11: accessori legati a obiettivi o progetti secondo l'integrativo, anche non proporzionali;
- c. 12: aggiunte di famiglia per intero.

Il CCNL 2022-2024 lo sostituisce con un articolo di numero **da verificare** sul testo ARAN. Va riletto prima del corpus reale.

**Da verificare.** I campi della ListaPosPA per il part-time, in particolare giorni e ore del verticale e del misto, vanno letti sul documento tecnico INPS prima di esporli.

**Fuori da questa decisione.**
- Lavoro supplementare: serve la retribuzione oraria globale di fatto.
- Tredicesima.
- Assenze riproporzionate.
- Conto Annuale: userà la stessa programmazione.
