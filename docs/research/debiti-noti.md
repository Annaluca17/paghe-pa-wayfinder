# Debiti noti di #73, #77 e #81: ricerca sulle fonti

Ticket #87. Data della ricerca: 08/11/2026. Solo ricerca: nessun codice e nessun valore del corpus è stato toccato.
Le decisioni stanno alla scheda principale, nel grilling; qui in fondo c'è l'«Esito per il grilling».

## Come leggere questo documento

Ogni tema ha: **stato** (norma certa, prassi, da verificare), **fonti** con data, **cosa si è letto davvero**, **proposta**.
Le fonti sono quelle primarie (testi INPS e Agenzia delle Entrate, Normattiva). Dove un testo non si è potuto leggere lo dico.
Per aliquote e importi serve una seconda fonte indipendente (ADR 0003): dove manca, il tema resta «da verificare».
Il vault-pa è stato aperto solo in lettura e solo come pista: nessuna citazione viene da lì. Dove una pista del vault ha
indirizzato la ricerca lo scrivo, e la fonte primaria da leggere è indicata.

Etichette: **norma certa** = testo di legge o circolare letto; **prassi** = interpretazione di un ente o analogia ragionevole,
senza testo che la dica per questo caso; **da verificare** = non risolto con le fonti lette.

Sigle delle fonti lette in questa ricerca:

- [C8] Circolare INPS n. 8 del 03/02/2026 (Gestione separata, aliquote, massimale, minimale 2026). Letta dal PDF dell'INPS.
- [C122] Circolare INPS n. 122 del 28/07/2017 (DIS-COLL, aliquota aggiuntiva 0,51%). Letta dal PDF dell'INPS.
- [C18] Circolare INPS n. 18 del 31/01/2018 (aliquote 2018). Letta in sintesi dal PDF dell'INPS.
- [C23] Circolare INPS n. 23 del 08/02/2013 (compilazione dei versamenti delle PA). Letta dal PDF dell'INPS.
- [C88] Circolare INPS n. 88 del 31/10/2023, sez. 10.1.1 (lavoro sportivo). Letta tramite una trascrizione di terzi (studiocerbone.com): la causale è un riscontro per analogia, vedi tema 1.
- [TAB] Agenzia delle Entrate, «Tabella codici tributo F24EP», aggiornata al 01/04/2020. Letta dal PDF dell'Agenzia.
- [DT] INPS, Documento tecnico UniEmens individuale, versione 4.33 del 29/09/2026. Letto dal PDF dell'INPS.
- [AT] INPS, Allegato tecnico UniEmens individuale, versione 4.32.2 del 30/06/2026. Letto dal PDF (copia su fiscoetasse.com).
- [LP] INPS, Manuale ListaPosPA v. 1 del 13/02/2018. Letto dal PDF dell'INPS.
- [IRAP26] Agenzia delle Entrate, istruzioni IRAP 2026 (quadro IK per gli enti pubblici). Lette dal PDF dell'Agenzia.
- [R151] Agenzia delle Entrate, risposta a interpello n. 151 del 28/12/2018 (personale in comando). Letta tramite una trascrizione di terzi.
- Normattiva: D.Lgs. 446/1997 (art. 10-bis, art. 30), D.M. 421/1998 (art. 2), L. 335/1995 (art. 2 c. 18 e 26), L. 260/1949,
  L. 54/1977, DPR 792/1985, L. 336/2000, L. 151/2025.
- CCNL comparto Funzioni Locali 2019-2021 (art. 38) e CCNL Area Funzioni Locali 2022-2024 (art. 10): PDF dei testi ARAN.

---

## 1. Causale F24EP della gestione separata (oggi `ZGS1`, fittizia)

**Stato: prassi** per la mappa aliquota-causale. **Norma certa** che le causali siano C10 e CXX.

**Cosa si è letto.**

