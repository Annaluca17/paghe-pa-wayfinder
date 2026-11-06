# La causa del pagamento tardivo è un fatto; recupero con riporto, sospensione e indebito distinti

Il regime di tassazione di un importo pagato dopo l'anno di competenza dipende dal perché del ritardo, che i dati di pagamento non dicono. Il modello non lo deduce: lo fa registrare. L'istituto dichiara, con date e riferimento, se il suo pagamento oltre l'anno è un **pagamento fisiologico**. Se non lo è, serve il fatto **causa del pagamento tardivo**, con tipo (legge, contratto collettivo, sentenza, atto sopravvenuto, situazione di fatto), date e riferimento. Se manca, il calcolo fiscale si ferma. Il controllo avviene sulla valuta prevista, prima della proposta, e si ripete al pagamento eseguito. Non riguarda gli importi pagati entro il 12 gennaio per l'anno prima. Una regola datata ricava dal fatto il **regime di tassazione**, che si congela nell'esito pagato.

Per l'errore di calcolo dell'ente nessun testo letto dà la risposta (ricerca `differenze-errore-ente.md`). Il fatto ha tipo `situazione di fatto`, motivo `errore di calcolo`, la scelta dell'ente e la motivazione scritta, e il corpus rinvia alla nota di prassi 8. Il modello mostra un'indicazione e non applica nulla da solo: separata per una competenza di due o più anni prima; nessuna indicazione, solo la segnalazione dell'incertezza, per l'anno prima dopo il 12 gennaio. Senza scelta il calcolo fiscale si ferma. La stessa meccanica vale per ogni situazione di fatto.

Il **recupero** resta il movimento nelle basi, e si fa fino a capienza con riporto ai mesi successivi. Su un sospeso attende il rientro in servizio. Cessazione e sospensione diventano fatti distinti, e la fine del servizio senza uno dei due ferma il calcolo. L'**indebito** è un fatto diverso dal recupero: dichiara la somma pagata senza titolo, la modalità di restituzione e i dati che CU e 770 leggono.

Scelto da Luca il 06/11/2026 nel grilling del ticket #16, domande 1–9.

## Considered Options

- **Competenza in un anno precedente uguale separata:** semplice, ma sbaglia performance e altri ritardi fisiologici, per cui la Ris. 151/E esclude la separata.
- **Causa solo sull'istituto:** lo stesso istituto può tardare per un rinnovo o per un errore.
- **Causa solo come fatto a ogni pagamento:** l'ufficio dovrebbe registrarla ogni anno anche per la performance.
- **Errore sempre in separata:** espone a rilievo se AdE legge il caso come nella Ris. 377/E, con rischio di sanzione sulla ritenuta inferiore.
- **Errore sempre in ordinaria:** il dipendente può pagare di più e dovrebbe chiedere il rimborso; su più anni contraddice la ratio della norma.
- **Soglia in giorni per il ritardo breve:** la Risposta 468/2022 rifiuta i 120 giorni come criterio generale.
- **Fermo sul mese negativo:** blocca un caso ordinario che il Manuale INPS regola.
- **Sospensione letta dal codice di cessazione:** non aggiunge fatti, ma il codice serve alla vista e la data di rientro resta ignota.
- **Indebito subito nel codice:** oggi non avrebbe lettori (ADR 0012).

## Consequences

**Norma certa**

- Art. 17 c. 1 lett. b) TUIR e, dal 01/01/2027, art. 19 c. 1 lett. b) TU D.Lgs. 117/2026, stesso testo salvo i rinvii.
- Art. 51 c. 1 TUIR e, dal 01/01/2027, art. 53 c. 1 TU: somme corrisposte entro il 12 gennaio.
- Art. 10 c. 2-bis TUIR e art. 150 D.L. 34/2020: restituzione al netto e credito del 30% per le somme restituite dal 01/01/2020, salvo i rapporti già definiti al 19/05/2020.
- Istruzione INPS: recupero nell'E0 fino a capienza e mai negativo; sul sospeso al rientro; su cessato V1 causale 7, codice motivo 7 (Manuale ListaPosPA 2017, pp. 20, 33, 41).

**Prassi-interpretazione**

- L'errore puro come situazione di fatto, e le indicazioni mostrate dal modello: inferenza dichiarata nella nota di prassi 8.
- `atto sopravvenuto` vale solo per un atto che attribuisce il diritto dopo il periodo. Chi sceglie quel tipo dichiara che l'atto lo attribuisce, e la spiegazione dell'importo lo riporta. Una determina che paga soltanto l'errore non basta.

**Conseguenze sul modello**

- Una differenza pagata dopo non genera un V1 causale 5: entra per cassa nel mese di pagamento (ADR 0005, 0006). Il V1 causale 5 resta per l'errore nella sola denuncia, ed è l'uscita di `differenze`.
- Una valuta effettiva che supera il 12 gennaio può cambiare anno, testo e regime: è una differenza sull'esito (ADR 0013).
- Sentenze e transazioni: il fatto ora le riconosce. Il fiscale segue la causa. Sui contributi il Manuale prevede V1 causale 7, codici motivo 3 e 4, mentre la Circ. 105/2012 § 2.1 cita la sentenza tra le fonti per cassa: la vista dà un quadro fermo e il calcolo prosegue, finché INPS non chiarisce.
- Un riporto ancora aperto alla cessazione ferma il calcolo e nomina il caso.
- Un piano di rate da atto si aggiunge quando un fatto lo porterà. La Corte cost. 8/2023 lega la rateizzazione alla buona fede.

**Nel codice**

- Riporto del recupero, cessazione e sospensione hanno già un lettore e vanno in un ticket `wayfinder:task` separato.
- Causa del pagamento tardivo, regime di tassazione e indebito sono nella specifica ma entrano nel codice con la prima fetta fiscale (ADR 0012).

**Da verificare**

- Il testo della Circ. 23/E/1997, letta solo tramite citazioni.
- Il periodo del V1 causale 7, codice motivo 7.
- La risposta di INPS su sentenze e transazioni.
- L'interpello: al primo caso reale l'ente può presentarlo prima del pagamento, senza dati nel repo. Il modello non ne dipende, e la risposta aggiorna il corpus.
- Una rilettura della nota di prassi 8 da parte di un consulente fiscale, prima del corpus reale.
