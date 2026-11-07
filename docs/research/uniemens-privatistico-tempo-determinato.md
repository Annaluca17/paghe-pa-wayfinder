# UniEmens privatistico (DenunciaIndividuale) per i dipendenti a tempo determinato

Ticket: #77. Data: 2026-11-07.

## Domanda

Un ente locale (CCNL Funzioni Locali) con dipendenti a **tempo determinato** invia, oltre alla ListaPosPA della gestione pubblica, una denuncia UniEmens individuale **privatistica** (`PosContributiva` / `DenunciaIndividuale`). Che cosa contiene per questi lavoratori e come si compila?

1. Perché e da quando: quali contribuzioni del tempo determinato pubblico vanno nella gestione privata INPS (NASpI, addizionale, malattia, maternità), con aliquota, base, chi paga, norma, e variazioni per tempo determinato, supplenti, part-time.
2. Elementi della `DenunciaIndividuale` che servono: qualifiche, `TipoContribuzione`, codici, imponibile, contributo, settimane e giorni, `TipoLavStat`; nomi, formato, regole.
3. Part-time: `GiorniDirittoPartTime`, `PercPartTimeMese`, `DR00` (circolare INPS 74/2021, messaggio 2162/2021), ogni elemento di giorni e ore per verticale e misto; calcolo da una programmazione; minimale.
4. Legame con la ListaPosPA dello stesso mese: matricola, codici dell'ente, coerenze, mesi senza imponibile.
5. Effetto del 01/01/2027 (testi unici).

## Metodo e legenda

Legenda, come negli altri documenti di `docs/research/`:

- **norma certa**: testo normativo o istruzione ufficiale INPS letta sul testo.
- **prassi-interpretazione**: lettura di prassi o inferenza argomentata. Quando è una mia inferenza lo scrivo.
- **da verificare**: non letto sul testo, letto solo tramite altri, o non determinato dalle fonti.

**Letti sul testo (PDF scaricati da INPS e convertiti con `pdftotext`)**

- [DT] Documento tecnico UniEmens individuale v. 4.33 del 29/09/2026 (255 pp.). Gli elementi di `DenunciaIndividuale` sono alle pp. 39-76, `DatiRetributivi` alle pp. 50-57, `DenunciaAziendale` alle pp. 155-171, `ListaPosPA` alle pp. 176-186.
- [AT] Allegato tecnico 4.33.1 del 30/10/2026, Appendice B: `Qualifica1/2/3` pp. 108-110, `TipoContribuzione` pp. 111-122, `Cittadinanza` p. 122, `TipoPaga`/`TipoRetrMal` pp. 126-127, `TipoAssunzione`/`TipoCessazione` pp. 127-130, `TipoLavStat` pp. 133-134, `TipoCopertura` p. 157, `TipoImpiego` pp. 235-236, Appendice D p. 281. Per le tabelle ho usato `pdftotext -raw`, perché con `-layout` i codici si scollano dalle descrizioni.
- [C74] Circolare INPS 74 del 04/05/2021 (testo intero). [M2162] Messaggio INPS 2162 del 03/06/2021. [M2655] Messaggio INPS 2655 del 19/07/2024.
- [C140] Circolare INPS 140 del 14/12/2012 (ASpI, contributi). [C94] Circolare INPS 94 del 12/05/2015 (NASpI). [M4623] Messaggio INPS 4623 del 15/03/2013 con Allegato 1 (tabelle delle aliquote 2013). [M4152] Messaggio INPS 4152 del 17/04/2014. [C91] Circolare INPS 91 del 04/08/2020.
- [C125] Circolare INPS 125 dell'11/09/2025 (contratti di ricerca e post-doc: par. 4 «Obblighi contributivi», par. 5 e 6 «esposizione nei flussi»). Copia del PDF INPS ospitata dal sito di un ateneo (l'URL INPS non è risultato raggiungibile).
- [C6] Circolare INPS 6 del 30/01/2026 (minimali 2026). Copia del PDF INPS ospitata da una associazione di categoria.
- [M1058] Messaggio INPS 1058 del 07/03/2022 (codice contratto unico, `CPUB`).
- [N] Normattiva, via lo strumento di lettura web, che restituisce una sintesi del testo e non l'HTML: L. 92/2012 art. 2 (anche con `!vig=2027-01-02`), D.Lgs. 22/2015 art. 2, L. 845/1978 art. 25, D.L. 463/1983 art. 7 (`!vig=2027-01-02`), D.Lgs. 81/2015 art. 11 (`!vig=2027-01-02`), D.Lgs. 314/1997 art. 6 (`!vig=2027-01-02`). Per le affermazioni importanti c'è un riscontro INPS sul testo.

**Letti solo in parte o tramite altri**

- [C31] Circolare INPS 31 del 30/01/2025 (apprendistato e CFL nelle PA, art. 3-ter D.L. 44/2023): trascrizione integrale su un sito di studio professionale, non il PDF INPS (non raggiungibile). **da verificare** sul PDF.
- Messaggio INPS 3014/2026 («Codici Contratto» v. 60 di settembre 2026): solo la sintesi ANCE. **da verificare**.
- D.Lgs. 117/2026 (testo unico imposte sui redditi): letti solo preambolo, art. 1 e indice; non gli articoli.

**Non letti**

- Schema XSD 4.33.1: non trovato un URL scaricabile. Nomi, formati e obbligatorietà vengono da [DT] e [AT], non dallo schema.
- Manuale del Software di controllo UniEmens e relativi codici di errore (i codici `0xxxxE` che cito vengono dal tool interno, vedi sotto).
- Messaggi INPS 2641/2021 e 939/2022 (citati da [M2655]): non trovati; messaggio 263/2026 (codice `MACS`, versamenti di enti esclusi dal F24): citato da una pagina INPS, non letto.
- File INPS «Codici Contratto» (elenco dei codici CNEL).
- Testo di D.L. 87/2018 (non applicazione alle PA dell'incremento dell'addizionale): letto solo come nota su Normattiva.

**Piste interne, non citabili come fonte**: `docs/research/part-time-lista-pos-pa.md` e `docs/research/conoscenza-tool.md`; il tool `uniemens-builder-privati` (codice e spec); `vault-pa` (le note previdenziali non contengono nulla di utile su NASpI o DenunciaIndividuale). Dal tool ho preso regole e riferimenti da verificare. Dai flussi di prova non ho copiato alcun dato.

## Sintesi

