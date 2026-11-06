# La delega F24EP nasce dalla composizione del pagamento

La **delega F24EP** è una vista delle **liquidazioni verso terzi** (ADR 0013). Le sue righe (sezione, codice tributo o causale, codice, estremi, riferimento A e B, debito, credito) si ricavano dalla **composizione del pagamento** delle proposte confermate e pagate: ritenute, contributi, addizionali, rate 730 e versamenti restano legati al pagamento da cui nascono. Il codice tributo o la causale è una **mappatura datata dell'istituto** (ADR 0022). Un importo pagato senza mappatura ferma l'invio della delega, non il calcolo.

**Compensazioni.** I crediti del sostituto (rimborsi da assistenza fiscale, trattamento integrativo e simili) entrano come righe **a credito** nella delega della stessa scadenza, ricavate da una regola sugli esiti pagati dei rimborsi. Il credito non assorbito resta visibile e passa alla scadenza successiva come fatto con la sua origine. Se il credito incontra un limite o una regola di compensazione non ancora modellata, la delega si ferma.

**Dati dell'ente.** Codice fiscale, denominazione, email, IBAN del conto di tesoreria e sigla della provincia per la sezione INPDAP sono **fatti sull'ente**, datati, con il lettore F24EP. Se ne manca uno, è un dato mancante e l'invio si ferma.

**Scadenza.** Una regola con fonte ricava la scadenza. La **data di versamento** è un fatto scelto dall'Ufficio personale; se cade dopo la scadenza calcolata, il modello avvisa.

**Esiti.** L'**esito dichiarato** è la delega trasmessa, immutabile, con la ricevuta dell'AdE. L'**esito versato** nasce dall'evento di versamento eseguito (ADR 0013). Una correzione è una nuova delega; l'annullamento entro il termine di trasmissione è un fatto a sé.

**File telematico.** Lo scrive un serializzatore del nucleo, in Python, sulla specifica AdE (Allegato 2). F24EP-editor è il controllo: i test replicano i controlli del suo validatore e il confronto con i file AdE già ricostruiti.

**IRAP** è un istituto a carico dell'ente con una base propria e una regola datata; finché la regola non ha fonte è un **fermo dichiarato** che blocca l'invio della delega, non il calcolo dei netti.

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

**Da verificare** (ticket di ricerca #51)

- Scadenza del 16 e slittamento; proroga di Ferragosto al 20 agosto per l'F24EP: i due tool si contraddicono e il vault non ne parla.
- Ordine, limiti e riporto delle compensazioni (150E, 153E, 154E, 170E, 175E dalla tabella AdE riportata dal vault). La prassi «trattamento integrativo compensato con la CPDEL» non ha norma a supporto.
- IRAP: aliquota, base, soggetti esclusi.
- Codice dell'addizionale comunale a saldo; causali C10 o CXX; P608, P632 e l'1% aggiuntivo in P201, provvisori in F24EP-editor.
- Se tutti gli enti del target sono in Tesoreria Unica (ADR 0013).
