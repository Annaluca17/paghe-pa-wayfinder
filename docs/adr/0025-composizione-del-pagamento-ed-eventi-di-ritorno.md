# Composizione del pagamento, eventi di ritorno e fatti sull'ente

La **composizione del pagamento** è una struttura sola, che serve insieme a Ragioneria, ritenute, trattenute a terzi e delega F24EP. Non nasce ridotta per un solo lettore.

**Pagamento e versione di proposta.** Una versione di proposta di liquidazione ha una sola **valuta prevista** e più rapporti; la emette l'Ufficio personale scegliendo valuta e rapporti. Entrano gli importi calcolati e non ancora in un esito pagato. Restano fuori, visibili con il motivo, quelli in attesa d'atto, oltre capienza o senza attestazione. Il **pagamento** è ciò che una versione confermata fa eseguire.

**Righe.** La composizione è un elenco di righe collegate a un importo, mai con un valore riscritto. Ogni riga ha natura, effetto sul netto (più, meno, nessuno), destinatario (beneficiario o terzo) e canale (accredito, F24EP, bonifico). Una **dichiarazione di composizione** datata dell'istituto, nel corpus, dà queste informazioni e dice anche se l'istituto è solo intermedio, come `cpdel_totale`, e quindi non entra. Una dichiarazione assente ferma la proposta, non il calcolo.

**Contributi.** La proposta calcola la denuncia in simulazione, come se il pagamento fosse già avvenuto alla valuta prevista, e porta i contributi per differenza rispetto ai pagamenti già compresi nel mese. Restano congelati nella versione. La denuncia resta il calcolo ufficiale: se a pagamento eseguito non coincide con quanto trattenuto, il modello lo segnala e non corregge.

**Netto.** C'è un **netto** per rapporto, perché ritenuta e classificazione stanno sul rapporto; la somma per persona è una vista. L'IBAN del beneficiario è un fatto datato della persona: se manca è un dato mancante. Un netto negativo ferma quel rapporto e nomina il caso, non gli altri.

**Ultimo pagamento dell'anno.** È un fatto sull'ente, uno per anno d'imposta, con la data prevista. La proposta con valuta prevista uguale o successiva, nello stesso anno d'imposta, porta il conguaglio di ogni persona che contiene. Un pagamento successivo fa il conguaglio per differenza; la persona assente da quel pagamento riceve un avviso. Se il fatto manca e la valuta cade tra dicembre e il 12 gennaio, è un dato mancante: la versione si invia solo con l'avvertenza (ADR 0013).

**Fatti sull'ente.** L'ente è un soggetto dei fatti, con un registro per ente e nessun identificativo da gestire. Ora entrano solo i tipi con un lettore: codice fiscale, denominazione, email, IBAN di tesoreria, sigla provincia, ultimo pagamento dell'anno.

**Evento di pagamento.** Elenca i rapporti pagati e la valuta. L'esito pagato comprende solo quelli, con tutte le righe della loro composizione, anche a carico ente: è la fotografia di ciò che quel pagamento ha generato. I rapporti non pagati ripartono con una nuova versione.

**Valuta effettiva diversa dalla prevista.** L'esito porta la data reale e l'anno d'imposta si congela su quella.
- Stesso mese: nessuna conseguenza.
- Altro mese, stesso anno d'imposta: gli importi entrano nella denuncia del mese reale, e le differenze su ritenute e contributi si regolano sul pagamento successivo, con un avviso.
- Anno d'imposta diverso: gli importi dell'esito restano com'erano e il calcolo fiscale della persona si ferma, nominando il caso.

**Fatto che cambia dopo l'invio.** La versione diventa superata finché non c'è un evento di pagamento, anche se è già confermata. Se l'evento arriva su una versione superata vince il denaro reale: l'esito nasce dalle righe di quella versione e la differenza col dovuto entra nel pagamento successivo. L'eventuale versione più recente si ricalcola sul nuovo esito.

**Ricevute e versamento.** La trasmissione della delega è un esito dichiarato. Ogni **ricevuta** (controlli formali, controllo dei crediti, addebito) è un evento con identificativo stabile, e lo stato della delega è una vista: trasmessa, accettata, sospesa, addebitata, scartata. L'**esito versato** nasce una sola volta per versamento, dall'**evento di versamento eseguito**, con la data reale dell'addebito, e comprende le righe versate ai terzi. La regolarizzazione del provvisorio è un evento contabile successivo; vale come versamento eseguito solo se è l'unica notizia disponibile, con la provenienza che lo dice. Una ricevuta negativa rende la delega scartata e gli importi tornano da versare. Il bonifico a un terzo (pignoramento, cessione) usa lo stesso evento e lo stesso esito: cambia il canale.