- [TAB]: le causali **C10** e **CXX** sono entrambe «Gestione Committenti», istituite con la risoluzione AdE 98/E del 07/10/2010
  (decorrenza 02/11/2010). Estremi: codice sede INPS; riferimento A: mese e anno di pagamento del compenso, formato `MM/AAAA`,
  non anteriore a 01/1996; riferimento B: non compilare. `ZGS1` non compare nella tabella: nella sezione INPGI la tabella ha
  causali di altro tipo con un nome simile (`CGS1`, `TGS1`...), che non c'entrano.
- [C23] par. 2.2: per C10 e CXX il periodo di riferimento è il mese del pagamento del compenso; l'esempio di compilazione usa CXX.
  Il testo dice «amministrazione committente, nel caso di collaborazioni» per il codice fiscale del committente.
  Non dice quale delle due causali vada con quale aliquota: rinvia alla Tabella A e all'elenco dell'Agenzia.
- [C8] par. 4.1: il committente versa entro il 16 del mese successivo a quello di effettiva corresponsione, con F24 EP per le
  amministrazioni pubbliche. Non nomina le causali. Rinvia alla circolare 23/2013 e al messaggio 8460/2013 (questo non è stato letto).
- [C88] sez. 10.1.1, sul lavoro sportivo: **CXX** per chi non ha altra copertura e non è pensionato (aliquota complessiva piena),
  **C10** per chi ha altra forma obbligatoria o pensione diretta (24% ai soli fini IVS). È l'unico testo INPS letto che dà la regola,
  ma riguarda i collaboratori sportivi, non quelli delle PA.

**Conclusione.** La regola «C10 = aliquota ridotta del 24% (pensionato o altra cassa); CXX = aliquota piena» è coerente con
tutto ciò che si è letto, ma il testo che la dice parla dei collaboratori sportivi. Per i co.co.co. delle PA nessun testo letto la
ripete. Quindi: **prassi per analogia**, non norma certa.

**Proposta.** Mappa nel corpus: posizione `gestione_separata` → `CXX`; `pensionato` e `altra_cassa` → `C10`; amministratori degli
enti locali, tipo 04 (33,72%, nessuna altra cassa), → `CXX`. Marcare la mappa come prassi, con riferimento a [C88] e [TAB].
Riferimento A = `MM/AAAA` del mese di pagamento del compenso (non il mese di competenza).

**Aperto.** (a) Leggere il messaggio INPS 8460/2013. (b) La tabella [TAB] letta è del 01/04/2020: riprendere l'ultima versione
dell'Agenzia. (c) Una conferma esplicita dell'INPS per i co.co.co. delle PA e per la quota forfettaria degli amministratori
(domanda al servizio di assistenza INPS per le PA).

---

## 2. Codice CCNL per UniEmens e ListaPosPA (oggi `S105`, provvisorio)

**Stato: norma certa** sul fatto che `S105` non è un codice UniEmens; **da verificare** il codice giusto.

**Cosa si è letto.**

- `S105` è il codice **CNEL** del comparto Funzioni Locali. Serve per i riferimenti normativi del corpus (`ccnl:S105:...`),
  non per i flussi. La ricerca precedente (`riferimenti-normativi.md`) riporta dal file ufficiale del CNEL che l'**area dirigenziale**
  delle Funzioni Locali ha invece **`S125`**; una fonte di terzi (ilccnl.it) lo conferma.
- [LP] riga `<Contratto>`: «Per i valori ammessi fare riferimento all'Allegato tecnico-Appendice G». Lo stesso per `<Qualifica>`.
  Quindi nel flusso PosPA il contratto è un codice INPS dell'Appendice G, non un codice CNEL.
- Pista dal vault-pa (non citabile): l'Appendice G (aggiornamento 30/09/2025, versione 15) ha, per gli enti locali, il contratto
  `401` «Regioni ed autonomie locali» (2005-2006) e **`RALN`** «Regioni e Aut. Loc. (CCNL naz.)» dal 2007, con qualifiche come
  dirigente a tempo indeterminato `0D0164`, segretario A/B/C `0D0102`/`0D0103`/`0D0485`, funzionari `0FZCD1`..., istruttori
  `0IR000`. **La fonte primaria da leggere è l'Appendice G dell'INPS** (non ho potuto scaricarla in questa ricerca).