1. **Perché.** I tempi determinati delle PA sono assicurati contro la disoccupazione (ASpI dal 01/01/2013, NASpI dal 01/05/2015); i tempi indeterminati no. La gestione pubblica non ha questa assicurazione: il contributo e i dati utili alla prestazione stanno nella gestione privata INPS, sotto una **matricola DM** dell'ente. **norma certa** [C140 §1, C94 §1-2, C125 §4].
2. **Contributo.** Il contributo NASpI è **1,61%** della retribuzione imponibile ai fini previdenziali, tutto a carico dell'ente: ordinario 1,31% (L. 92/2012 art. 2 c. 25) più integrativo 0,30% (L. 845/1978 art. 25 c. 4). Riscontro in tre fonti INPS indipendenti (circolari 140/2012 e 125/2025, tabelle del messaggio 4623/2013); la legge conferma la componente 0,30% e l'impianto. **norma certa**.
3. **Non dovuti.** Addizionale 1,40% (art. 2 c. 29 lett. d L. 92/2012), malattia, maternità, CUAF, fondo garanzia TFR. IVS, TFS/TFR, credito stanno in ListaPosPA. **norma certa**.
4. **Né supplenti né part-time cambiano l'aliquota.** Cambiano la base (retribuzione effettivamente imponibile, con i minimali) e `Qualifica3` (`A` sostituzione, `D` altri a termine). **norma certa** sull'aliquota; il resto **prassi-interpretazione**.
5. **Codice di contribuzione.** `TipoContribuzione` **71**: «solo contributo DS» per il personale di Amministrazioni non soggette a CUAF (Comuni compresi). Il codice è nell'allegato tecnico; che sia quello dei tempi determinati dei Comuni con IVS in CPDEL è una mia inferenza. **norma certa** sul codice, **prassi-interpretazione** sull'uso. `CodiceContratto` = `CPUB` con `TipoCodiceContratto` = `02` [M1058], ma il file codici è cambiato a settembre 2026: **da verificare**.
6. **Part-time.** `PercPartTime` (percentuale del contratto, mai variata mese per mese) e `PercPartTimeMese` (percentuale dell'orario del mese: 100 con lavoro per l'intero mese, 0 senza lavoro, «da ricavare» nei mesi parziali) sono **in centesimi** (100% = 10000), non in millesimi come nella ListaPosPA. Il **«da ricavare» non ha formula** nelle fonti. **norma certa** sul testo, **da verificare** sulla formula.
7. **`GiorniDirittoPartTime` non è per noi.** Esiste solo nelle sezioni dei fondi speciali (FS, ex Ipost, esattoriali, gas). Per tutti gli altri il «solo diritto» si dichiara con `TipoCopertura` = `D` nelle `Settimana`, `Lavorato` = `N` nei `Giorno` e, a mese intero non lavorato, `TipoLavStat` = `DR00`. **norma certa**.
8. **Il punto aperto.** Circolare 74 e messaggio 2162 si rivolgono a FPLD, ex Enpals e fondi speciali, e dicono che per la gestione pubblica l'estratto conto è già inclusivo del tempo non lavorato. Nessun testo letto dice se `D` e `DR00` vanno dichiarati nella posizione «solo DS» di un ente. Per la NASpI le settimane `D` non contano (C94, C74 §8). **da verificare** con INPS: è la decisione principale.
9. **Legame con la ListaPosPA.** Stesso `<Azienda>` (`AnnoMeseDenuncia` + `CFAzienda`), stesso `CFLavoratore`; la ListaPosPA ha `PRGAZIENDA`, la privata `Matricola` DM. Non ho trovato controlli incrociati documentati tra i due rami: le coerenze (tipo impiego, qualifiche, date, mesi senza lavoro) sono mie inferenze. Termine comune: ultimo giorno del mese successivo.
10. **01/01/2027.** Nessun testo unico trovato su contributi INPS o NASpI. Le norme citate risultano invariate su Normattiva a `!vig=2027-01-02`. Toccano indirettamente la base contributiva (D.Lgs. 314/1997 art. 6 rinvia agli artt. 46 e 48 TUIR, sostituiti dal D.Lgs. 117/2026) e il versamento (D.Lgs. 33/2025). I codici `ID/IG/IS` della circolare 31/2025 valgono per le assunzioni fino al 31/12/2026.

## 1. Perché la denuncia privatistica, e da quando

### 1.1 Quadro

