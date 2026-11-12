# Somma esente e trattamento integrativo: codici F24EP, restituzione, ripartizione, rate, CU

Ticket: non indicato · Data: 2026-11-09 · Serve a: conguaglio e delega F24EP (ADR 0019, ADR 0023); completa `parametri-fiscali-2026-2027.md` (temi 2 e 3) e `versamenti-f24ep.md` (tema 3)

## Domanda

Come si trattano, dal lato del sostituto d'imposta, due benefici che non fanno reddito: il **trattamento integrativo** (D.L. 3/2020 art. 1) e la **somma esente** (L. 207/2024 art. 1 c. 4)? Cinque punti: (1) codice F24EP con cui si recupera la somma e come si compilano i riferimenti; (2) come si restituisce quanto recuperato e poi risultato non spettante; (3) come si riconoscono mese per mese; (4) recupero a rate, soglia dei 60 euro, cessazione; (5) dove vanno nella CU 2026.

## Legenda e come sono state lette le fonti

- **norma certa**: testo di legge letto su Normattiva, oppure provvedimento dell'AdE per ciò che dice del proprio modello (risoluzione istitutiva di codici, tabella codici).
- **prassi-interpretazione**: circolare o istruzioni AdE, oppure lettura ricavata da più fonti concordi.
- **da verificare**: non confermato su fonte primaria.

Aperti e letti per intero (PDF scaricati ed estratti in testo), il 09/11/2026: risoluzione AdE 9/E del 31/01/2025; risoluzione 35/E del 26/06/2020; risoluzione 51/E del 06/10/2025; circolare 4/E del 16/05/2025; circolare 29/E del 14/12/2020; istruzioni CU 2026; tabella codici F24EP aggiornata al 01/10/2026. Su Normattiva: D.L. 3/2020 art. 1 commi 1-4 e L. 207/2024 art. 1 commi 4-9 (testo consolidato: il c. 6 compare abrogato dal D.Lgs. 117/2026; la pagina è stata letta fino ai primi 100.000 caratteri).

- La **risoluzione AdE del 2025 che istituisce i codici per la somma** è la **9/E del 31/01/2025**: è già citata in `versamenti-f24ep.md`, qui è stata riletta per esteso.
- Le circolari 4/E 2025 e 29/E 2020 sono su carta intestata dell'AdE e valgono come **prassi**: guidano gli uffici e i sostituti, non sono legge.
- Il **vault-pa** non è stato consultato per questo lavoro. Nessuna affermazione si regge sul vault.
- Aliquote, importi e codici: dove la riga dice «due fonti» sono atti distinti e indipendenti. Dove manca la seconda fonte, la riga lo dice.
- Nessun dato reale, nessun nome di ente.

## Sintesi

1. **Codice della somma**: **175E** (F24EP) e **1704** (F24 ordinario), risoluzione 9/E 2025. Sezione Erario (F), riga **a credito compensato**. Riferimento A = mese (`00MM`), riferimento B = anno (`AAAA`). Il **trattamento integrativo** resta **170E** (F24 ordinario 1701), risoluzione 35/E 2020: confermato.
2. **Ulteriore detrazione (c. 6)**: **nessun codice a parte e nessun credito**. È una detrazione dall'imposta lorda: riduce la ritenuta. La legge dà il credito compensabile solo per la somma del c. 4 (c. 8).
3. **Restituzione**: non c'è un codice di versamento dedicato. Si usa **lo stesso codice** (170E o 175E) nella colonna **«importi a debito versati»**. I codici **700E e 701E** servono solo se l'AdE notifica un atto di recupero (ris. 51/E 2025).
4. **Ripartizione mensile della somma**: la percentuale (7,1 / 5,3 / 4,8) si sceglie sul **reddito annuo teorico**, poi si applica al **reddito di lavoro dipendente effettivamente pagato nel mese**. Per il trattamento integrativo: criterio «oggettivo e costante», scelto dal sostituto.
5. **Soglia dei 60 euro**: per la somma e l'ulteriore detrazione si guarda l'importo **«anche complessivamente considerato»** (prassi: si sommano). Dieci rate (somma, ulteriore detrazione), otto (integrativo).
6. **Cessazione**: recupero **in unica soluzione** a prescindere dall'importo. Se la retribuzione non basta, il sostituto lo comunica e il lavoratore versa **entro il 15 gennaio**.
7. **CU 2026**: integrativo ai punti **391-395**; somma ai punti **725-728**; ulteriore detrazione al punto **368**.