**Identificativi.** Stesso identificativo e stesso contenuto: nessun effetto. Stesso identificativo e contenuto diverso: rifiuto con errore. Una valuta si corregge con un evento nuovo, che diventa un nuovo fatto (ADR 0006). Ogni evento conserva l'adattatore che l'ha portato.

**Mappatura esterna.** Struttura unica nel corpus: istituto, sistema (codice tributo, causale, poi SICO, punto CU), codice, date, riferimento. Più istituti possono avere lo stesso codice. I casi doppi diventano istituti distinti (addizionale saldo e acconto, ritenuta ordinaria e separata), senza condizioni nella mappatura finché un caso non le impone. Il codice si sceglie per anno d'imposta quando c'è, altrimenti per data di pagamento. Una mappatura assente ferma l'invio, non il calcolo. Sezione e formato dei riferimenti stanno nel catalogo dei codici del ticket #54.

Scelto da Luca il 07/11/2026 nel grilling del ticket #56, domande 1-16. Precisa l'ADR 0013 (versamento eseguito, regolarizzazione) e l'ADR 0019 (anno d'imposta sulla data reale, ultimo pagamento).

## Considered Options

- **Composizione solo per l'F24EP, con righe per codice tributo:** Ragioneria e trattenute a terzi ne avrebbero bisogno di un'altra, e il legame col pagamento si perderebbe.
- **Valori copiati nella composizione:** due numeri per lo stesso importo, senza derivazione.
- **Natura scritta dal calcolo o dedotta dal nome dell'istituto:** nascosta e senza date.
- **Contributi solo a pagamento avvenuto:** nessun netto prima del mandato.
- **Netto per persona:** ritenuta e classificazione stanno sul rapporto; per la persona basta una vista.
- **Ultimo pagamento dichiarato su ogni proposta, o per persona:** un passaggio manuale già scartato dall'ADR 0019. Fare il conguaglio per «dicembre» ignora la cassa allargata.
- **Identificativo dell'ente in ogni fatto:** multi-tenant è fuori ambito; più enti saranno più registri.
- **Una sola ricevuta:** una delega inviata sembrerebbe pagata anche se scartata o sospesa.
- **Esito versato dalla regolarizzazione:** può arrivare giorni dopo l'addebito, con una data che non è quella del versamento.
- **Esito pagato per tutta la versione:** chi non ha ricevuto nulla risulterebbe pagato e la sua ritenuta finirebbe in delega.
- **Anno d'imposta congelato sulla valuta prevista:** dopo uno slittamento oltre l'anno sarebbe falso.
- **Condizioni nella mappatura:** più flessibili, ma nascondono casi diversi sotto lo stesso istituto.

## Consequences

**Norma certa**

- Fasi dopo l'invio: Allegato 2 alle specifiche F24EP, par. 1 e 3 (ricerca `versamenti-f24ep.md`).
- Sospensione fino a 30 giorni di una delega con compensazioni: art. 5 c. 5-6 D.Lgs. 33/2025, applicabile dal 01/01/2027, e Allegato 2 par. 1 b. La fonte per il 2026 è **da verificare**.

**Scelte di progetto**

- Forma della composizione, dichiarazione dell'istituto, fatto sull'ultimo pagamento, trattamento della valuta diversa e delle versioni superate.

**Conseguenze sul modello**

- L'esito pagato può portare contributi e righe a carico ente: le basi non cambiano, perché la denuncia ignora gli importi derivati.
- La delega legge solo gli esiti pagati: le ritenute di chi non è stato pagato non si versano.
- Il calcolo fiscale conserva `ultimo_dell_anno`, ma nel ciclo lo ricava la proposta dal fatto sull'ente: l'Ufficio personale non lo dichiara a ogni pagamento.

**Fuori dal ticket #56**

- Righe per classificazione e impegno, abbinamento: ticket a parte. Fino ad allora la versione di proposta porta solo la composizione.
- Storno di un accredito dopo l'esito: caso non modellato, ferma il rapporto. Ticket a parte.
- La delega, il serializzatore e le compensazioni: ticket #54.