**Un'incongruenza trovata nel corpus.** `corpus/funzioni-locali-cpdel.toml` cita contratti dell'**Area** (dirigenti e segretari:
CCNL 16/07/2024 art. 64; CCNL 23/02/2026 art. 24, 35, 63) con `ccnl:S105:...`. Se `S105` è il comparto e `S125` l'area
dirigenziale, quei riferimenti usano il codice CNEL sbagliato. Va verificato sul file CNEL, perché la ricerca sul sito del CNEL non ha
dato altro che la conferma di una fonte di terzi.

**Proposta.** Separare le due cose nel corpus: (1) codice CNEL nei riferimenti (`S105` per il comparto, `S125` per l'Area, dopo verifica
sul file CNEL); (2) codice `Contratto`/`Qualifica` dei flussi come **fatto del rapporto** con mappatura datata, letto dall'Appendice G.
Per ora nessun valore reale nel corpus finché l'Appendice G non è letta.

**Aperto.** Leggere l'Appendice G ufficiale; dire se la dirigenza dell'Area usa `RALN` o un codice proprio dopo il 2023.

---

## 3. DIS-COLL e aliquota per i collaboratori pensionati

**Stato: norma certa** sulla DIS-COLL (non dovuta ai pensionati). **Da verificare** se il totale per i pensionati sia 24,00% o 24,72%.

**Cosa si è letto.**

- [C122]: «iscritti in via esclusiva alla Gestione Separata, non pensionati e privi di partita IVA» è dovuta l'aliquota aggiuntiva
  DIS-COLL (allora 0,51%); «sono interessati dalla modifica... i soggetti privi di altra copertura previdenziale obbligatoria,
  non pensionati e non titolari di partita IVA»; «restano esclusi» tra gli altri gli amministratori di enti locali (D.M. 25/05/2001).
- [C8] tabella dei committenti: la colonna DIS-COLL 1,31% vale per i «soggetti senza altra copertura previdenziale obbligatoria,
  non titolari di pensione e di P.IVA»: codice 11, co.co.co. presso PP.AA., 33,00 + 0,50 + 0,22 + 1,31 = **35,03%**. Gli amministratori
  di enti locali (tipo 04) sono **33,72%**, senza DIS-COLL. Il par. 1.1 dice, per chi è già pensionato o assicurato altrove:
  «l'aliquota è confermata al 24%» (art. 1 c. 79 L. 247/2007). Non stampa un totale con le aliquote aggiuntive né la DIS-COLL per
  quella categoria. L'unico caso in cui la circolare somma 24,00 + 0,50 + 0,22 + 1,31 = 26,03% è quello dei **magistrati onorari**
  con altra previdenza (art. 15-bis D.L. 75/2023), con regola propria.
- [C18] sez. 1.3 e 1.4 (2018): per pensionati e altra tutela solo «24%», senza DIS-COLL. Stessa formula del 2026.

**Cosa cambia rispetto al corpus.** La nota di prassi 10 e `regimi-titolo-cifre-2026.md` danno 24,72% (24 + 0,72) per pensionati e altra cassa.
Questo 0,72 non è stampato nei testi letti per quella categoria: viene dall'analogia con i magistrati. La lettura letterale delle
circolari 2018 e 2026 è **24%** totale. Le due letture divergono di 0,72 punti. DIS-COLL: la ricerca precedente lasciava aperto
26,03%; questa lettura lo esclude per i pensionati (norma e [C122]). Per chi ha **altra cassa ma non è pensionato** [C122] non dice
nulla di esplicito sulla DIS-COLL: il testo letto esclude chi ha altra copertura obbligatoria, quindi vale lo stesso trattamento.

**Proposta.** DIS-COLL: **non dovuta** per `pensionato` e `altra_cassa` (norma certa). Totale: **24,00%** secondo il testo
letterale, da riconfermare con una seconda fonte prima di cambiare il corpus (oggi 24,72%). Se si preferisce il 24,72, va dichiarato
come prassi con il motivo.