## Domanda 1. Codici per recuperare la somma esente e il trattamento integrativo

| Punto | Esito | Marcatura e fonte |
|---|---|---|
| **Somma esente (L. 207/2024 c. 4)**: codice F24EP | **175E**, «Credito maturato dai sostituti d'imposta per l'erogazione ai lavoratori dipendenti della somma di cui all'articolo 1, comma 4, della legge 30 dicembre 2024, n. 207». Sezione **Erario (valore F)**, campo **«importi a credito compensati»**. Modalità di utilizzo **E** (a debito e a credito). In vigore dal 31/01/2025 | **norma certa**: risoluzione AdE 9/E del 31/01/2025. Seconda fonte: tabella codici F24EP al 01/10/2026 (riga 175E) e istruzioni CU 2026 (punti 727-728). Due fonti |
| Stesso beneficio nel modello **F24 ordinario** | **1704**, stessa denominazione. Sezione Erario, colonna «importi a credito compensati»; campi «rateazione/regione/prov./mese rif.» e «anno di riferimento» nei formati `00MM` e `AAAA` | **norma certa**: ris. 9/E 2025. Seconda fonte: istruzioni CU 2026 (punti 727-728) |
| **Riferimento A e B del 175E** | **A** = mese in cui è avvenuta l'erogazione (formato `00MM`, per esempio `0004` o `0012`); **B** = anno (`AAAA`). Codice ed estremi: **non compilare** | **norma certa**: ris. 9/E 2025 e tabella F24EP 01/10/2026 (stessa lettura) |
| **Trattamento integrativo**: codice F24EP | **170E** (F24 ordinario **1701**), sezione Erario (F), colonna a credito compensato; riferimento **A** = mese di erogazione (`00MM`), **B** = anno (`AAAA`). Conferma del codice già presente nel repo | **norma certa**: risoluzione AdE 35/E del 26/06/2020. Seconda fonte: tabella F24EP 01/10/2026 (riga 170E, modalità E) e istruzioni CU 2026 (punti 393-394). Due fonti |
| Quale mese e quale anno si indicano | Il mese e l'anno del **giorno in cui il sostituto paga** il beneficio, di solito il giorno di pagamento delle retribuzioni, **non** il mese di competenza | **prassi-interpretazione**: circ. 29/E 2020 par. 7 (esempio: stipendi di agosto pagati il 10 settembre, riferimento `09/2020`). Scritta per il trattamento integrativo; per la somma la ris. 9/E dice solo «mese e anno in cui è avvenuta l'erogazione»: stessa lettura, **da verificare** che l'AdE non dica altro |
| Conguaglio fatto a gennaio o febbraio (erogazione o recupero riferiti all'anno precedente) | Riferimento **dicembre** e anno **precedente**, sia per il credito sia per il riversamento | **prassi-interpretazione**: circ. 29/E 2020 par. 7 (esempi di febbraio 2021 con `12/2020`), per il trattamento integrativo. Per la somma **da verificare**: né la ris. 9/E né la circ. 4/E danno esempi |
| **Ulteriore detrazione (L. 207/2024 c. 6)**: esiste un codice a parte? | **No.** Non genera un credito: riduce l'imposta lorda, quindi la ritenuta del mese. Il credito compensabile è previsto dal c. 8 **solo** per «la somma di cui al comma 4» | **norma certa**: L. 207/2024 art. 1 c. 8, testo letto su Normattiva. Seconda fonte: ris. 9/E 2025 (titolo e testo parlano solo della somma) e circ. 4/E par. 1.2 («per effetto dell'erogazione … della somma di cui al comma 4 … maturano un credito») |
| Con quali debiti si compensa il credito | Circ. 4/E: il sostituto compensa «qualsiasi importo a debito esposto nel modello F24», anche in sezioni diverse da Erario. Per il 170E la circ. 29/E dice solo «nell'ambito del modello F24» | **prassi-interpretazione**: circ. 4/E 2025 par. 1.2 (per la somma). Chiude, per la somma, il «da verificare» di `versamenti-f24ep.md` sull'uso contro causali di altre sezioni. Per il 170E resta come scritto lì |
| Limite annuo di compensazione | Per il 170E non si applica (art. 34 L. 388/2000) | **prassi-interpretazione**: circ. 29/E 2020 par. 7. Per il 175E né ris. 9/E né circ. 4/E lo dicono: **da verificare** |
| Obbligo di canale | I modelli con compensazione del credito vanno presentati solo con i servizi telematici AdE, pena lo scarto del versamento; l'uso del credito **non** richiede di aver presentato prima la dichiarazione | **norma certa** per il richiamo: ris. 35/E 2020 (art. 37 c. 49-bis D.L. 223/2006). Per il 175E la ris. 9/E non lo ripete |
| Il credito va riportato nel 770 | Sì, per il trattamento integrativo | **prassi-interpretazione**: circ. 29/E 2020 par. 7. I righi del quadro SX restano **da verificare** (vedi `versamenti-f24ep.md`) |

