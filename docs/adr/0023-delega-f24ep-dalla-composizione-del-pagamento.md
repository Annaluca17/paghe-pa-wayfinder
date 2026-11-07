# La delega F24EP nasce dalla composizione del pagamento

La **delega F24EP** è una vista delle **liquidazioni verso terzi** (ADR 0013). Le sue righe (sezione, codice tributo o causale, codice, estremi, riferimento A e B, debito, credito) si ricavano dalla **composizione del pagamento** delle proposte confermate e pagate: ritenute, contributi, addizionali, rate 730 e versamenti restano legati al pagamento da cui nascono. Il codice tributo o la causale è una **mappatura datata dell'istituto** (ADR 0022). Un importo pagato senza mappatura ferma l'invio della delega, non il calcolo.

**Compensazioni.** I crediti del sostituto (rimborsi da assistenza fiscale, trattamento integrativo e simili) entrano come righe **a credito** nella delega della stessa scadenza, ricavate da una regola sugli esiti pagati dei rimborsi. Si compensano prima contro le ritenute (100E), poi contro gli altri debiti nell'ordine delle sezioni della delega: è una scelta del modello, scelta da Luca il 07/11/2026, la più vicina alla circolare AdE 29/E del 2020, non un obbligo di legge. Il saldo di ogni modello non può essere negativo. Il credito non assorbito resta visibile e passa alla scadenza successiva come fatto con la sua origine. Se il credito incontra un limite o una regola di compensazione non ancora modellata, la delega si ferma.

**Dati dell'ente.** Codice fiscale, denominazione, email, IBAN del conto di tesoreria e sigla della provincia per la sezione INPDAP sono **fatti sull'ente**, datati, con il lettore F24EP. Se ne manca uno, è un dato mancante e l'invio si ferma.

**Scadenza.** Una regola con fonte ricava la scadenza: il 16 del mese successivo; se cade di sabato o di giorno festivo, anche infrasettimanale, il primo giorno lavorativo dopo. Le scadenze dal 1° al 20 agosto slittano al 20 agosto: per l'F24EP questa proroga vale per prassi, non per testo di legge. La **data di versamento** è un fatto scelto dall'Ufficio personale; se cade dopo la scadenza calcolata, il modello avvisa.

**Esiti.** L'**esito dichiarato** è la delega trasmessa, immutabile. Dopo l'invio ci sono tre ricevute dell'AdE: controlli formali, controllo dei crediti (solo con compensazioni, con possibile sospensione fino a 30 giorni) e addebito. L'**esito versato** nasce dall'evento di versamento eseguito (ADR 0013, 0025). Una correzione è una nuova delega; l'annullamento entro il termine di trasmissione è un fatto a sé.

**File telematico.** Lo scrive un serializzatore del nucleo, in Python, sulla specifica AdE (Allegato 2). F24EP-editor è il controllo: i test replicano i controlli del suo validatore e il confronto con i file AdE già ricostruiti.

**IRAP** è un istituto a carico dell'ente con una base propria e una regola datata: 8,5% sulla base retributiva, acconto mensile, codice 380E. Il **fermo dichiarato** si riduce a due casi, **scadenza** e **riparto per regione**, e blocca l'invio della delega, non il calcolo dei netti.

**Ravvedimento.** Un versamento tardivo (esito versato dopo la scadenza) si segnala e ferma quella delega. Il ravvedimento resta per ora a F24EP-editor; come vista del modello verrà con un ticket successivo.

Scelto da Luca il 06/11/2026 nel grilling del ticket #45, domande 2, 3, 4, 5, 10, 11, 12 e 13. Chiude il punto lasciato dall'ADR 0019: il recupero in F24EP dei rimborsi anticipati.

## Considered Options

- **Delega dal file UniEmens e dalle ritenute** (come fa oggi F24EP-editor): ricostruisce a valle i versamenti e perde il legame con il pagamento da cui nascono.
- **Motore di F24EP-editor come generatore** (ADR 0022): respinto.
- **Delega modificabile dopo l'invio:** un esito che cambia non è un esito.
- **Ravvedimento subito nel modello:** è un'eccezione, non il flusso del mese, e le sue regole (tassi, sanzioni) hanno ancora parti di prassi.
- **Dati dell'ente copiati da un F24EP precedente:** l'IBAN cambia con Re.Tes. e va datato.

## Consequences

- La prima fetta di codice è il ticket #54.
- Il premio INAIL entra nella sezione INAIL della stessa delega senza compensazioni (ADR 0024).
- La lista collaboratori (ADR 0015) versa nella sezione INPS con la causale della gestione separata, da verificare per aliquota.

- Il nuovo codice **179E** (e gemelli) per la sostitutiva sul trattamento accessorio del personale non dirigenziale entra nella mappatura (L. 199/2025, art. 1 c. 237; ris. AdE 4/E del 29/01/2026).
- 700E e 701E servono al recupero di un 170E indebito.
- F24EP-editor spegne di default la proroga di Ferragosto e l'estrattore ignora i festivi infrasettimanali: sono da correggere nei tool, se restano controlli.

**Esito della ricerca #51** (`docs/research/versamenti-f24ep.md`)

- **Norma certa:** scadenza del 16 e slittamento anche per i festivi infrasettimanali, art. 4 c. 2 D.Lgs. 33/2025 dal 01/01/2027; nel 2026 vale la fonte originaria, art. 32-ter DL 185/2008, non letta direttamente. Saldo del modello non negativo (Allegato 2, record V). Tre fasi dopo l'invio (Allegato 2). Codici 384E (saldo), 385E (acconto), 380E, P608, P632.
- **Prassi-interpretazione:** proroga di Ferragosto per l'F24EP, comunicato AdE del 06/08/2008 riferito da Fisco Oggi: l'art. 11 D.Lgs. 33/2025 non richiama l'art. 4. Criterio di cassa dell'IRAP. Scadenza del 16 per l'IRAP.
- **IRAP, aliquota:** 8,5% con due fonti concordi (art. 16 c. 2 D.Lgs. 446/1997 in sintesi, risoluzione DF 1/2021 riportata da fonte secondaria). La base retributiva è letta in sintesi: l'art. 10-bis va riaperto prima di citarlo in una regola.
- **Scelte del modello:** ordine dei crediti e riporto, senza norma che li fissi. Il debito contro cui compensare per primo si decide nel ticket #54.
- **Dal 01/01/2027** cambiano i riferimenti, non il contenuto: D.Lgs. 33/2025 per i versamenti, D.Lgs. 141/2026 per i rimborsi da assistenza fiscale.

**Da verificare**

- Il comunicato AdE del 2008 sulla proroga, sull'originale; lo slittamento se il 20 agosto cade di sabato o domenica.
- Il limite di 2 milioni per il 175E; ordine e riporto sulle istruzioni ufficiali del 770.
- La prassi «trattamento integrativo compensato con la CPDEL»: compatibile con la norma generale, nessuna fonte specifica.
- IRAP: il decreto ministeriale della scadenza (art. 30 c. 5), il riparto per regione, LSU, co.co.co. al netto dei contributi, indennità di fine mandato.
- Causali C10 o CXX sulla circolare INPS 8/2026; l'1% aggiuntivo in P201, senza causale dedicata.
- Se tutti gli enti del target usano l'F24EP: elenco delle tabelle della L. 720/1984 non letto (ADR 0013).
- Se esiste un testo unico che sostituisce il D.Lgs. 446/1997.