**Aperto.** Seconda fonte indipendente sul totale dei pensionati (la pagina INPS «Gestione separata: le aliquote contributive per il
2026» non si è potuta leggere per intero; una sintesi di terzi riporta anch'essa «24%»). Verificare la definizione di «altra cassa»
per i dipendenti pubblici con co.co.co. in un altro ente.

---

## 4. Massimale della gestione separata 2027

**Stato: da verificare** (non pubblicato).

**Cosa si è letto.**

- L. 335/1995 art. 2 c. 18 (Normattiva): massimale annuo della base contributiva, fissato in lire e **rivalutato** sulla base
  dell'indice dei prezzi al consumo per le famiglie di operai e impiegati.
- [C8] par. 6.1: **122.295,00 euro** per il 2026; par. 6.2: minimale 18.808,00 euro. Seconda fonte per il 2026: Circ. INPS 14/2026
  (presa dalla ricerca `regimi-titolo-cifre-2026.md`, non riletta qui).
- Per il 2027 non c'è circolare. Le circolari annuali sono uscite il 30/01/2025 (n. 27) e il 03/02/2026 (n. 8): la prossima è attesa
  tra fine gennaio e inizio febbraio 2027.
- Un calcolatore di terzi dà 119.650 euro per il 2027: **non usare**. Sarebbe un massimale più basso di quello 2026, e la legge lo
  rivaluta con un indice; non è una fonte.

**Proposta.** Non inserire nessun valore 2027. Il motore si ferma già oggi quando la vigenza manca (comportamento da conservare, con il
messaggio che nomina la circolare attesa). Quando esce la circolare 2027: aggiornare massimale, minimale, aliquote e DIS-COLL insieme,
con seconda fonte (la circolare per artigiani e commercianti dello stesso anno riporta il massimale).

**Aperto.** Il valore del 2027 e la data di uscita. Le aliquote IVS (33% e 24%) sono fissate dalla L. 247/2007 art. 1 c. 79, quindi
non cambiano senza nuova legge: restano comunque da riconfermare sulla circolare.

---

## 5. Calendario dei festivi nazionali e patrono, come dato del corpus

**Stato: norma certa** per le feste nazionali; **norma certa (CCNL)** per il patrono; **da verificare** il 4 ottobre.

**Cosa si è letto.**

- L. 260/1949 art. 2 (Normattiva, testo vigente): festivi oltre le domeniche: 1 gennaio; 6 gennaio; lunedì dell'Angelo; 25 aprile;
  1 maggio; 15 agosto; 1 novembre; 8 dicembre; 25 dicembre; 26 dicembre; (il testo elenca ancora, come storico, S. Giuseppe,
  Ascensione, Corpus Domini, SS. Pietro e Paolo e il 4 novembre, che le leggi seguenti hanno tolto). Pasqua cade sempre di domenica.
- L. 54/1977 art. 1: soppresse come festivi civili S. Giuseppe (19/03), Ascensione, Corpus Domini, SS. Pietro e Paolo (29/06);
  la festa del 2 giugno e quella del 4 novembre spostate alla prima domenica del mese.
- DPR 792/1985 (intesa con la Santa Sede): ripristina l'Epifania (6/01); elenco delle festività religiose riconosciute; il 29 giugno
  vale solo per Roma.
- L. 336/2000 art. 1: dal 2001 il **2 giugno** torna giorno festivo. Il 4 novembre non è festivo.
- **L. 151/2025** (in vigore dal 01/01/2026): inserisce nell'art. 2 L. 260/1949 «il 4 ottobre: festa nazionale di San Francesco
  d'Assisi, patrono d'Italia», «agli effetti della osservanza del completo orario festivo e del divieto di compiere determinati atti
  giuridici». Gli effetti sul rapporto di lavoro e sulla retribuzione non sono scritti nella legge; sulla stampa si dice che il 4 ottobre
  torna festivo dal 2026, ma non l'ho trovato in un testo ARAN o INPS.
- **Patrono**: CCNL comparto Funzioni Locali 2019-2021, art. 38 c. 6: «è altresì considerato giorno festivo la ricorrenza del Santo patrono
  della località in cui il dipendente presta servizio, purché ricadente in un giorno lavorativo». CCNL Area Funzioni Locali 2022-2024,
  art. 10 c. 10: le festività nazionali e il Santo Patrono della località in cui il personale presta servizio sono giorni festivi;
  per il segretario titolare di segreterie convenzionate vale il **Santo Patrono del comune capofila**. Il CCNL comparto 2022-2024
  ha la stessa materia all'art. 28 (da indice; testo non letto).

**Calendario 2027 che ne risulta** (giorni infrasettimanali o di sabato; le domeniche non servono): 01/01 (ven), 06/01 (mer),
29/03 lunedì dell'Angelo (Pasqua 28/03), 01/05 (sab), 02/06 (mer), 04/10 (lun), 01/11 (lun), 08/12 (mer), 25/12 (sab). Il 25/04, il
15/08 e il 26/12 cadono di domenica. Il 2026: Pasqua 05/04, lunedì dell'Angelo 06/04; il 4 ottobre 2026 era di domenica.

**Proposta.**

- Calendario nazionale come **dato del corpus per anno**, con riferimento alla legge: elenco fisso (01/01, 06/01, lunedì dell'Angelo,
  25/04, 01/05, 02/06, 15/08, 01/11, 08/12, 25/12, 26/12) più il **4 ottobre dal 2026**; Pasqua calcolata dalla regola ecclesiastica,
  non scritta a mano.
- **Patrono come fatto della sede di lavoro** (comune, giorno e mese), datato, con riferimento al CCNL; per il segretario in
  convenzione, quello del comune capofila. Se il patrono cade di sabato o domenica, non vale come festivo infrasettimanale.
- Un anno senza calendario resta «non dichiarato» e il calcolo si ferma, come oggi (`paghe/corpus.py`, `calendario_festivi`).

**Aperto.** (a) Il 4 ottobre ai fini del CCNL e del part-time verticale: chiedere all'ARAN o leggere una circolare INPS/ARAN.
(b) Come si tratta un patrono che coincide con una festa nazionale (l'art. 10 c. 10 dell'Area dice che non dà diritto a un giorno in
più).

---

## 6. `Qualifica1` e `RegimePost95` della DenunciaIndividuale dei TD

**Stato: norma certa** sulla forma dei campi; **da verificare** i valori per il comparto Funzioni Locali.

**Cosa si è letto.**

- [AT] Elemento `Qualifica1` (p. 108): `1` operaio, `2` impiegato, `3` dirigente, e altri codici per apprendisti, quadri e categorie
  particolari. Il testo non dice come corrispondono le categorie del CCNL Funzioni Locali (operatore, operatore esperto, istruttore,
  funzionario ed elevata qualificazione).
- [DT] p. 41: `RegimePost95` è «obbligatorio a decorrere dalle denunce di competenza gennaio 2015»; ammette «S» se il lavoratore è
  «soggetto a regime contributivo», altrimenti «N». Il testo non spiega che cosa significhi «soggetto a regime contributivo».
- [DT]: i criteri di univocità della denuncia sono `CFLavoratore`, `Qualifica1`, `Qualifica2`, `Qualifica3`, `TipoContribuzione`
  (da ricerca precedente; confermato dal Documento tecnico).

**Ragionamento.** Il nome dell'elemento («Post95») e la legge fanno pensare a chi è stato iscritto per la prima volta ad una forma
obbligatoria dal 01/01/1996 (sistema contributivo puro: L. 335/1995 art. 1, richiamato, non riletto in questa ricerca). Resta un
dubbio: dal 2012 tutti i lavoratori hanno il calcolo contributivo per le quote maturate dal 2012 (L. 214/2011, richiamata, non
riletta), quindi «soggetto a regime contributivo» potrebbe voler dire anche questo. Il Documento tecnico non lo dice.

**Proposta.**

- `RegimePost95`: `S` se la prima iscrizione a una forma pensionistica obbligatoria è dal 01/01/1996 (fatto del rapporto,
  `FATTO_PRIMA_ISCRIZIONE_DAL_1996` che il codice già usa), altrimenti `N`. Marcarlo **prassi-interpretazione** e dichiarare nel
  corpus il motivo della scelta.
- `Qualifica1`: `2` (impiegato) come valore di default per le categorie del comparto, con mappatura datata e, se Luca vuole
  distinguere gli operatori, `1` solo per quella categoria. Marcarlo **da verificare**. Non c'è alcun testo letto che dica
  «operatore = operaio».

**Aperto.** Domanda al servizio di assistenza INPS (tempi determinati privatistici delle PA): valore di `Qualifica1` per le categorie del
comparto e significato esatto di `RegimePost95`. Verifica con il Software di controllo UniEmens.

---

## 7. Scadenza dell'acconto IRAP degli enti: 15 o 16

**Stato: da verificare.** Nessun testo letto riconcilia le due date.

**Cosa si è letto.**

- D.Lgs. 446/1997 art. 30 c. 5 (Normattiva): l'acconto mensile si versa «con le modalità e nei termini stabiliti con decreto» del
  Ministro delle finanze, in un importo pari all'aliquota dell'art. 16 c. 2 applicata agli emolumenti «corrisposti nel mese
  precedente». La legge non dice il giorno.
- D.M. 421/1998 art. 2 c. 1 (Normattiva, ultimo aggiornamento 29/06/2019, in vigore dal 22/12/1998): l'acconto si versa «entro il giorno
  15 del mese successivo» a quello di erogazione delle retribuzioni e dei compensi. Il testo vigente dopo la modifica del 2019
  (art. 4-quater c. 3 D.L. 34/2019) ha ancora il **15**: la modifica ha toccato l'art. 1 (modalità), non l'art. 2.
- Risoluzione AdE 75/E del 09/08/2019: istituisce l'uso del codice 3858 per gli enti che non possono usare l'F24 Enti pubblici e
  rinvia all'art. 30 c. 5; **non indica nessun giorno**.
- [C8] par. 4.1: per i **contributi** della gestione separata il termine è il 16 del mese successivo (F24 EP). Riguarda i contributi,
  non l'IRAP.
- Fonti di terzi (Il Sole 24 Ore, una Regione): «16 del mese» per il 380E. Sono fonti secondarie.
- L'art. 32-ter D.L. 185/2008, citato nell'ADR 0028 per lo slittamento, risulta **abrogato dal D.Lgs. 33/2025 con effetto dal
  01/01/2027** (Normattiva): non ne ho potuto leggere il testo in questa ricerca. Lo stesso vale per l'art. 18 D.Lgs. 241/1997.
  La nuova norma (art. 4 del testo unico del D.Lgs. 33/2025) non l'ho letta: la pagina di Normattiva mostra solo l'indice.

**Che cosa significa.** Il «16» è la scadenza del versamento unitario con F24 (art. 18 D.Lgs. 241/1997, che il D.M. richiama per
gli enti che usano il versamento unitario: art. 1 c. 6). Il «15» è il termine scritto dal regolamento dell'IRAP degli enti pubblici.
Il regolamento non è stato adeguato. Non c'è un testo che dica quale vince.

**Rischio asimmetrico.** Pagare entro il 15 è regolare in entrambe le letture. Pagare il 16, se vale il 15, è un ritardo di un giorno
(ravvedimento). Il contrario non costa nulla.

**Proposta.** Mostrare nella delega la scadenza **16** come termine di prassi (come fa il resto della delega) con un **avviso**
che il D.M. 421/1998 art. 2 dice 15, oppure adottare il 15 come termine prudenziale. Decisione di Luca, perché cambia l'ADR 0028.
Non è una questione da risolvere con altri testi: serve un chiarimento dell'Agenzia delle Entrate (interpello o assistenza ai
tesorieri).