**Differenza di dettaglio tra le due risoluzioni.** La tabella F24EP descrive il riferimento del 175E come «mese di erogazione della somma»; il testo della ris. 9/E dice «mese e anno in cui è avvenuta l'erogazione **ovvero il recupero**» (vedi domanda 2). Per il modello conviene un solo criterio per i due codici, con la nota che la fonte del 175E è meno precisa.

## Domanda 2. Restituire il beneficio recuperato e non spettante

| Punto | Esito | Marcatura e fonte |
|---|---|---|
| Esiste un codice di versamento dedicato al riversamento al conguaglio? | **No.** Si espone lo **stesso codice** del credito (170E o 175E) nella colonna **«importi a debito versati»**. Nello stesso modello possono convivere due righe dello stesso codice: una a credito (benefici erogati) e una a debito (benefici recuperati) | **norma certa** per il 175E: ris. 9/E 2025 («nei casi in cui il sostituto debba procedere al riversamento della somma già erogata e poi recuperata in capo al dipendente, nella colonna importi a debito versati»). **prassi-interpretazione** per il 170E: circ. 29/E 2020 par. 7 (esempi con 1701: 400 a debito e 1000 a credito). Seconda fonte per il 170E: istruzioni CU 2026 (punti 393-394: recuperato e versato «con i seguenti codici 1701 e 170E») |
| Il debito si versa con le ritenute? | Sì: entro i termini ordinari di versamento delle ritenute | **prassi-interpretazione**: circ. 29/E 2020 par. 7 |
| Come si compilano i riferimenti al riversamento | Ris. 9/E: mese e anno «in cui è avvenuta l'erogazione ovvero il recupero». Circ. 29/E (integrativo): per la **prima rata** o il recupero **in conguaglio** si indica il periodo del conguaglio (dicembre e anno del conguaglio; negli esempi di gennaio-febbraio `12/2020`); per le **rate successive** il **mese del recupero** e l'**anno in cui è avvenuta l'erogazione non spettante** | **prassi-interpretazione**. Le due formulazioni non coincidono: per il 175E **da verificare** quale vale; il testo di ris. 9/E è ambiguo sull'anno |
| Si riduce la compensazione dello stesso codice? | Nella pratica **sì**: sono righe separate nello stesso modello e il saldo del modello non può essere negativo (vedi `versamenti-f24ep.md`). Il sostituto non netta da sé: espone il credito e il debito | **prassi-interpretazione**: circ. 29/E 2020 par. 7 (esempi) |
| Si riversa **tutto** il beneficio o solo la parte tolta in busta? | Per l'integrativo, se in busta si trattiene solo la differenza con l'ulteriore detrazione spettante, **si riversa allo Stato l'intero importo** non spettante | **prassi-interpretazione**: circ. 29/E 2020 par. 6 (chiarimento «vale ai fini della busta paga, non del versamento»). Per la **somma**, la circ. 4/E par. 1.2 dice che si recupera «l'importo erogato al netto dell'ulteriore detrazione» e non ripete il chiarimento sul versamento: **da verificare** |
| Codici di versamento a seguito di atto di recupero (controllo sostanziale, art. 38-bis D.P.R. 600/1973) | **F24**: 7909 (credito e interessi) e 7910 (sanzione). **F24EP**: **700E** (credito e interessi) e **701E** (sanzione). Sezione Erario (F), colonna a debito; «codice ufficio» e «codice atto» come da provvedimento; **riferimento B** = anno in cui è stata fatta l'indebita compensazione; **riferimento A** non compilato. Pagamento intero entro il termine del ricorso, senza compensazione | **norma certa**: risoluzione AdE 51/E del 06/10/2025. Seconda fonte: tabella F24EP 01/10/2026 (righe 700E e 701E, modalità D). Due fonti. Riguarda il **solo trattamento integrativo**: per la somma esente **nessun codice analogo letto**, **da verificare** |
| Se il recupero non è possibile in busta (cessazione, incapienza) | Il sostituto comunica l'importo non trattenuto al percipiente, che versa **entro il 15 gennaio** dell'anno dopo; se non è più possibile il conguaglio a debito, il lavoratore restituisce nella dichiarazione dei redditi, anche a rate | **norma certa** per il testo citato: art. 23 c. 3 D.P.R. 600/1973 (già in `parametri-fiscali-2026-2027.md`). **prassi-interpretazione** per l'applicazione ai benefici: circ. 4/E 2025 par. 1.2 e circ. 29/E 2020 par. 6 |