- **Chi è assicurato.** L'ASpI (L. 92/2012 art. 2 c. 1-2) copre «tutti i lavoratori dipendenti» con esclusione dei **dipendenti a tempo indeterminato** delle PA (art. 1 c. 2 D.Lgs. 165/2001). La circolare 140/2012 elenca tra gli assicurati i «dipendenti a tempo determinato delle amministrazioni pubbliche» e dice che l'esclusione si fonda solo sull'essere a tempo indeterminato [C140 §1.1-1.2]. **norma certa**.
- **NASpI.** Dal 01/05/2015 la NASpI (D.Lgs. 22/2015) sostituisce ASpI e mini-ASpI per gli eventi di disoccupazione da quella data; stessa esclusione dei tempi indeterminati delle PA [C94 §1, §2.1; N: D.Lgs. 22/2015 art. 2 c. 1]. Il finanziamento resta quello dell'ASpI [C94 §9]. **norma certa**.
- **Perché la gestione privata.** La NASpI è erogata dalla Gestione prestazioni temporanee ai lavoratori dipendenti [C94 §1]; la ListaPosPA è la denuncia delle gestioni ex INPDAP [DT p. 37]. Per questo il datore pubblico che ha tempi determinati deve avere una **matricola DM** e fare «gli adempimenti informativi e contributivi» verso l'INPS; chi non ce l'ha deve chiederla [C125 §4, con rinvio alle circolari 2/2007 e 80/2014]. **norma certa**.
- **Perché i dati contano per il lavoratore.** La NASpI richiede 13 settimane di contribuzione contro la disoccupazione negli ultimi 4 anni (valide le settimane retribuite con retribuzione non inferiore ai minimali settimanali) e 30 giornate di lavoro effettivo nei 12 mesi, quelle con codice «S» nel flusso mensile; la misura parte dalla retribuzione imponibile esposta in UniEmens divisa per le settimane `X` o `2`, per 4,33 [C94 §2.2-2.3; DT p. 75 su `Lavorato`]. Un errore di `Imponibile`, di `Settimana` o di `Lavorato` cambia la prestazione. **norma certa**.
- **Da quando.** Contributo dai periodi maturati dal **01/01/2013** (L. 92/2012 art. 2 c. 25; C140). Prima del 2013 non ho letto la disciplina del tempo determinato pubblico (la C140 accenna a «previgente assicurazione DS» con requisito di stabilità d'impiego): **da verificare** se serve la storia.
- **Lettura estensiva.** La C125 parla di contratti di ricerca e post-doc, ma il par. 4 «rammenta» le regole generali per le PA che assumono a tempo determinato; la stessa formulazione, con gli stessi importi, è nella C31 (apprendistato e CFL nelle PA) [C31 par. 3, via trascrizione]. Applicarla a tutti i tempi determinati di un ente locale è una lettura coerente con C140 e C94. **prassi-interpretazione**.

### 1.2 Contribuzioni

| Voce | Aliquota | Base | A carico | Riferimento | Marcatura |
|---|---|---|---|---|---|
| Contributo ordinario NASpI | 1,31% | retribuzione imponibile ai fini previdenziali | datore | L. 92/2012 art. 2 c. 25 (rinvio agli artt. 12 c. 6 e 28 c. 1 L. 160/1975); C140 §3; C125 §4 | norma certa |
| Contributo integrativo | 0,30% | idem | datore | L. 845/1978 art. 25 c. 4 [N]; C140 §3; C125 §4 | norma certa |
| **Totale** | **1,61%** | idem | datore | C140 §3 («1,61% (1,31% + 0,30%)»); C125 §4; M4623 tabelle 2.1-2.3 (1,31 + 0,30 nel «TOTALE lav. NON a tempo INDETERMINATO») | norma certa, 4 fonti |
| Addizionale | 1,40%, **non dovuta** | | | L. 92/2012 art. 2 c. 28; esclusione c. 29 lett. d (PA); C140 §4.1; M4623 avvertenze; C125 §4 | norma certa |
| Incremento 0,5 punti a rinnovo | non applicabile alle PA | | | art. 2 c. 28 come modificato dal D.L. 87/2018, che non si applica ai contratti delle PA (nota su Normattiva) | da verificare sul testo del D.L. |
| Malattia, maternità | **non dovute** | | | C125 §4 («la tutela è garantita direttamente dal datore»); M4623 tabelle 2.1-2.3 («escluso dai contributi TFR, CUAF, MALATTIA e MATERNITÀ») | norma certa |
| CUAF, fondo garanzia TFR | non dovuti | | | M4623 tabelle 2.1-2.3; AT, cod. 71 («aziende non soggette alla disciplina della CUAF») | norma certa |
| IVS, TFS/TFR, gestione creditizia e sociale, ex ENPDEP | in ListaPosPA | | | C125 §4 | norma certa |
| Riduzioni del costo del lavoro sul 1,31% (art. 120 L. 388/2000, ecc.) | previste dal c. 26 per i datori privati | | | C140 §3.1 | **da verificare** se valgono per un ente pubblico |

**Chi paga.** Tutto il 1,61% è a carico del datore: nelle tabelle M4623 la voce «di cui a carico del lavoratore» riguarda solo il Fondo pensioni FPLD (9,19), non la NASpI, e la C140 §3 dice che il contributo ordinario è «a carico dei datori di lavoro». **norma certa**.

**Variazioni.**
- *Tempo determinato, supplenti:* nessuna differenza di aliquota; l'esclusione dell'addizionale vale per tutte le PA, non per la sostituzione. Il codice `Qualifica3` = `A` («tempo determinato per sostituzione di lavoratori assenti», dal 01/2013) e `D` («restanti tipologie») distingue le due ipotesi; per la sostituzione l'INPS ha chiesto di continuare a esporre `A` perché opera l'esenzione [M4152 par. 1.1]. Per una PA l'esenzione vale comunque (lett. d), quindi la scelta A/D non cambia il contributo. **norma certa** sui codici, **prassi-interpretazione** sull'irrilevanza contributiva.
- *Part-time:* stessa aliquota; la base è la retribuzione effettiva (§3.4 sul minimale). **prassi-interpretazione**.
- *Inquadramento della matricola:* le tabelle M4623 danno per i Comuni, personale iscritto al FPLD, CSC 2.01.01 con c.a. 6A (Comuni, Province, Regioni), 6B (Comunità montane), 6C (altri enti territoriali), 9G e altri (tabelle 2.1-2.3, del 2013, per personale con IVS in FPLD). Non è detto che sia l'inquadramento di una matricola «solo DS»: **da verificare**.

## 2. Elementi della DenunciaIndividuale

### 2.1 Dove sta, struttura

- Percorso: `DenunceMensili / Azienda / PosContributiva (Composizione, Matricola) / DenunciaIndividuale` più, una sola volta per posizione e mese, `DenunciaAziendale` [DT pp. 36-39]. **norma certa**.
- `Azienda` è univoca per `AnnoMeseDenuncia` + `CFAzienda`. `AnnoMeseDenuncia` minimo `2009-10` per `PosContributiva`, `2012-10` per `ListaPosPA`; con più gestioni per lo stesso `CFAzienda` vale il vincolo più restrittivo [DT p. 36].
- **Criteri di univocità** della denuncia individuale: `CFLavoratore`, `Qualifica1`, `Qualifica2`, `Qualifica3`, `TipoContribuzione`. Se nel mese cambia uno di questi (per esempio da tempo pieno a part-time), servono due denunce distinte [DT p. 23]. Per variare l'inquadramento: `InquadramentoLavVariaz` (dal 01/05/2013) [DT p. 42].
- Rettifiche: nuova denuncia con gli stessi dati identificativi sostituisce la precedente; per eliminare, attributo `Elimina="S"`; gli elementi «con valenza contributiva» (tra cui `Qualifica1-3`, `TipoContribuzione`, `Imponibile`, `Contributo`) generano un titolo di regolarizzazione se variati [DT pp. 22-24]. **norma certa**.
- Termine: l'ultimo giorno del mese successivo alla competenza; se festivo, il primo giorno lavorativo; invii frazionabili [DT p. 22]. **norma certa**.

### 2.2 Anagrafica e inquadramento

| Elemento | Contenuto e regola | Marcatura |
|---|---|---|
| `CFLavoratore`, `Cognome`, `Nome` | obbligatori; CF 16 caratteri (o 11); cognome max 30, nome max 20 [DT p. 42] | norma certa |
| `Qualifica1` | obbligatorio, con valenza contributiva. `1` operaio, `2` impiegato, `3` dirigente, `Q` quadro, `5` apprendista (dal 2007)... [AT p. 108-109]. Per i tempi determinati delle PA con contratti art. 3-ter D.L. 44/2023 la C31 vuole `2`. Per il comparto Funzioni Locali (operatore, istruttore, funzionario) non ho trovato una regola di corrispondenza | norma certa sui codici; **da verificare** per il comparto |
| `Qualifica2` | `F` tempo pieno, `P` orizzontale, `V` verticale, `M` misto [AT p. 110]; vietata se `Qualifica1` è `A`, `B`, `Z` [DT p. 42] | norma certa |
| `Qualifica3` | `I` tempo indeterminato, `A` TD per sostituzione, `D` TD restanti tipologie, `B` TD in provincia di Bolzano, `T`/`G`/`S` stagionali, `X` extra, `E` Fondo Trentino [AT p. 110; C91]. Per i tempi determinati di un ente: `D` o `A` | norma certa |
| `TipoContribuzione` | con valenza contributiva. Assente o `00` = nessuna particolarità. **`71`**: personale di aziende non soggette a CUAF (Amministrazioni statali, Regioni, Province, Comuni ecc.) «per il quale è dovuto il solo contributo per l'assicurazione contro la Disoccupazione (DS)». Altri: `61` IVS e DS; `62` solo IVS; `72` opzione INPDAP con DS e TFR; `10` non soggetti a DS [AT pp. 111-114]. Per i soli CFL/apprendisti art. 3-ter D.L. 44/2023: `IS` solo DS, `ID` DS e IVS piena, `IG` DS e IVS con Gescal ridotto, fino al 31/12/2026 [AT; C31] | norma certa sui codici; **prassi-interpretazione**: `71` è quello dei TD con IVS in CPDEL |
| `RegimePost95` | obbligatorio dal 2015; `S` se soggetto a regime contributivo, altrimenti `N` [DT p. 42]. Quale valore per un lavoratore con IVS in cassa pubblica: non detto | norma certa; **da verificare** |
| `Cittadinanza` | obbligatorio; `000` Italia [AT p. 122] | norma certa |
| `UnitaOperativa`, `UnitaProduttiva` | `0` in assenza di unità [DT p. 43] | norma certa |
| `CodiceComune` | Belfiore del comune di lavoro prevalente; ultimo comune nel mese [DT p. 43] | norma certa |
| `CodiceContratto`, `TipoCodiceContratto` | codice unico CNEL, `TipoCodiceContratto` = `02` dalla competenza 02/2022. Per i lavoratori iscritti a gestioni pubbliche per cui serve una denuncia nella privata, se il contratto è nel macrosettore CNEL «Amministrazione pubblica» il codice è **`CPUB`** [M1058]. Il documento «Codici Contratto» dalla v. 60 (09/2026) non contiene più il macrosettore CNEL [sintesi ANCE del msg 3014/2026] | norma certa [M1058]; **da verificare** dopo la v. 60 |
| `QualProf` | facoltativo, codice ISTAT CP2021 dalla competenza 05/2025 [DT p. 44] | norma certa |
| `TipoPaga` | facoltativo (obbligatorio solo con eventi CIG): `M`, `G`, `H` [DT p. 44; AT p. 126] | norma certa |
| `OrarioContrattuale` | ore settimanali previste dal contratto, in centesimi (36 ore = 3600); per i part-time l'orario del corrispondente tempo pieno [DT p. 44] | norma certa |
| `OrarioGiornMedioContrattuale` | deprecato; obbligatorio solo con eventi congedo parentale a ore (`MA0`, `MB0`): orario settimanale tempo pieno diviso i giorni di ripartizione, in centesimi (4000 su 5 giorni = 800) [DT p. 44] | norma certa |
| `TipoRetrMal` | obbligatorio «per tutti i datori di lavoro tenuti al versamento della contribuzione di malattia»; valori `0`, `1`, `2` [DT p. 45; AT p. 127]. Un ente non è tenuto alla contribuzione di malattia (§1.2): obbligo **da verificare** | norma certa; **da verificare** |
| `NumMensilita` | in millesimi (13 mensilità = 13000); per i part-time, anche verticale e misto, quelle del corrispondente tempo pieno [DT p. 45-46] | norma certa |

### 2.3 DatiRetributivi

| Elemento | Contenuto e regola | Marcatura |
|---|---|---|
| `TipoLavoratore` | «0» nella normalità [DT p. 52]. Esistono `CL` (CFL nelle PA, art. 3-ter D.L. 44/2023) e `AD` (apprendistato TD, stesso articolo) [AT; C31] | norma certa |
| `TipoLavStat` | (§3) `DR00` mese part-time verticale/ciclico senza prestazione; `NFOR` lavoratore non in forza (denuncia dopo la cessazione); `NR00` lavoratore non retribuito; `E000`/`S000` aspettativa per funzioni elettive/sindacali (valgono «non retribuito»); `LS01` LSU [DT p. 52; AT pp. 133-134] | norma certa |
| `Imponibile` | imponibile previdenziale del mese, **in unità di euro** (intero). Con valenza contributiva [DT p. 52] | norma certa |
| `Contributo` | obbligatorio se c'è `Imponibile`, può essere 0; **con virgola esplicita e due decimali**, arrotondamento per millesimi da 5 a 9 al centesimo superiore [DT p. 52, p. 31]. Qui: 1,61% dell'imponibile | norma certa; calcolo **prassi-interpretazione** (§Piste) |
| `ContribuzioneAggiuntiva/Contrib1PerCento` | per i privati; per la ListaPosPA va in `Contrib1PerCento` di ListaPosPA [C6 §5]. Non è un elemento della posizione «solo DS»: **da verificare** | da verificare |
| `RetribTeorica` | obbligatoria, anche 0; retribuzione del mese «sempre rapportata al mese intero» (salvo assunzione/cessazione), senza ultramensili, adeguata al minimale se inferiore; con `NumMensilita` forma la retribuzione globale annua [DT p. 54-55] | norma certa |
| `ForzImpZero` | attributo `"S"`: forza la presenza di imponibile a zero con settimane retribuite [DT p. 50] | norma certa |
| `GestioneTFR / MeseTFR / BaseCalcoloTFR` | `BaseCalcoloTFR` «deve essere indicato per la generalità dei lavoratori», anche 0 [DT p. 112]. Per un TD pubblico il TFR è gestito in ListaPosPA: se `GestioneTFR` sia richiesto resta **da verificare** | da verificare |

### 2.4 Settimane, giorni, giorni e ore contribuiti

| Elemento | Regola | Marcatura |
|---|---|---|
| `Settimana / IdSettimana` | progressivo della settimana (da domenica a sabato, o frazione) nell'anno, 1-54; una frazione a cavallo di mese si dichiara in entrambi i mesi [DT p. 74] | norma certa |
| `Settimana / TipoCopertura` | `X` totalmente retribuita; `1` totalmente non retribuita (evento tutelato figurativamente); `2` parzialmente retribuita; `D` solo diritto (part-time verticale/ciclico); `0` annulla [DT p. 74; AT p. 157]. Settimana senza retribuzione per eventi non tutelati: non si indica | norma certa |
| `Giorno` (attributo `GG`) | obbligatorio in costanza di rapporto dal 06/2012; assente solo prima dell'assunzione, dopo la cessazione, negli intervalli [DT p. 75] | norma certa |
| `Giorno / Lavorato` | `S`/`N`; `S` è un giorno con prestazione subordinata retribuita, **qualunque sia la durata**; `N` i giorni senza prestazione (anche per part-time: C74 §3) [DT p. 75; C74 §3] | norma certa |
| `GiorniRetribuiti` | giorni retribuiti nel mese: per ciascuna settimana, le giornate per cui il contratto stabilisce la retribuzione; «congruo con le coperture settimanali/giornaliere» [DT p. 55-56]. Con la C74: «da riferirsi unicamente al tempo lavorato» | norma certa; formula **da verificare** |
| `GiorniContribuiti` **oppure** `OreContribuite` | alternativi. `OreContribuite` per tempo parziale e intermittenti: ore su cui è stata versata contribuzione, **in centesimi** (1 ora = 100) [DT p. 56] | norma certa |
| `RispettoMinimale` | `S`/`N`: se la retribuzione debba essere adeguata al minimale; `N` per retribuzioni ridotte in presenza di malattia, maternità, CIG [DT p. 56] | norma certa; valore per un ente **da verificare** |
| `SettimaneUtili` | per i part-time: ore retribuite nel mese diviso l'orario contrattuale settimanale del tempo pieno; **in centesimi** (1 settimana = 100), da 0 a 460. Esempio DT: 100 ore su 40 = 250; 173 su 40 = 432 [DT p. 56] | norma certa |
| `GiorniUtili` | alternativa di `SettimaneUtili` solo per sport e spettacolo (TipoLavoratore `SC`...): non per noi [DT pp. 56-57] | norma certa |
| `OreLavorabili` | ore lavorabili del mese, per part-time «effettive» secondo orizzontale, verticale o misto; centesimi; obbligatorio solo con eventi CIG [DT p. 55] | norma certa |

La C74 conferma: nulla cambia per `SettimaneUtili`, `GiorniUtili`, `GiorniRetribuiti`, `GiorniContribuiti`, «da riferirsi unicamente al tempo lavorato» [C74 §3].

### 2.5 Assunzione e cessazione

- `Assunzione`: `GiornoAssunzione`, `TipoAssunzione` (`1` assunzione; `1R` assunzione a seguito di rinnovo di precedente rapporto a tempo determinato, circ. 121/2019; `3` rientro da sospensione; `9` altre) [DT p. 48; AT pp. 127-128].
- `Cessazione`: `GiornoCessazione`, `TipoCessazione` (`1C` fine contratto; `1B` dimissioni; `1G` risoluzione consensuale; `3` sospensione; `4` decesso; `9` altre) [DT p. 49; AT pp. 128-130]. Se nello stesso mese più assunzioni e cessazioni, si indica solo la prima assunzione; la cessazione solo se non seguita da nuova assunzione [DT p. 49]. **norma certa**.
- Settimane e giorni si dichiarano solo nel periodo di rapporto del mese [DT p. 75].

### 2.6 DenunciaAziendale e quadratura

Una per posizione e mese, anche con invii frazionati; l'ultima sostituisce [DT p. 39]. Obbligatori: `TrattQuotaLav` (`S`/`N`), `NumLavoratori` (lavoratori in forza; i part-time per intero), `ForzaAziendale` (a tempo pieno e part-time **in proporzione all'orario**; per verticale e misto ore prestate rapportate su base annua), `DatiQuadraturaRetrContr` con `NumDenIndiv`, `TotaleADebito` (intero, totale delle contribuzioni di tutte le denunce individuali del mese, «ex Totale A del DM10») e `TotaleACredito` [DT pp. 156-157, 171]. **norma certa**.