**Aperto.** Un testo dell'Agenzia delle Entrate o del MEF che dica quale termine vale per il 380E; la lettura dell'art. 4 del testo unico
del D.Lgs. 33/2025 per il 2027.

---

## 8. IRAP del personale in comando e in convenzione

**Stato: prassi** per il comando (risposta a interpello, istruzioni). **Da verificare** per la convenzione di segreteria.

**Cosa si è letto.**

- [IRAP26] quadro IK, rigo IK1: la base è l'ammontare delle retribuzioni **erogate (principio di cassa)** al personale dipendente,
  pari all'imponibile previdenziale (art. 12 L. 153/1969); somme non soggette a contribuzione, come il TFR, non entrano. Poi:
  «In caso di distacco di personale, i relativi oneri concorrono a formare la base imponibile dell'IRAP del **soggetto che impiega il
  personale distaccato** e assume rilievo il momento in cui tale soggetto **eroga il rimborso** degli oneri al soggetto distaccante.»
  Per i soggetti con metodo retributivo, [IRAP26] nel passo sulle retribuzioni (rigo IK1 e IK2, art. 10-bis) non dice altro sul distacco.
- [R151]: la posizione di comando è «assimilabile» a quella del distacco; l'IRAP sulle retribuzioni del personale comandato grava
  sull'**ente utilizzatore**, che è tenuto al versamento. Il parere richiama le istruzioni del quadro IK sul momento del rimborso.
  Non dice che cosa faccia l'ente di appartenenza.