## Domanda 3. Ripartizione in corso d'anno

| Punto | Esito | Marcatura e fonte |
|---|---|---|
| **Trattamento integrativo**: «ripartito fra le retribuzioni» | Il sostituto lo riconosce «in via automatica» e lo ripartisce «fra le retribuzioni erogate». Criterio non fissato dalla legge | **norma certa**: D.L. 3/2020 art. 1 c. 3, testo letto su Normattiva |
| Con quale criterio | «Vari criteri, purché **oggettivi e costanti**», che ripartiscano l'intero importo spettante fra le retribuzioni dell'anno. Esempio: dividere per il numero dei periodi di paga in cui il beneficio è erogato (600 euro in sei mesi: 100 al mese; in cinque mesi: 120) | **prassi-interpretazione**: circ. 29/E 2020 par. 4. Scritta per il 2020; per gli anni successivi nessun testo diverso letto, e la circ. 4/E 2025 rinvia alla 2/E 2024 solo per i requisiti: **da verificare** che il criterio valga ancora. Importo rapportato al periodo di lavoro: D.L. 3/2020 art. 1 c. 2 (**norma certa**) |
| **Somma esente**: base del mese | Il sostituto sceglie la **percentuale** sul **reddito annuo teorico** e la applica «al reddito effettivamente corrisposto mensilmente» | **prassi-interpretazione**: circ. 4/E 2025 par. 1.2 (testo letto). Fondamento di legge: c. 5, il reddito è rapportato all'intero anno «ai soli fini dell'individuazione della percentuale» (**norma certa**) |
| Come si calcola il reddito annuo teorico | Reddito di lavoro dipendente percepito diviso i giorni di lavoro e moltiplicato per **365**. Con più rapporti: giorni sommati, quelli contemporanei **una sola volta** | **prassi-interpretazione**: circ. 4/E 2025 par. 1.2, esempi 1 e 2 (2.000 su 62 giorni → 11.744,19; 3.000 su 92 giorni → 11.902,17). In un anno bisestile il divisore: **da verificare** |
| Base del mese: quali voci | La circolare dice «reddito di lavoro dipendente» di art. 49 TUIR, esclusi i pensionati (e, nella CU, gli assimilati). Non dice se sia il reddito del mese per **competenza o per cassa**, né come trattare arretrati e mensilità aggiuntive | **da verificare**. Il criterio «reddito effettivamente corrisposto mensilmente» fa pensare alla **cassa** (data di pagamento), ma nessun testo letto lo scrive |
| Base per le verifiche di spettanza in corso d'anno | Reddito **previsionale** dell'anno, più i dati comunicati dal lavoratore con la CU di altri rapporti | **prassi-interpretazione**: circ. 4/E 2025 par. 1.2 |
| Quando partire | Dalla prima retribuzione utile, con **recupero delle quote** delle mensilità precedenti; se per motivi tecnici non è possibile, nei mesi dopo o al conguaglio | **prassi-interpretazione**: circ. 4/E 2025 (riferita al 2025, anno di avvio). Per il 2026 vale per analogia: **da verificare** |
| **Somma esente nel calcolo del reddito per le soglie** (20.000 per la somma; 15.000 e 28.000 per l'integrativo; 20.000-40.000 per l'ulteriore detrazione) | La somma è, per legge, una somma che **non concorre alla formazione del reddito**: quindi non entra nel reddito complessivo. La legge e la circolare non lo scrivono per questo caso preciso | **norma certa** per «non concorre» (L. 207/2024 c. 4; D.L. 3/2020 c. 1 per l'integrativo). La conseguenza sulle soglie è una **lettura**: **da verificare** (nessun testo letto lo afferma) |
| Cosa **rientra** invece nel reddito di riferimento | Anche cedolare secca, mance con imposta sostitutiva, quota esente di ricercatori e impatriati (c. 9), e il reddito si assume **al netto dell'abitazione principale** | **norma certa**: L. 207/2024 art. 1 c. 9. **prassi-interpretazione**: circ. 4/E par. 1.2 e istruzioni CU 2026. Alla quota esente degli impatriati si applica la percentuale solo sulla **quota imponibile** (circ. 4/E, esempio 3) |
| Più datori e part-time | Il lavoratore può consegnare la CU del precedente datore; con più part-time contemporanei il beneficio è attribuito da **un solo** sostituto, indicato dal lavoratore | **prassi-interpretazione**: circ. 4/E 2025 par. 1.2 |
| Il lavoratore può chiedere di non riceverlo | **Da verificare: la riga di prima era sbagliata.** Nel testo della circ. 4/E 2025 (PDF riletto per intero il 12/11/2026) non c'è nessuna facoltà di rinuncia per somma e ulteriore detrazione, né l'obbligo di documentarla per iscritto. La L. 207/2024 art. 1 c. 7 dice che i sostituti riconoscono la somma «in via automatica» (anche il D.L. 3/2020 art. 1 c. 3 per l'integrativo). La circolare dice solo che, se il sostituto non ha riconosciuto somma o ulteriore detrazione a conguaglio (per esempio alla cessazione), il lavoratore le fa valere nella dichiarazione dei redditi. La scelta «nel mese / solo a conguaglio / nessuna» è una regola operativa di Paghe PA (ADR 0040) | **da verificare** (nessuna fonte letta); il recupero in dichiarazione: **prassi-interpretazione**, circ. 4/E 2025 |

## Domanda 4. Recupero a rate

| Punto | Esito | Marcatura e fonte |
|---|---|---|
| Quante rate | Trattamento integrativo: **otto**. Somma esente e ulteriore detrazione: **dieci**. Rate di pari ammontare, dalla prima retribuzione che sconta gli effetti del conguaglio | **norma certa**: D.L. 3/2020 art. 1 c. 3 e L. 207/2024 art. 1 c. 7. Seconda fonte per ciascuno: istruzioni CU 2026 e circ. 29/E 2020 (otto), circ. 4/E 2025 (dieci). Due fonti |
| La soglia dei 60 euro: per beneficio o cumulata | Per somma esente e ulteriore detrazione il recupero «anche **complessivamente considerato**» oltre 60 euro va in dieci rate: la soglia si guarda sull'**importo sommato** dei due recuperi | **prassi-interpretazione**: circ. 4/E 2025 par. 1.2 (testo letto: «nel caso in cui il relativo importo, anche complessivamente considerato, sia superiore a 60 euro»). La **legge** non lo dice: il c. 7 parla di «il predetto importo». **Chiude** il «da verificare» di `parametri-fiscali-2026-2027.md` (tema 3) |
| Recupero della somma quando spetta l'ulteriore detrazione (il reddito sale oltre 20.000) | Si recupera **l'importo erogato meno l'ulteriore detrazione spettante**; la soglia di 60 euro si guarda sul **netto**. Nel caso opposto (ulteriore detrazione non più spettante e somma da erogare), si fa la compensazione tra debito e credito, e la soglia si guarda sul netto | **prassi-interpretazione**: circ. 4/E 2025 par. 1.2. Per l'integrativo del 2020: circ. 29/E par. 6, con un caso opposto (nel 2020 senza compensazione) |
| La soglia del trattamento integrativo si somma anche con quella della somma esente? | Il testo della circ. 4/E parla di «tali somme» riferito a somma e ulteriore detrazione di L. 207/2024, non dell'integrativo di D.L. 3/2020. Le due soglie sono in leggi diverse | **da verificare**: nessun testo letto dice se i recuperi di integrativo e somma si cumulano |
| **Cessazione del rapporto** | In sede di conguaglio di fine rapporto il sostituto recupera i benefici non spettanti **in unica soluzione, indipendentemente dall'importo**, perché non ci sono altre retribuzioni su cui dilazionare | **prassi-interpretazione**: circ. 4/E 2025 par. 1.2 e circ. 29/E 2020 par. 6 (testo quasi uguale). Due fonti indipendenti dello stesso ufficio, con cinque anni di distanza |
| Cessazione con **rate già in corso** | Il testo parla del conguaglio di fine rapporto, non del residuo di rate avviate prima. La lettura più vicina: il residuo si recupera **in unica soluzione** nell'ultima retribuzione | **da verificare**: nessun testo letto lo dice |
| Se la retribuzione di fine rapporto non basta | Si applica l'art. 23 c. 3 D.P.R. 600/1973: importo comunicato all'interessato, versamento **entro il 15 gennaio**; in mancanza il lavoratore restituisce nella dichiarazione | **prassi-interpretazione**: circ. 4/E 2025 par. 1.2. Il testo di legge citato nel sostituto: **norma certa** |
| Se il sostituto non ha riconosciuto o recuperato (per esempio a cessazione) | Il lavoratore può far valere i benefici **nella dichiarazione dei redditi** | **prassi-interpretazione**: circ. 4/E 2025 par. 1.2 |
| Dal 2027 | Il c. 7 rinvia alla «detrazione di cui al comma 6», abrogato: per l'art. 376 c. 2 D.Lgs. 117/2026 il rinvio vale per l'art. 13 c. 10 del TU | **norma certa** per la clausola; già in `parametri-fiscali-2026-2027.md` |

## Domanda 5. Punti della CU 2026 (redditi 2025)

| Punto | Che cosa | Marcatura e fonte |
|---|---|---|
| **390** | Codice: 1 = integrativo riconosciuto ed erogato in tutto o in parte; 2 = non riconosciuto, o riconosciuto ma non erogato | **norma certa** (istruzioni CU 2026, provvedimento dell'AdE per il proprio modello) |
| **391** | **Integrativo erogato**, **al netto** di quanto recuperato e da recuperare | idem |
| **392** | Integrativo **riconosciuto ma non erogato** | idem |
| **393** | Integrativo **recuperato entro le operazioni di conguaglio**, versato con **1701 e 170E** | idem |
| **394** | Integrativo **da recuperare dopo il conguaglio** (a rate), versato con 1701 e 170E | idem |
| **395** | Integrativo recuperato **dopo il conguaglio** e riferito agli importi del punto 394 della CU **dell'anno precedente** | idem |
| **397-400, 403** | Dati dei precedenti sostituti; il 400 si riporta anche nel 393 | idem |
| **718** | Codice: se ci sono redditi di lavoro dipendente per cui spettano somma e ulteriore detrazione (compilare anche sopra 40.000 euro) | idem |
| **719-723** | Reddito di lavoro dipendente (art. 49), reddito sportivo dilettante, giorni di lavoro, data di inizio e di fine rapporto | idem |
| **724** | Codice: 1 = somma riconosciuta ed erogata in tutto o in parte; 2 = non riconosciuta o non erogata | idem |
| **725** | **Somma esente erogata**, **al netto** di recuperato e da recuperare | idem |
| **726** | Somma **riconosciuta ma non erogata** | idem |
| **727** | Somma **recuperata entro il conguaglio**, versata con **1704 e 175E** | idem |
| **728** | Somma **da recuperare dopo il conguaglio** (a rate), versata con 1704 e 175E | idem |
| **731-741** | Dati dei precedenti sostituti (il 740 si riporta anche nel 727) | idem |
| **368** | **Ulteriore detrazione** (L. 207/2024 c. 6) | idem |
| **469** | Irpef **non trattenuta al conguaglio** ma da trattenere nei periodi di paga successivi, tra cui quella determinata dal **recupero dell'ulteriore detrazione**, a partire dal mese dopo il conguaglio; sopra 60 euro in dieci rate | idem |
| **Eredi** | Integrativo corrisposto all'erede: punto 391; somma: punto 725 | idem |

**Recuperati e non recuperati.** I «recuperati» hanno punti propri (393-395 e 727-728). Per i **non recuperati** per cessazione o incapienza non c'è un punto dedicato letto: l'importo non trattenuto si comunica al lavoratore (art. 23 c. 3) e il beneficio resta in 391 o 725 al netto solo di quanto si è recuperato (**prassi-interpretazione** sul testo letto, **da verificare**). Per la **somma esente** le istruzioni CU 2026 **non descrivono** un punto analogo al 395 (recupero fatto dopo il conguaglio, riferito alla CU dell'anno prima): **da verificare** nelle specifiche tecniche della CU, non lette.

## Correzioni e aggiunte per gli altri file

- `parametri-fiscali-2026-2027.md`, tema 3: la soglia dei 60 euro per somma e ulteriore detrazione è cumulata («anche complessivamente considerato», circ. 4/E 2025); il recupero a cessazione è in unica soluzione. Restano **da verificare** il cumulo con l'integrativo e le rate già in corso.
- `parametri-fiscali-2026-2027.md`, tema 2: il criterio mensile della somma ha ora la fonte (circ. 4/E 2025: percentuale sul reddito annuo teorico, applicata al reddito pagato nel mese). Resta aperta la definizione di «reddito del mese».
- `versamenti-f24ep.md`, tema 3: per il **175E** c'è una prassi esplicita (circ. 4/E 2025) sulla compensazione contro qualsiasi debito del modello, anche di sezioni diverse da Erario. Per il 170E resta quanto già scritto.
- `versamenti-f24ep.md`: 700E e 701E riguardano solo l'integrativo (ris. 51/E 2025, **norma certa**); per la somma non c'è un codice letto.

## Cosa resta da verificare

- Per il **175E**: riferimento A e B nel riversamento (mese di recupero o di erogazione, anno), conguaglio di gennaio-febbraio, limite annuo di compensazione.
- Se per la somma si riversa **tutto** o solo la quota tolta in busta; codice di versamento per atto di recupero della somma.
- Definizione di «reddito del mese» per la somma (competenza o cassa; arretrati; mensilità aggiuntive); divisore in anno bisestile.
- Se il reddito entra o no nel reddito complessivo per le soglie (lettura da «non concorre»).
- Cumulo della soglia dei 60 euro tra integrativo e somma; rate già in corso alla cessazione.
- Criterio di ripartizione dell'integrativo dopo il 2020 (la fonte è la circ. 29/E 2020).
- Punto CU per i recuperi della somma fatti dopo il conguaglio; trattamento dei non recuperati.
- Legge di bilancio 2027: nessun testo letto che cambi somma, ulteriore detrazione o integrativo.

## Fonti

**Normattiva** (consultate il 09/11/2026; testo del portale, senza link stabile, ADR 0003)

- D.L. 5 febbraio 2020, n. 3, art. 1: `urn:nir:stato:decreto.legge:2020-02-05;3~art1` (commi 1-4).
- L. 30 dicembre 2024, n. 207, art. 1: `urn:nir:stato:legge:2024-12-30;207~art1` (commi 4-9; c. 6 mostrato come abrogato dal D.Lgs. 117/2026).

**Agenzia delle Entrate** (PDF scaricati ed estratti in testo)

- [Risoluzione 9/E del 31/01/2025](https://www.agenziaentrate.gov.it/portale/documents/20143/8410894/RIS_n_9_del_31_01_2025/d093ae0e-6f92-4637-0f29-fc60c0330bf8): codici 1704 e 175E (somma).
- [Risoluzione 35/E del 26/06/2020](https://www.agenziaentrate.gov.it/portale/documents/20143/2522862/risoluzione+credito+bonus+IRPEF+2020.pdf/6a8760cb-8a9e-b719-f701-1982232634e8): codici 1701 e 170E (integrativo).
- [Risoluzione 51/E del 06/10/2025](https://www.agenziaentrate.gov.it/portale/documents/20143/8413112/RIS_n_51_del_06_10_2025/f650d8c8-8208-d4c6-9cf5-4a1825012fda): codici 7909, 7910, 700E, 701E.
- [Circolare 4/E del 16/05/2025](https://www.agenziaentrate.gov.it/portale/documents/20143/8410823/Circolare+lavoro+dipendente+LB2025+DD+IRPEF+n.+4+del+16+maggio+2025.pdf/36979eaa-9fc5-a4ec-a7aa-136497c53f91), par. 1.2.
- [Circolare 29/E del 14/12/2020](https://www.agenziaentrate.gov.it/portale/documents/20143/2957155/Circolare+n.+29+del+14_12_2020.pdf/1620fff6-4786-0268-51d4-ef82ae4abf1d), parr. 4, 6 e 7.
- [Istruzioni CU 2026](https://www.agenziaentrate.gov.it/portale/documents/d/guest/cu_istr_2026_agg-1-): punti 368, 390-403, 469, 718-741.
- [Tabella codici F24EP al 01/10/2026](https://www.agenziaentrate.gov.it/portale/documents/d/guest/tabella-codici-tributo-f24ep-aggiornata-al-1-ottobre-2026): righe 170E, 175E, 700E, 701E.

**Fonti secondarie** (solo per trovare le primarie): risultati di ricerca su ecnews.it, edotto.com, orizzontescuola.it e investireoggi.it sulla circ. 4/E 2025; non usate per fondare alcuna regola.