### 2.7 Formati, in breve

Maiuscole; importi interi in unità di euro (max 9 cifre; minimo 1 se obbligatori); importi contributivi con virgola e al più 2 decimali (`1234,5` esatto, `1234,567` errato); percentuali e ore **in centesimi**; date `AAAA-MM-GG`; elementi vuoti omessi [DT pp. 31-32]. **norma certa**.

## 3. Part-time

### 3.1 Elementi della DenunciaIndividuale

| Elemento | Dove | Contenuto | Marcatura |
|---|---|---|---|
| `Qualifica2` | inquadramento | `P`/`V`/`M` | norma certa |
| `PercPartTime` | `DenunciaIndividuale` | obbligatorio se part-time dal 07/2008. «Percentuale di part-time prevista nel contratto», indipendentemente dalla forma; **non è l'orario del mese**: un verticale con sei mesi a tempo pieno e sei di assenza è 50% «su tutte le denunce». **In centesimi** (65% = 6500) [DT p. 45]. Con la C74: invariata in tutti i mesi, con e senza prestazione, fino al nuovo contratto [C74 §3] | norma certa |
| `PercPartTimeMese` | idem | obbligatorio se `V` o `M` dal 06/2012. «Percentuale di part-time lavorata nel mese»: sei mesi pieni e sei di assenza danno 100% e 0%. **In centesimi** [DT p. 45]. Con la C74: «in riferimento all'orario di lavoro (lavorabile) del singolo mese»: 100% se lavorato l'intero mese, 0% se mai lavorato, «nei mesi parzialmente lavorati, la percentuale va ricavata» [C74 §3] | norma certa; formula **da verificare** |
| `TipoLavStat` = `DR00` | `DatiRetributivi` | «Lavoratore in contratto di part time verticale/ciclico, in assenza di prestazione lavorativa relativa all'intero mese» [AT p. 133]. Il messaggio 2162: marca il mese interamente privo di prestazione in cui c'è almeno un periodo interamente non lavorato per il part-time; convive di norma con l'assenza di `Imponibile`; se c'è, riguarda solo importi di tempo lavorato in mese diverso. Non va usato nei mesi parzialmente lavorati, né in caso di sequenza tra assenza tutelata (ferie, congedo retribuito) e part-time [C74 §3; M2162 §1-2] | norma certa |
| `Settimana / TipoCopertura` = `D` | `DatiRetributivi` | settimane totalmente non lavorate per il part-time. Le parzialmente lavorate restano `X` (o `2` con figurativo). Vietato su intere settimane di aspettativa o congedo non retribuito privo di tutela figurativa; una settimana mista aspettativa+part-time va `D` [C74 §3; M2162 §1c] | norma certa |
| `Giorno / Lavorato` = `N` | `DatiRetributivi` | giorni senza prestazione per il part-time [C74 §3] | norma certa |
| `GiorniRetribuiti`, `GiorniContribuiti`/`OreContribuite`, `SettimaneUtili` | `DatiRetributivi` | solo tempo lavorato (§2.4) | norma certa |
| `GiorniDirittoPartTime` | **solo** `FondiSpeciali` di `DatiParticolari`: `FondoFS`, `Esattoriali`, `GAS`, `ExIPOST`, e `DatiMeseIPOST`; con `Qualifica2` `V` o `M`; giorni di mancata prestazione, **30 nel mese** non lavorato, o parametrati a 30 se mese misto [DT pp. 132, 138; C74 §3; M2162 §1] | norma certa |
| ex Enpals | — | `TipoCoperturaGiorn` = `D`, riposo = `0` [M2162 §1, 3]: non per noi | norma certa |

