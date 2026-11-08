# Righe di proposta: classificazione, disponibilità dell'impegno e abbinamento

La versione di proposta porta, oltre alla composizione, le **righe di proposta**: una per classificazione ufficiale e impegno, con l'elenco degli importi che la sommano.

- **Spesa.** Diventano righe di proposta solo le righe di composizione di spesa del Titolo 1, con natura `retribuzione`, `contributo_ente` o `irap`. Ritenute, addizionali, contributi del lavoratore, 730 e trattenute a terzi restano nella composizione, collegate al lordo come nella struttura `ritenute` dell'OPI. Reversali del Titolo 9 e mandati di versamento del Titolo 7 sono atti della Ragioneria.
- **Classificazione.** Il codice di V livello del piano dei conti è una dichiarazione datata dell'istituto nel corpus, con fonte. Se manca alla valuta prevista, la versione non si emette e l'errore nomina l'istituto: ferma l'invio, non il calcolo, come la composizione e la mappatura (ADR 0025). Missione e programma sono un fatto datato del rapporto, scritto dall'ente: il programma dove la persona lavora. Se manca, è un dato mancante e la versione si invia solo con l'avvertenza.
- **Origine dell'impegno.** L'istituto dichiara nel corpus, con date e fonte, se l'impegno è `automatico` col bilancio oppure nasce da un tipo di atto del registro.
- **Disponibilità.** Il fatto contabile dell'impegno porta numero, esercizio, classificazione, atto presupposto e la disponibilità a una data. Il modello sottrae da quella disponibilità le righe delle proprie versioni inviate o confermate, non respinte né superate, registrate dopo quella data. Una disponibilità nuova è un fatto nuovo e il conto riparte da lì.
- **Abbinamento.** Cerca un impegno con la stessa classificazione e l'atto presupposto richiesto dall'origine. Per un'origine automatica vale solo l'esercizio della valuta prevista. Per un'origine da atto vale l'esercizio della valuta prevista e poi, come residuo, gli esercizi precedenti dal più vecchio. Tra più impegni adatti e capienti sceglie nell'ordine: prima l'esercizio della valuta, poi i residui dal più vecchio, e nello stesso esercizio il numero più basso. La capienza si controlla sulla riga intera, che non si spezza mai su due impegni. Se nessun impegno adatto è noto, l'impegno è un dato mancante. Se ce ne sono ma nessuno è capiente, i rapporti con importi in quella riga restano tra i fermi, con classificazione e importo mancante; gli altri rapporti proseguono.
- **Conferma.** La Ragioneria può indicare per una riga un altro impegno, purché già noto come fatto contabile e con la stessa classificazione; altrimenti la conferma è rifiutata. Un impegno incapiente produce un avviso e non un blocco. La conferma conserva il cambio, con l'impegno proposto e quello scelto, e la disponibilità successiva si conta sull'impegno scelto.
- **Proposte di impegno e di accertamento.** Quando nel registro entra un atto, con importo ed esercizio, di un tipo che l'origine di un istituto dichiara, il modello emette una proposta di impegno immutabile, con classificazione, esercizio, atto e importo. La Ragioneria la conferma o la respinge con motivo. La proposta di accertamento ha la stessa forma, con verso entrata. Gli importi del fondo (ADR 0014) e del riparto della convenzione (ADR 0017) restano nei loro ticket e useranno questo meccanismo.

Scelto da Luca l'08/11/2026 nel grilling del ticket #62, domande 1-8. Precisa gli ADR 0013 e 0014 sulla regola di abbinamento e l'ADR 0025, la cui versione portava solo la composizione.

## Considered Options

- **Classificazione tutta nel corpus:** il programma dipende da dove lavora la persona, quindi cambia da ente a ente e da persona a persona.
- **Fatto sul programma obbligatorio, con fermo:** l'ADR 0013 tratta un dato non noto all'ente come dato mancante.
- **Righe anche per il Titolo 9 e il Titolo 7:** sono partite di giro, senza impegno di spesa del personale. Il modello terrebbe un secondo registro contabile, e i codici sono ancora da verificare.
- **Capienza calcolata dal modello sull'importo dell'impegno:** non vede le liquidazioni degli altri uffici né le variazioni dell'impegno.
- **Nessun controllo di capienza:** sparirebbe il fermo chiesto dall'ADR 0013.
- **Riga spezzata su più impegni:** il modello deciderebbe una destinazione che la Ragioneria non ha dato.
- **Scelta tra più impegni lasciata alla Ragioneria come dato mancante:** ogni versione avrebbe un'avvertenza per un caso normale. Una regola scritta e ripetibile, che si può cambiare in conferma, basta.
- **Solo l'esercizio della valuta, anche per gli atti:** ogni arretrato pagato a residuo andrebbe corretto a mano.
- **Esercizio di competenza dell'importo:** confonde la competenza della paga con l'esercizio contabile.
- **Qualunque impegno accettato in conferma:** con un impegno non noto non si conta più la disponibilità; con una classificazione diversa cambierebbe la riga, non l'abbinamento.
- **Proposte di impegno rinviate a un altro ticket, o fondo minimo nel #62:** nel primo caso l'origine dichiarata non avrebbe un lettore che propone; nel secondo il ticket raddoppierebbe.

## Consequences

**Norma certa** (ricerca `classificazione-spese-personale.md`, testi del D.Lgs. 126/2014 letti su copie istituzionali; versione Arconet vigente da riconfrontare)

- Glossario di missioni e programmi: il programma 01.10 non comprende la spesa di personale imputabile ai singoli programmi.
- Allegato 4/2, punto 5.2: impegno automatico dei trattamenti fissi; arretrati da rinnovo impegnati nell'anno di firma; accessorio sull'esercizio del fondo, con FPV per la parte esigibile dopo.
- Allegato 4/2, punto 7: le ritenute del sostituto d'imposta sono servizi per conto terzi.

**Da verificare**

- I codici di V livello sulla versione Arconet vigente, compresi IRAP `U.1.02.01.01.001` e il codice dell'accessorio del fondo.
- Il decreto del 16/03/2026 che aggiorna gli allegati 4/1, 4/2 e 9.
- Gli altri elementi della transazione elementare: COFOG, codice UE, ricorrente/non ricorrente. Restano fuori dalla riga finché non sono verificati.
- Se oneri riflessi e IRAP sull'accessorio seguano l'imputazione della retribuzione.

**Fuori**

- Lo schema concreto del contratto neutro e la delega F24EP (#54).
