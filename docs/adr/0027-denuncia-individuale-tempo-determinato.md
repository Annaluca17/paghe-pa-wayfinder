# DenunciaIndividuale dei tempi determinati: vista della denuncia, contributo NASpI dell'ente, part-time dalla programmazione

Il **tempo determinato** con pensione in CPDEL, oltre alla ListaPosPA, entra ogni mese in una **DenunciaIndividuale** della gestione privata INPS, sotto la matricola DM dell'ente: è la posizione «solo DS», che porta il contributo NASpI. La DenunciaIndividuale è una **vista** della stessa denuncia del modello da cui nasce la ListaPosPA (ADR 0008), non un secondo calcolo. Produce un **esito dichiarato** e rientra nel **controllo di completezza degli output** (ADR 0015, 0022).

**Perimetro.** Solo i tempi determinati con pensione in CPDEL. CFL, apprendisti, contratti di ricerca e tempi determinati con pensione in FPLD fermano la vista e nominano il caso.

**Contributo.**
- `TipoContribuzione` 71 («solo contributo DS» per le amministrazioni non soggette a CUAF).
- `Imponibile`: la base pensionistica CPDEL del periodo, arrotondata all'euro come vuole il tracciato.
- `Contributo`: 1,61% (1,31% ordinario più 0,30% integrativo), con due decimali, tutto a carico dell'ente. L'aliquota è un parametro datato del corpus con le sue due componenti.
- Il **minimale non si applica**.

**Part-time verticale e misto.**
- Nelle settimane interamente non lavorate `TipoCopertura` D.
- Nei giorni senza prestazione `Lavorato` N.
- Nel mese interamente non lavorato `TipoLavStat` DR00.
- `PercPartTimeMese` = ore programmate del mese su ore lavorabili del tempo pieno nello stesso mese, dalla programmazione del part-time (ADR 0026). Distingue il misto, che a giorni non si distinguerebbe.
- `PercPartTime` è la percentuale del contratto, uguale in tutti i mesi.
- Le percentuali sono in centesimi (100% = 10000), non in millesimi come nella ListaPosPA.
- Senza programmazione per il mese è un dato mancante: la vista è una bozza non trasmissibile, come la ListaPosPA.

**Inquadramento.** `Qualifica1`, `Qualifica3` (A tempo determinato per sostituzione, D gli altri) e `RegimePost95` sono regole del corpus che leggono i fatti del rapporto, con una mappatura esterna datata. `CodiceContratto` è CPUB, con `TipoCodiceContratto` 02.

**Mesi senza imponibile.** Se il rapporto è attivo nel mese, la denuncia si emette anche senza prestazione né imponibile: l'obbligo nasce dal rapporto, non dall'imponibile.

Scelto da Luca il 07/11/2026 nel grilling del ticket #77, sulla ricerca `docs/research/uniemens-privatistico-tempo-determinato.md`. Luca ha confermato `TipoContribuzione` 71 e `CPUB` senza prova con il Software di controllo.

## Considered Options

- **Includere subito CFL, apprendisti e TD in FPLD:** codici propri (ID, IG, IS, AD, CL, 61), in parte in scadenza al 31/12/2026, e nessun caso nell'ente tipo.
- **`TipoContribuzione` 00:** non dice che è dovuto solo il contributo DS.
- **Contributo sull'imponibile a centesimi:** il tool Uniemens-private calcola così, ma il tracciato dichiara l'imponibile all'euro e il contributo deve tornare dall'imponibile dichiarato.
- **Applicare il minimale giornaliero o orario:** nessuna fonte letta lo applica alla base del contributo NASpI di un ente, che per la pensione segue le regole CPDEL.
- **Non dichiarare D, DR00 e Lavorato N nella posizione «solo DS»:** contro l'obbligo di invio «dal rapporto» della circolare 74/2021, § 3.
- **`PercPartTimeMese` a giorni:** coincide con le ore solo con giornate uguali e appiattisce il misto.
- **Omettere la denuncia nei mesi senza imponibile:** il verticale a termine con sospensione estiva è il caso tipico degli enti.

## Consequences

- **Norma certa:**
  - aliquota 1,61% (L. 92/2012 art. 2 c. 25; L. 845/1978 art. 25 c. 4; circolari INPS 140/2012 e 125/2025);
  - codici `TipoContribuzione`, `Qualifica3`, `TipoCopertura`, `TipoLavStat` dall'Allegato tecnico;
  - formati del documento tecnico: importi interi all'euro, contributo con virgola e due decimali, percentuali in centesimi;
  - `CPUB` dal messaggio 1058.
- **Prassi-interpretazione:**
  - il 71 come codice dei tempi determinati dei Comuni con pensione in CPDEL;
  - la formula di `PercPartTimeMese` in ore;
  - la corrispondenza tra `TipoImpiego` della ListaPosPA e le qualifiche della DenunciaIndividuale.
- **Da verificare:**
  - dichiarare D e DR00 nella posizione «solo DS», da chiedere all'INPS;
  - `RetribTeorica`, `TipoRetrMal`, `GestioneTFR` e `RispettoMinimale` per un ente;
  - il file «Codici Contratto» dalla v. 60 (09/2026), che non porta più il macrosettore CNEL;
  - il rinvio del D.Lgs. 314/1997 art. 6 al TUIR dopo il D.Lgs. 117/2026.
- **Tool come controllo (ADR 0022).** Le regole di Uniemens-private confermate dal documento tecnico diventano prove. Prima vanno corretti i tre punti del tool discordanti con l'Allegato: `Qualifica3` D/I, `TipoCessazione` 1B/1C, `NR00`/`NFOR`. I codici di errore del validatore senza fonte INPS (02560E e simili) restano solo nomi di test.
- **DenunciaAziendale.** `NumDenIndiv` e `TotaleADebito` (intero, somma dei contributi) sono la quadratura della vista.
- **Fuori da questa decisione:** versamento del contributo (F24EP o MACS), rettifiche ed eliminazioni (`Elimina="S"`), `InquadramentoLavVariaz`.