`GiorniDirittoPartTime` non è dunque un elemento della posizione di un ente locale: richiede `TipoLavoratore` `FS`, `PS`, `ES`, `GA`.

**Errore nel testo ufficiale.** [DT] e [AT] datano la legge a «30 dicembre 2018»; la legge è la 178 del 30/12/**2020** (art. 1 c. 350) come dice la C74. Non è un problema di compilazione.

### 3.2 A chi si rivolgono circolare 74 e messaggio 2162, e per la PA

- La C74 tratta le «posizioni assicurative dei lavoratori dipendenti diversi dagli operai agricoli» e dà istruzioni per FPLD (`D` nelle settimane), ex Enpals (`D` nei giorni) e Fondi FS, ex Ipost, esattoriali, gas (`GiorniDirittoPartTime`) [C74 §3]. Per la gestione pubblica dice che la legge 554/1988 art. 8 rende utili per intero gli anni a orario ridotto, «l'estratto conto UNEX è già inclusivo del periodo riferito al tempo non lavorato» [C74 §1, §4]. Nessun passaggio nomina la posizione «solo DS» di un ente pubblico.
- Il par. 3 impone però l'invio mensile «anche per i periodi in cui non esiste prestazione lavorativa», precisando che **«l'obbligo discenderà dalla presenza del rapporto di lavoro, non dalla presenza di `<Imponibile>`»** [C74 §3]. È una regola generale sull'obbligo di trasmissione per il datore, non limitata alla pensione AGO.
- Per le prestazioni diverse dalle pensioni la C74 esclude effetti del riconoscimento fino al 31/12/2020 e per i periodi successivi «si confermano le disposizioni in essere» [C74 §8]; per la NASpI contano le settimane `X` e `2` [C94 §2.3] e le giornate `S` [C94 §2.2]. Nessun testo letto dà alle settimane `D` un valore per la NASpI (mia inferenza).
- Il messaggio 2655/2024 conferma che i contratti a termine con sospensione programmata nello **stesso** contratto (per esempio la sospensione estiva della ristorazione scolastica) rientrano nella norma sul riconoscimento del tempo non lavorato, mentre contratti a termine successivi e distinti no [M2655 §2]. Per l'ente locale è il caso tipico del verticale/ciclico a termine. Anche qui la sede è l'accredito per la pensione AGO.

**Esito.** Gli elementi esistono e sono fissati. Che vadano dichiarati nella posizione «solo DS» di un ente (con `D`, `DR00`, `Lavorato`=`N` e `PercPartTimeMese`) **non è determinato dalle fonti**: la regola scritta (`obbligo dal rapporto`) dice di sì per l'invio; l'utilità (nessun effetto né sulla pensione pubblica né sulla NASpI) dice che potrebbe essere inutile. **da verificare** con l'INPS (sede o call center datori di lavoro) o con il Software di controllo su un caso nominato.

### 3.3 Calcolo da una programmazione di giorni lavorativi e ore

Convenzioni: tempo pieno 36 ore su 5 giorni (7,2 ore/giorno), come nel CCNL Funzioni Locali; ore in centesimi. I numeri sono di fantasia. Le regole sono quelle del DT e della C74; dove l'INPS non dà la formula lo dico.

| Caso | `PercPartTime` | `PercPartTimeMese` | Ore e settimane | Giorni, settimane, stato |
|---|---|---|---|---|
| Orizzontale 50%, 22 giorni lavorativi tutti lavorati (79,2 ore) | 5000 | non richiesta (solo `V`/`M`) | `OreContribuite` 7920; `SettimaneUtili` = 79,2 / 36 = 2,20 → 220 | tutte le settimane `X`; `Lavorato` `S` nei giorni lavorati |
| Verticale 50%, mese con 10 giorni programmati su 22 (72 ore) | 5000 (contratto) | «da ricavare»: ore programmate / ore del tempo pieno nel mese = 72 / 158,4 = 45,45% → 4545 (lettura mia). Con ore uguali ogni giorno coincide con giorni / giorni lavorabili (10/22) | `OreContribuite` 7200; `SettimaneUtili` = 72 / 36 = 2,00 → 200 | `Lavorato` `S` nei 10 giorni, `N` negli altri; settimane con lavoro `X`; settimane intere non lavorate `D` |
| Verticale 50%, mese interamente non lavorato | 5000 | 0 | nessuna | `TipoLavStat` `DR00`; tutte le settimane `D`; tutti i giorni `Lavorato` `N`; niente `Imponibile` (o solo arretrati di altro mese) |
| Misto: giorni a orario ridotto, per esempio 8 giorni a 5 ore e 6 giorni a 7,2 ore (83,2 ore) | percentuale del contratto | stessa formula in ore: 83,2 / 158,4 = 52,53% → 5253. Con giorni/giorni lavorabili darebbe 14/22 = 63,64%: le due letture divergono | `OreContribuite` 8320; `SettimaneUtili` = 83,2 / 36 = 2,31 → 231 | come sopra |

**Formula di `PercPartTimeMese`: non determinata.** La C74 dice «in riferimento all'orario di lavoro (lavorabile) del singolo mese» e che nei mesi parziali «la percentuale va ricavata», senza formula. Le letture possibili sono due: giorni programmati sui giorni lavorabili del tempo pieno, oppure ore programmate sulle ore lavorabili del tempo pieno. Coincidono solo se le ore giornaliere sono uguali. La seconda segue l'esempio del DT sulle `SettimaneUtili` (ore retribuite sull'orario settimanale pieno) ed è l'unica che distingue il misto. **da verificare**. In ListaPosPA lo stesso problema aperto riguarda `PercPartTime` per `V` e `M` (`part-time-lista-pos-pa.md`).

**Scala.** `PercPartTime` e `PercPartTimeMese` della privata sono **in centesimi** (100% = 10000); `PercPartTime` della ListaPosPA è «in millesimi», con massimo 100000 [DT p. 185]. I due flussi non vanno alimentati con lo stesso numero senza conversione. **norma certa** sui testi, **da verificare** la scala esatta della ListaPosPA sull'XSD (aperta dal #72).

### 3.4 Minimale

- **Principio.** La retribuzione imponibile non può essere inferiore al minimale giornaliero (art. 7 c. 1 D.L. 463/1983, 9,5% del trattamento minimo FPLD) né al minimo contrattuale (art. 1 c. 1 D.L. 338/1989). **norma certa** [C6 §1; N].
- **2026.** Trattamento minimo 611,85 €/mese; minimale giornaliero **58,13 €**; limite settimanale di accredito (40%) **244,74 €**; annuo 12.726 € [C6 §1, §7]. **norma certa**.
- **Part-time.** Vale l'art. 1 c. 1 D.L. 338/1989, con un minimale **orario** (art. 11 c. 1 D.Lgs. 81/2015): minimale giornaliero per le giornate settimanali a orario normale, diviso le ore settimanali del tempo pieno del CCNL. Per 40 ore su 6 giorni: 58,13 × 6/40 = **8,72 €/ora**; per 36 ore su 5 giorni, «per i lavoratori iscritti alla Gestione pubblica»: 58,13 × 5/36 = **8,07 €/ora** [C6 §4]. **norma certa**.
- **Settimane e NASpI.** Per le 13 settimane valgono le settimane con retribuzione almeno pari al minimale settimanale; se l'annuale è sotto soglia il numero di contributi è il quoziente annuo / minimale settimanale (art. 7 c. 2 D.L. 463/1983) [C94 §2.2; N]. Le 30 giornate si contano «a prescindere dal minimale» [C94 §2.2]. **norma certa**.
- **Applicazione a un ente.** La C6 si intitola «generalità dei lavoratori dipendenti iscritti alle gestioni private e pubbliche» e il minimale orario cita la Gestione pubblica, ma nessun testo letto dice che il minimale si applichi alla base del contributo NASpI di un ente (che per la quota pensionistica ha regole proprie). `RispettoMinimale` `S` o `N` per un ente: **da verificare**.

## 4. Legame con la ListaPosPA dello stesso mese

| Aspetto | Regola | Marcatura |
|---|---|---|
| Contenitore | un solo `<Azienda>` (`AnnoMeseDenuncia`, `CFAzienda`) può avere sia `PosContributiva` sia `ListaPosPA`; o due flussi distinti; invii frazionabili [DT pp. 22, 36-37] | norma certa |
| Identità dell'ente | privata: `Matricola` (DM) in `PosContributiva`; il `CFAzienda` è di `Azienda`. ListaPosPA: `PRGAZIENDA` (5 cifre), `CFRappresentanteFirmatario`, `ISTAT`, `FormaGiuridica`, `PosPA` con `EnteAppartenenza` (`CFAzienda`, `PRGAZIENDA`, `ISTAT`, `RagSocAzienda`, `FormaGiuridica`) e `SedeServizio` [DT pp. 176-178]. La matricola DM non compare in ListaPosPA | norma certa |
| Il lavoratore | `CFLavoratore` è la chiave in `D0_DenunciaIndividuale` e in `DenunciaIndividuale` [DT pp. 23, 177] | norma certa |
| Chi va nella privata | solo chi è tenuto alla NASpI: i **tempi determinati**; il tempo indeterminato resta solo in ListaPosPA. Apprendisti e CFL art. 3-ter e contratti di ricerca hanno `TipoLavoratore`, `TipoContribuzione` e `TipoImpiego` propri [C31; C125] | norma certa |
| Tipo impiego e qualifiche | ListaPosPA `TipoImpiego`: `17` TD tempo pieno, `18` part-time TD (con `TipoPartTime` obbligatorio), `13` supplenti della Scuola, `48`/`49` art. 3-ter D.L. 44/2023, `52`/`53` ricerca e post-doc [AT p. 235-236; C31; C125]. Privata: `Qualifica2` `F`/`P`/`V`/`M`, `Qualifica3` `D`/`A`. Corrispondenza **mia**: `17` ↔ `F` + `D`/`A`; `18` ↔ `P`/`V`/`M` + `D`/`A`; `13` riguarda il personale scolastico statale, non i supplenti degli enti | **prassi-interpretazione** |
| Controlli incrociati | non trovato nessun controllo documentato tra `PosContributiva` e `ListaPosPA` (il manuale ListaPosPA 2018 non cita `PosContributiva`) | da verificare |
| Date | le date di rapporto (assunzione, cessazione) sono in `Assunzione`/`Cessazione` della privata e nei periodi `E0` e `CodiceCessazione` della ListaPosPA. Devono coincidere per coerenza; nessuna regola scritta | prassi-interpretazione |
| Mesi senza imponibile | ListaPosPA: il `E0_PeriodoNelMese` va compilato anche per i mesi senza prestazione del verticale (manuale 2018, ex. 13; part-time-lista-pos-pa). Privata: l'invio discende dal rapporto, non dall'imponibile [C74 §3]; con imponibile 0 e settimane retribuite: attributo `ForzImpZero`; mese di non lavoro: `DR00` (§3.1); non in forza: `NFOR`; non retribuito o aspettativa: `NR00`, `E000`, `S000`; per l'aspettativa non retribuita senza part-time nessuna `Settimana` se la settimana è tutta non retribuita [DT p. 74] | norma certa sui testi; scelta del caso **da verificare** |
| Termine | uguale per i due rami: ultimo giorno del mese successivo [DT p. 22] | norma certa |
| Versamento | `TotaleADebito` della privata (intero) è il «Totale A del DM10» per la matricola; l'esito dipende dal modo di versamento dell'ente (F24EP o, per enti esclusi, codice `MACS`, messaggio 263/2026 citato da INPS, non letto) | norma certa su `TotaleADebito`; **da verificare** il resto |

## 5. Effetto del 01/01/2027

- **Nessun testo unico su contributi INPS o NASpI trovato.** I testi unici che entrano il 01/01/2027 sono fiscali: D.Lgs. 117/2026 (TUIR) e D.Lgs. 33/2025 (versamenti e riscossione), già in `arrotondamenti-norma.md` e `differenze-errore-ente.md`; dalla ricerca web risulta anche un D.Lgs. 141/2026 sulla procedura tributaria (non letto). **prassi-interpretazione** (assenza di prova, non prova di assenza).
- **Normattiva `!vig=2027-01-02`:** L. 92/2012 art. 2 (commi 2, 25, 28, 29 lett. d presenti, ultimo aggiornamento 23/03/2026), D.L. 463/1983 art. 7 (ultimo aggiornamento 04/05/2023), D.Lgs. 81/2015 art. 11 (nessuna modifica 2026-2027), D.Lgs. 314/1997 art. 6, L. 845/1978 art. 25 (nessuna modifica 2026-2027 nelle note): nessuna abrogazione o rinvio a testi unici. **norma certa** sulle pagine lette.
- **Rinvio da ricontrollare.** Il D.Lgs. 314/1997 art. 6 (che sostituisce l'art. 12 L. 153/1969) definisce la base contributiva con rinvio agli artt. 46 c. 1 e 48 TUIR. Il D.Lgs. 117/2026 abroga il TUIR dal 01/01/2027 (art. 376 c. 1 lett. e; `differenze-errore-ente.md`); dall'indice il lavoro dipendente è nel Capo IV, artt. 51-54. Su Normattiva a `!vig=2027-01-02` il rinvio dell'art. 6 appare ancora ai vecchi articoli, e la clausola generale sui rinvii non è stata letta. **da verificare**. La retribuzione imponibile del contributo 1,61% dipende da quel rinvio.
- **Versamento.** Scadenze e regole di riscossione del contributo DM passano dal D.Lgs. 33/2025 (art. 243: dal 01/01/2027). Non riguarda gli elementi di UniEmens. **da verificare** sul testo dell'allegato.
- **Codici datati.** Il documento tecnico e l'allegato (4.33.x) sono versioni datate: codici e contratti (`CPUB`, file «Codici Contratto» v. 60) vanno in tabella con la data. I codici `ID`/`IG`/`IS` e le `Qualifica` della C31 valgono per assunzioni fino al 31/12/2026 [C31]; non toccano i tempi determinati ordinari.

## Piste interne (non citabili come fonte)

Nel tool `uniemens-builder-privati` ho trovato conferme e **discrepanze** con [AT], da portare nei controlli e nei test:

1. **Conferme.** Aliquota di default 1,61% e giorni retribuiti 26; `TipoContribuzione` `71` presente nella lista; calcolo di `IdSettimana` progressivo dalla settimana che contiene il 1° gennaio, settimane domenica-sabato con frazioni in entrambi i mesi (coerente con [DT p. 74]).
2. **Etichette sbagliate nella spec del tool (`UniEmens_Privatistico_Spec_v2.md`) e nel codice.** `Qualifica3`: la spec dice «D=dipendente, I=intermittente»; [AT] dice `D` tempo determinato (restanti), `I` tempo indeterminato. `TipoCessazione`: la spec dice `1B` fine contratto; [AT] dice `1B` dimissioni, `1C` fine contratto. `TipoLavStat`: la spec dice `NR00` non in forza; [AT] dice `NR00` non retribuito e `NFOR` non in forza (nel codice `NR00` è giusto, ma `NFOR` è etichettato «Non formale»).
3. **Codici di errore del validatore INPS** (citati nel codice, non letti su fonte INPS): `02560E`, `02570E`, `02580E` (rapporto tra settimane coperte e `GiorniRetribuiti`: settimane ≤ giorni e settimane × 6 ≥ giorni), `07780E` (giorno lavorato senza `Settimana`), `02990E` (settimana non congrua con il mese), `00940E` (TFR a febbraio), `00820E` (`Qualifica2` `F` con `PercPartTime`), `00090E`. Il [DT] dice solo che `GiorniRetribuiti` deve essere «congruo». **da verificare**.
4. **Contributo e imponibile.** Il README del tool riporta che l'XML ha `Imponibile` intero ma il contributo si calcola sul valore a centesimi (su 951,56 fa 15,32; da 952 farebbe 15,33), e che sui flussi trasmessi vale il primo. Il [DT] non dice su quale base si calcoli `Contributo`. **da verificare**.
5. **Uso nel flusso reale.** I flussi di prova analizzati (solo struttura) usano `CodiceContratto` `CPUB` con `TipoCodiceContratto` `02`, in linea con [M1058].

## Esito per il grilling

Decisioni che servono a Luca, nell'ordine in cui bloccano. Per ognuna dico cosa ha trovato la ricerca; la scelta resta sua.

1. **Perimetro della vista.** Chi entra nella `DenunciaIndividuale` dell'ente locale: solo i tempi determinati con IVS in cassa pubblica (posizione «solo DS»)? Anche gli apprendisti e i CFL art. 3-ter (codici `ID/IG/IS`, `AD/CL`, fino al 31/12/2026), i contratti di ricerca? E un TD con IVS in FPLD (aliquota piena, `TipoContribuzione` `61` o `00`)? La ricerca copre solo il primo caso.
2. **`TipoContribuzione`.** `71` («solo DS») come valore da corpus per i TD? È una mia inferenza dal testo dell'allegato; va confermata con una denuncia accettata dal Software di controllo. In caso contrario `00`.
3. **Inquadramento.** `Qualifica1` per il comparto (2 impiegato? 1 operaio per le categorie A/B?), `Qualifica3` (`D`, e `A` per i supplenti in sostituzione), `RegimePost95`, `CodiceContratto` `CPUB`. Decidere se sono input dell'ente o regole del corpus; se `CPUB` regge dopo il file «Codici Contratto» v. 60.
4. **Base e aliquota.** Quale importo del modello alimenta `Imponibile` (l'imponibile previdenziale della ListaPosPA? quale gestione?) e dove vive l'aliquota 1,61% (dato di corpus datato 01/01/2013, 01/05/2015 per la prestazione, con le due componenti). Come si arrotonda `Contributo` (su valore reale a centesimi, `Imponibile` intero).
5. **Minimale.** Applicare 58,13 €/giorno e 8,07 €/ora (36 ore, 5 giorni) alla base del contributo? E `RispettoMinimale` `S` o `N`? Le fonti dicono che il minimale esiste e conta per le settimane NASpI, non che si applichi alla base di un ente.
6. **Part-time: dichiarare o no `D`, `DR00`, `Lavorato`=`N`.** È il punto principale. Opzioni: (a) dichiararli sempre, per rispettare l'obbligo «dal rapporto» di C74 §3; (b) solo con `PercPartTime`/`PercPartTimeMese`, senza `D`/`DR00`; (c) chiedere all'INPS. Raccomando di fare partire (c) e intanto produrre (a), perché `Lavorato` `S`/`N` e la presenza del rapporto sono regole generali e `D` non conta per la NASpI.
7. **Formula di `PercPartTimeMese`** nei mesi parziali: ore programmate sulle ore del tempo pieno (distingue il misto) o giorni sui giorni lavorabili? Le fonti non danno la formula. Proposta: ore, con bozza non trasmissibile e caso nominato finché l'INPS non conferma, come per la ListaPosPA (ADR 0026).
8. **Mesi senza prestazione né imponibile.** Emettere la denuncia (con `DR00`/`NR00`/`ForzImpZero` a seconda del caso) o ometterla? Il verticale a termine con sospensione estiva è il caso tipico degli enti.
9. **Programmazione come fonte di giorni e ore.** Conferma che `OreContribuite` e `SettimaneUtili` (e non `GiorniContribuiti`) si ricavano dalle ore programmate, e `GiorniRetribuiti` dai giorni programmati (formula da verificare con un caso nominato).
10. **Quadratura e completezza.** `NumDenIndiv`, `TotaleADebito` (intero, somma dei contributi), `TotaleACredito`, `ForzaAziendale` (part-time proporzionale all'orario, verticale e misto in ore annue) come controlli di completezza della vista (ADR 0015, 0022), con esito dichiarato; la matricola DM e il legame con il versamento (F24EP o `MACS`) come dato dell'ente.
11. **Il tool `Uniemens-private` come controllo (ADR 0022).** Replicare nei test le regole confermate dal DT e correggere nel tool le etichette sbagliate (`Qualifica3`, `TipoCessazione`, `NFOR`); decidere se i codici di errore del validatore (02560E ecc.) diventano regole del corpus con la fonte INPS, che ora manca.
12. **Riferimenti dal 01/01/2027.** Il rinvio di D.Lgs. 314/1997 art. 6 al TUIR va ricontrollato dopo l'entrata in vigore del D.Lgs. 117/2026; il versamento dipende dal D.Lgs. 33/2025. Decidere se il corpus cita ora le due versioni con vigenza.

## Fonti

**INPS, letti sul testo**

- Documento tecnico UniEmens individuale v. 4.33 del 29/09/2026: https://www.inps.it/content/dam/inps-site/pdf/prestazioni-e-servizi/uniemens-enti-amministrazioni/UniEMENSind.pdf
- Allegato tecnico 4.33.1 del 30/10/2026: https://www.inps.it/content/dam/inps-site/pdf/prestazioni-e-servizi/uniemens-aziende-private/UniemensInd_AllegatoTecnico.pdf
- Circolare 74 del 04/05/2021: https://servizi2.inps.it/CircolariZIP/Circolare%20numero%2074%20del%2004-05-2021.pdf
- Messaggio 2162 del 03/06/2021: https://servizi2.inps.it/MessaggiZIP/Messaggio%20numero%202162%20del%2003-06-2021.pdf
- Messaggio 2655 del 19/07/2024: file già scaricato per il #72 (`m2655.pdf`).
- Circolare 140 del 14/12/2012: https://servizi2.inps.it/CircolariZIP/Circolare%20numero%20140%20del%2014-12-2012.pdf
- Circolare 94 del 12/05/2015: https://servizi2.inps.it/CircolariZIP/Circolare%20numero%2094%20del%2012-05-2015.pdf
- Messaggio 4623 del 15/03/2013, Allegato 1 (tabelle aliquote): https://servizi2.inps.it/MessaggiZIP/Messaggio%20numero%204623%20del%2015-03-2013_Allegato%20n%201.pdf
- Messaggio 4152 del 17/04/2014: https://servizi2.inps.it/MessaggiZIP/Messaggio%20numero%204152%20del%2017-04-2014.pdf
- Circolare 91 del 04/08/2020: https://servizi2.inps.it/CircolariZIP/Circolare%20numero%2091%20del%2004-08-2020.pdf
- Messaggio 1058 del 07/03/2022: https://servizi2.inps.it/MessaggiZIP/Messaggio%20numero%201058%20del%2007-03-2022.pdf
- Circolare 125 dell'11/09/2025, copia ateneo: https://www.uniroma1.it/sites/default/files/field_file_allegati/circolare_125_11_09_2025_inps.pdf
- Circolare 6 del 30/01/2026, copia associazione: https://ascom.bo.it/wp-content/uploads/2026/02/Allegato-1-CIRCO-23-26_Circolare-INPS-n.-6-del-30-01-2026.pdf

**Normattiva (sintesi dello strumento di lettura, non HTML)**

- L. 92/2012 art. 2: https://www.normattiva.it/uri-res/N2Ls?urn:nir:stato:legge:2012-06-28;92~art2 (anche `!vig=2027-01-02`)
- D.Lgs. 22/2015 art. 2: https://www.normattiva.it/uri-res/N2Ls?urn:nir:stato:decreto.legislativo:2015-03-04;22~art2
- L. 845/1978 art. 25: https://www.normattiva.it/uri-res/N2Ls?urn:nir:stato:legge:1978-12-21;845~art25
- D.L. 463/1983 art. 7: https://www.normattiva.it/uri-res/N2Ls?urn:nir:stato:decreto.legge:1983-09-12;463~art7!vig=2027-01-02
- D.Lgs. 81/2015 art. 11: https://www.normattiva.it/uri-res/N2Ls?urn:nir:stato:decreto.legislativo:2015-06-15;81~art11!vig=2027-01-02
- D.Lgs. 314/1997 art. 6: https://www.normattiva.it/uri-res/N2Ls?urn:nir:stato:decreto.legislativo:1997-12-02;314~art6!vig=2027-01-02
- D.Lgs. 117/2026 (solo preambolo, art. 1 e indice): https://www.normattiva.it/uri-res/N2Ls?urn:nir:stato:decreto.legislativo:2026-06-19;117

**Secondari, non sostitutivi delle fonti primarie**

- Circolare INPS 31 del 30/01/2025, trascrizione: https://www.studiocerbone.com/?p=495156
- Messaggio INPS 3014/2026, sintesi ANCE: https://ance.it/2026/10/inps-msg-n-3014-2026-uniemens-aggiornato-il-file-codici-contratto/
- Messaggio INPS 263 del 27/01/2026 (codice `MACS`): citato da https://www.inps.it/it/it/dettaglio-approfondimento.schede-informative.49814.contributi-obbligatori-degli-iscritti-alla-gestione-dipendenti-pubblici.html

**Interne, solo piste**

- `docs/research/part-time-lista-pos-pa.md`, `docs/research/conoscenza-tool.md`, `docs/research/arrotondamenti-norma.md`, `docs/research/differenze-errore-ente.md`, ADR 0022 e 0026.
- `Progetto HR Tools/uniemens-builder-privati` (README, `docs/UniEmens_Privatistico_Spec_v2.md`, `src/UniEmensPriv.jsx`), letto in sola lettura.