- D.Lgs. 446/1997 art. 10-bis c. 1 (Normattiva): base = retribuzioni erogate al personale dipendente, redditi assimilati (art. 47
  TUIR, ora art. 50), compensi per co.co.co. e lavoro autonomo occasionale; esclusi le somme esenti da IRPEF e le borse di studio.
- Per la **convenzione di segreteria** non ho trovato un testo dell'Agenzia delle Entrate. Il CCNL Area FL 2022-2024 art. 10 c. 10
  parla del patrono del comune capofila: indica che il capofila è l'ente di riferimento, ma non dice nulla di IRAP.

**Confronto con l'ADR 0028.** L'ADR dice «paga chi eroga, e chi rimborsa sulla quota rimborsata». Le istruzioni dicono invece:
l'IRAP segue l'**utilizzatore**, nel momento in cui questo **eroga il rimborso**. Le due formulazioni coincidono quando c'è un rimborso
(l'ente che eroga lo stipendio e riceve il rimborso non lo mette in base: l'utilizzatore sì, quando paga). Divergono se l'ente di
appartenenza eroga lo stipendio e **nessun rimborso** viene pagato: le fonti lette non dicono chi paga l'IRAP in quel caso.

**Proposta.** Tenere i fermi del comando e della convenzione (come l'ADR 0028), ma riscrivere il motivo del fermo con la regola vera:
«l'IRAP segue l'ente che impiega il personale, sul rimborso che eroga; i rimborsi tra enti non sono modellati». Quando si
modelleranno i rimborsi tra enti: base dell'utilizzatore = rimborso pagato nel mese; base dell'ente che eroga lo stipendio e
riceve il rimborso = retribuzioni al netto di quanto recuperato [da riscontrare, vedi sotto].

**Co.co.co. al netto.** Un dato in più, che riguarda l'ADR 0028 (co.co.co. al netto della quota del collaboratore): nel quadro IK
i compensi dei co.co.co. sono redditi assimilati (IK2) e entrano «per l'importo contrattualmente spettante». Nessun testo letto
deduce la quota del collaboratore dalla base IRAP (nemmeno per i dipendenti: la base è l'imponibile previdenziale, che include la
quota del lavoratore). La scelta del netto è quindi **senza fonte**; la lettura dei testi porta al compenso **al lordo**. Vale come
suggerimento già dato dalla ricerca `irap-scadenza-riparto.md`.

**Aperto.** Chi versa l'IRAP quando il comando è senza rimborso; il trattamento dell'ente che eroga e recupera; il testo che vale per
la segreteria in convenzione; il testo integrale dell'art. 11 c. 1 lett. a n. 5 e delle risoluzioni citate dalle istruzioni (non lette).

---

## Esito per il grilling

| # | Tema | Stato | Proposta di valore | Cosa resta aperto |
|---|------|-------|--------------------|-------------------|
| 1 | Causale F24EP gestione separata | prassi (per analogia) | `CXX` per `gestione_separata` e amministratori tipo 04; `C10` per `pensionato` e `altra_cassa`; riferimento A = mese di pagamento `MM/AAAA`; `ZGS1` va tolto | msg INPS 8460/2013; tabella AdE aggiornata; conferma INPS per i co.co.co. delle PA |
| 2 | Codice CCNL | norma certa che `S105` non è codice flusso; codice giusto da verificare | Separare il codice CNEL dei riferimenti dal `Contratto` del flusso, che viene dall'Appendice G (pista: `RALN`). Verificare `S105` contro `S125` per l'Area | Leggere l'Appendice G INPS; controllare i riferimenti `ccnl:S105` dell'Area nel corpus |
| 3 | DIS-COLL e pensionati | DIS-COLL: norma certa; totale: da verificare | DIS-COLL non dovuta a `pensionato` e `altra_cassa`; totale 24,00% (testo letterale) invece di 24,72% | Seconda fonte sul totale dei pensionati |
| 4 | Massimale 2027 | da verificare (non pubblicato) | Nessun valore; il motore si ferma finché non esce la circolare 2027 | Valore e data della circolare (attesa fine gen.-inizio feb. 2027) |
| 5 | Festivi e patrono | norma certa (nazionali, patrono nel CCNL); 4 ottobre da verificare | Calendario nazionale per anno con riferimento alla legge, Pasqua calcolata, 4 ottobre dal 2026; patrono come fatto della sede di lavoro (capofila per il segretario in convenzione) | Effetti del 4 ottobre nel CCNL; patrono che coincide con una festa |
| 6 | `Qualifica1` e `RegimePost95` | forma: norma certa; valori: da verificare | `RegimePost95` = `S` se prima iscrizione dal 1996, altrimenti `N`; `Qualifica1` = `2` come default del comparto | Risposta INPS su `Qualifica1` per le categorie FL e su `RegimePost95` |
| 7 | Acconto IRAP 15 o 16 | da verificare | Mostrare il 16 con avviso del 15 del D.M. 421/1998, oppure adottare il 15 prudenziale (decide Luca) | Testo AdE/MEF che dica quale vale; art. 4 testo unico D.Lgs. 33/2025 |
| 8 | IRAP comando e convenzione | prassi (comando); da verificare (convenzione) | Tenere i fermi, riscrivere il motivo: l'IRAP segue l'ente che impiega, sul rimborso. Co.co.co.: tornare al lordo (nessuna fonte per il netto) | Comando senza rimborso; ente che eroga e recupera; testo per la convenzione |

**Cose che questa ricerca ha cambiato rispetto a quanto il corpus e gli ADR dicono oggi.**

1. Il totale per i pensionati: la lettura letterale è 24%, non 24,72% (tema 3).
2. I riferimenti CNEL dell'Area: probabilmente `S125`, non `S105` (tema 2).
3. I co.co.co. al netto nell'IRAP non hanno fonte (tema 8).
4. L'acconto IRAP: il testo vigente del D.M. dice 15; il 16 è prassi (tema 7).
5. Il 4 ottobre è festivo per legge dal 2026 (tema 5).

**Non letto in questa ricerca** (da leggere prima di chiudere): messaggio INPS 8460/2013; Appendice G dell'Allegato tecnico PosPA;
file CNEL dei codici contratto; art. 4 del testo unico del D.Lgs. 33/2025 e art. 32-ter D.L. 185/2008 prima dell'abrogazione;
Circolare INPS 14/2026 (usata solo per la ricerca precedente); testo del CCNL comparto 2022-2024 art. 28; risoluzioni AdE citate
dalle istruzioni IRAP.
