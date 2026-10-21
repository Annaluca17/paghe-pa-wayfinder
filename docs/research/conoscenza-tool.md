# Estrazione della conoscenza normativa dai tool esistenti

Ticket: #11 (mappa #1). Branch: `research/conoscenza-tool`. Data: 2026-10-21.

## Domanda

Quali regole di calcolo e conoscenze normative sono codificate nei tool esistenti dell'utente (uniemens-builder, F24EP-editor, verifica-770, estrattore-f24ep-quietanze, analizzatore-posizioni, indennita-amministratori, cedolino-parlante, costo-dipendente, Pensione-2.0, normative-monitor, Public-Payroll, payroll-italia-pro)? Catalogo di regole, parametri e tracciati con fonte dichiarata nel codice e livello di certezza; contratti di input/output dei tool che generano output obbligatori. Non si estrae la loro struttura come modello.

## Metodo e legenda

Fonte primaria: il codice sorgente dei tool, clonato in sola lettura (`git clone --depth 1`) il 2026-10-21. Tutti e 12 i repo sono stati raggiunti. Commit letti:

| Tool | Commit | Data ultimo commit |
|---|---|---|
| uniemens-builder | `33e22c5` | 2026-10-17 |
| F24EP-editor | `07e5143` | 2026-10-14 |
| verifica-770 | `15ab082` | 2026-10-21 |
| estrattore-f24ep-quietanze | `3d7ef03` | 2026-10-21 |
| analizzatore-posizioni | `dbda583` | 2026-10-20 |
| indennita-amministratori | `6d19640` | 2026-09-01 |
| cedolino-parlante | `edae08e` | 2026-10-04 |
| costo-dipendente | `e0724f1` | 2026-08-28 |
| Pensione-2.0 | `8d59bf4` | 2026-10-19 |
| normative-monitor | `037957b` | 2026-10-19 |
| Public-Payroll | `b59d700` | 2026-05-06 |
| payroll-italia-pro | `33ce2ef` | 2026-06-08 |

I riferimenti `file:riga` sono relativi alla radice di ciascun repo a quei commit.

Legenda di certezza (applicata a ciò che il codice dichiara, non a una rilettura dei testi normativi, che in questa sessione non sono stati riletti):

- **norma certa**: il codice cita una fonte puntuale e verificabile (articolo, circolare/messaggio con numero, specifica tecnica ufficiale) e il valore è coerente con essa o è stato riscontrato su file ufficiali prodotti dall'amministrazione (round-trip, controlli INPS). La fonte va comunque riletta prima dell'uso in produzione.
- **prassi-interpretazione**: regola dichiarata nel codice come prassi dell'operatore, deduzione da dati reali, scelta progettuale, oppure fonte citata in modo generico ("da indicare", "vault", "circolari INPS GDP").
- **da verificare**: valore senza fonte, fonte citata che appare imprecisa, valore in conflitto con un altro tool, oppure dichiarato provvisorio nel codice stesso.

Le osservazioni di chi scrive (incoerenze, lacune) sono marcate esplicitamente e non aggiungono riferimenti normativi che non stiano già nel codice.

## Sintesi (risposta)

1. La conoscenza normativa riusabile è concentrata in **sei tool PA**: uniemens-builder (tracciato DMA2/ListaPosPA e controlli INPS), F24EP-editor (tracciato telematico F24 EP, mappatura UniEmens -> F24 EP, ravvedimento), estrattore-f24ep-quietanze (raccordi voce/punto CU/codice tributo/quadri 770; verifica-770 ne è solo il build), analizzatore-posizioni (aliquote storiche ex INPDAP, regime TFS/TFR, regole di ricostruzione posizioni ante e post 2005), Pensione-2.0 (tabelle CCNL Funzioni Locali versionate con fonte per valore, utilità delle voci per pensione/13a/TFS/TFR, regole ultimo miglio PASSWEB) e costo-dipendente (oneri riflessi e IRAP sul fondamentale). **prassi-interpretazione** (giudizio di chi scrive).
2. Pensione-2.0 è il tool più vicino a "rules as code": ogni parametro e ogni tabella porta una stringa `fonte` con articolo, pagina del PDF ARAN o circolare, e distingue esplicitamente le scelte di prassi (es. `src/tabelle/parametri.ts:4-24`, `src/tabelle/ccnl-2022-24.ts:140-162`). Gli altri tool citano le fonti in commenti o README, con densità variabile. **prassi-interpretazione**.
3. Il dominio meglio coperto è la **previdenza ex INPDAP** (CPDEL, TFS/TFR, Fondo Credito): aliquote, imponibili, mappatura gestioni -> causali F24 EP, codici errore del Software di controllo INPS, messaggio INPS 3267/2026. Il **fisco** è coperto in due modi molto diversi: bene sul lato verifica (CU, 770, codici tributo, scadenze, ravvedimento), male sul lato calcolo (i due motori IRPEF, Public-Payroll e payroll-italia-pro, hanno formule divergenti e in parte errate secondo l'audit già scritto in cedolino-parlante). **prassi-interpretazione**.
4. Il **CCNL Funzioni Locali** è codificato in modo autorevole solo in Pensione-2.0 (CCNL 2019-21, 2022-24 del 23/02/2026, Ipotesi 2025-27 del 21/07/2026, IVC, comparto e conglobamento); costo-dipendente e Public-Payroll ne contengono sottoinsiemi coerenti sui tabellari ma non sulla gestione dell'indennità di comparto e dell'indennità specifica. **norma certa** per i valori di Pensione-2.0 (fonte puntuale), **da verificare** per gli altri.
5. La **contabilità armonizzata** (impegni, liquidazioni, mandati, reversali) non è codificata in nessun tool. L'unica conoscenza vicina è contabile-fiscale: raccordo F24 EP <-> quadro SX del 770 sulle compensazioni e mappatura dei righi F24 EP. **da verificare** (assenza constatata nel codice letto).
6. Gli output obbligatori effettivamente generati sono tre: **XML UniEmens DMA2/ListaPosPA** (uniemens-builder e il generatore dell'analizzatore), **file telematico F24 EP** (F24EP-editor, verificato byte per byte su 8 file AdE) e **stampa del modello F24 EP** su PDF ufficiale. CU, 770 e PASSWEB sono **letti e verificati**, non generati (verifica-770; Pensione-2.0 produce righe da digitare in PASSWEB, non un flusso). **norma certa** per i due tracciati, con le divergenze specifica/realtà documentate.
7. Ci sono **duplicazioni deliberate** (analizzatore vendorizza uniemens-builder e inps-extractor con ORIGINE.md; F24EP-editor porta il calcolo del repo F24EP-Ravvedimento-Operoso-2.0; verifica-770 è il build dell'estrattore) e **incoerenze reali** fra tool: aliquota TFS/TFR unica 6,10% contro 6,91% sugli ulteriori elementi TFR, proroga di Ferragosto sì/no, codice tributo 143E con due significati, indennità specifica 5,38 dentro o fuori dall'imponibile TFS, accessorio dentro o fuori dall'imponibile CPDEL, detrazioni per coniuge con due formule diverse. Dettaglio nella sezione Incoerenze. **da verificare** caso per caso (il 143E è risolto dalla tabella ufficiale presente nel repo F24EP-editor).
8. Per il modello alternativo il riuso più sicuro è di **dati e regole puntuali con fonte** (tabelle CCNL, aliquote storiche, mappature gestione->causale, raccordi CU/770/F24 EP, codici errore INPS, regole del messaggio 3267), non dei motori di calcolo, che incorporano scelte di prassi non tracciate in modo uniforme. **prassi-interpretazione**.

## Catalogo per tool

### 1. uniemens-builder

Scopo: compilazione assistita di flussi UniEmens DMA2 (quadri E0/V1) per enti locali, import da XML o da JSON dell'INPS Extractor, controlli di congruità, generazione XML e rendiconto PDF (README).

| Regola / conoscenza | Dove | Fonte dichiarata | Validità | Certezza |
|---|---|---|---|---|
| Mappatura tipo contributo -> gestione XML: TC1 CPDEL -> GestPensionistica CodGestione 2; TC6 contributo aggiuntivo 1% -> Contrib1PerCento; TC7 TFS/INADEL -> GestPrevidenziale CodGestione 6; TC9 Fondo Credito -> GestCredito CodGestione 9; TC6 solidarietà L. 166/91 come EnteVersante distinto; TC8 TFR versato dall'ente | `docs/specs.md`; `src/UniEmensBuilder.jsx:1045` | nessuna puntuale (dominio) | corrente | prassi-interpretazione |
| Congruità bidirezionale al centesimo (tolleranza 0,005) fra somma terne EnteVersante e gestioni: Σ imponibile TC1 = imponibile CPDEL (00171I); Σ contributo TC1+TC5+TC6 = CPDEL + 1% + solidarietà (00172I); Σ imponibile TC9 = imponibile Credito (00032I); Σ TC9 contributo = contributo Credito; Σ TC7 o TC8 = gestione TFS o TFR | `src/UniEmensBuilder.jsx:782-830`, `1481-1501` | codici errore del Software di controllo INPS; quadratura osservata "sempre esatta al centesimo" sui flussi reali (README) | corrente | prassi-interpretazione (codici INPS citati, regola bidirezionale dedotta dai flussi) |
| Imponibile CPDEL = imponibile Credito su ogni periodo | `src/UniEmensBuilder.jsx:748-753` | nessuna | corrente | da verificare |
| RegimeFineServizio 1 e 2 = TFR, 3 = TFS; prevale RegimeFineServizio su regimeTFS; terne del regime opposto segnalate | `src/UniEmensBuilder.jsx:314`, `756-779`, `1041` | nessuna | corrente | prassi-interpretazione |
| RetribValutabileTFR = ImponibileTFR x 1,25 + ImponibileTFRUlterioriElem; RetribTeoricaTabellareTFR è dato tabellare, mai calcolato | `src/UniEmensBuilder.jsx:1276-1294` | "rif. circ. 105/2012, msg. 2440/2019" | corrente | norma certa (fonte citata; coerente con errore INPS 00720I riportato in analizzatore) |
| Messaggio INPS 3267 del 14/10/2026: dalla denuncia di dicembre 2026 gli eventi (permessi L. 104, congedi D.Lgs. 151/2001) e il dante causa si dichiarano con V1 causale 7 CMU 5, IdentAtto 6-22, accanto al quadro principale (E0/V1C5 o V1C7 CMU 8); tabella IdentAtto -> evento, tipo servizio (4, 9, 42, 48, 49, 63, 64, 72, 73), contenuto di PercRetribuzione in millesimi, un elemento per giorno, max 3 nel mese, NumeroRegistro = CF del dante causa o del lavoratore (art. 33 c. 6); DataAtto = 14/10/2026 (00902I); annullamento con sole date e IdentAtto | `src/UniEmensBuilder.jsx:603-740` | msg. INPS 3267/2026; art. 1 c. 724 L. 199/2025; circ. 81/2015 e 40/2016 | dalla denuncia 12/2026 | norma certa (fonte puntuale e datata) |
| AnnoMeseErogazione = mese di pagamento effettivo, non mese del quadro | README | nessuna | corrente | prassi-interpretazione |
| Cumulo mensilità: su annualità intera GEN-DIC, dicembre = doppio, divisore 13, residuo su dicembre; su periodo parziale divisore N mesi | `docs/specs.md`; `src/UniEmensBuilder.jsx:2249-2265` | nessuna (analizzatore la chiama "prassi INPS, fino al 2011", senza fonte scritta) | ricostruzioni storiche | prassi-interpretazione |
| Tabelle codici: CausaleVariazione 1/5/6/7; TipoImpiego (1, 2, 8, 9, 10, 13, 14, 17, 18, 3-7, 11, 12, 35-37, con riduzioni aliquota ente per CFL e inserimento); TipoServizio 4/5/6/49; TipoPartTime P/V/M (non "O"); forma giuridica 2410-2790 (Comune 2430) | `src/UniEmensBuilder.jsx:1015-1046` | "Manuale PASSWEB Tabella 11"; XSD DMA2 | corrente | norma certa per TipoImpiego e TipoPartTime (fonte puntuale); prassi-interpretazione per il resto |
| Vincoli di sequenza XSD (E0 prima di V1 nello stesso D0; ordine Gestioni -> CodiceCessazione -> RetribTeorica -> RetribValutabile -> EnteVersante) | `src/UniEmensBuilder.jsx:255`, `523`, `565` | XSD DMA2 | corrente | norma certa |
| Errori INPS noti: 00124I (PosPA multipli -> PosPA unico) | `docs/specs.md` | Software di controllo INPS | corrente | prassi-interpretazione |

Contratto I/O (output obbligatorio UniEmens ListaPosPA, quadri E0/V1):
- Input: XML UniEmens già trasmessi (`parseUniEmensXML`) oppure JSON `_formato: "uniemens-builder-import"` dell'INPS Extractor (quadri ricostruiti da PASSWEB, senza anagrafica né frontespizio); dati di frontespizio mittente/azienda (CF mittente, CF azienda, PRGAZIENDA, ISTAT, forma giuridica).
- Output: XML DenunceMensili con PosPA unica e D0_DenunciaIndividuale, da validare con il Software UniEmens Individuale INPS (v4.1.0 citata in `docs/specs.md`) prima dell'invio; rendiconto PDF della congruità.

### 2. F24EP-editor

Scopo: produrre il tracciato telematico F24 EP leggendo i flussi UniEmens; ravvedimento di un F24 EP non versato; stampa sul modello ufficiale (README).

| Regola / conoscenza | Dove | Fonte dichiarata | Validità | Certezza |
|---|---|---|---|---|
| Tracciato F24 EP: record da 1900 caratteri (1897 dati + "A" + CR LF), sequenza A (M V+)+ Z, NU a zeri, AN a spazi, importi in centesimi; campi posizionali di A, M, V (22 righi da 71 byte, pos. 123-1684), Z; invarianti di quadratura (record V pos. 1743/1758/1774/1793, record M pos. 1873, record Z conteggi) | `docs/tracciato-f24ep.md` §1-8; `src/f24ep.mjs`; `tools/valida_f24ep.py` | Provvedimento AdE 1/12/2015, Allegato 2, versione dicembre 2016 (testo in `docs/allegato2-specifiche-tecniche-2016.txt`) | dal 2016 | norma certa (specifica nel repo; 8 file AdE ricostruiti byte per byte) |
| Divergenze specifica/realtà: CAB Banca d'Italia `04306` (non `03245`), filler record V pos. 1685-1742 a zeri (non spazi) | `docs/tracciato-f24ep.md` §7 | file reali prodotti dall'applicazione AdE | corrente | prassi-interpretazione (osservato 8/8) |
| Tipi riga F/I/R/S/N/Q/W/G/P/5 e regole di compilazione di codice, estremi, riferimento A e B; nel ciclo stipendiale osservati solo S, Q, F, R, I | `docs/tracciato-f24ep.md` §6 | Allegato 2, pagg. 19-20 | dal 2016 | norma certa |
| Scadenze di trasmissione: saldo > 0 entro le 20:00 del secondo giorno lavorativo precedente la data di versamento; saldo = 0 fino alle 24:00 del giorno; annullamento entro le 22:00 del secondo giorno lavorativo precedente | `docs/tracciato-f24ep.md` §10 | Allegato 2 | dal 2016 | norma certa |
| Mappatura UniEmens gestione pubblica -> sezione Q: GestPensionistica Contributo + Contrib1PerCento -> P201; ContributoTFS -> P607; ContributoTFR -> P608; ContributoTFRUlterioriElem -> P632; GestCredito -> P909; codice = sigla provincia T2 (non nel flusso); riferimento A/B = MMAAAA da GiornoInizio/GiornoFine | `src/importa-uniemens.mjs:23-37`; `docs/mappatura-uniemens-f24ep.md` §A | confronto con F24 EP reali (Noto), non documentazione | corrente | P201 (solo Contributo), P607, P909: prassi-interpretazione verificata su file reale; 1% in P201, P608, P632: **da verificare** (dichiarate "provvisorie" nel codice) |
| Gestione privata -> sezione I, causale DM10; codice sede = primi 4 caratteri di SedeINPS; estremi = matricola; importo = TotaleADebito - TotaleACredito; consolidamento per sezione + tributo + codice + estremi + periodo | `src/importa-uniemens.mjs:140-160`; `docs/mappatura-uniemens-f24ep.md` §B | file reali (67 denunce) | corrente | prassi-interpretazione |
| Controllo aliquota CPDEL implicita (Contributo/Imponibile) contro la mediana dei periodi, soglia 0,5 punti; caso reale 23,80% (quota ente) contro 32,65% (aliquota piena) nel mese di cessazione | `src/importa-uniemens.mjs:79-131` | nessuna (euristica) | corrente | prassi-interpretazione |
| Ravvedimento operoso: tassi legali annui 2010-2026 (2026: 1,6% esteso in avanti), interessi = importo x tasso x giorni / 36500; sanzione base 30% (pre) / 25% (post) e ridotta 15% / 12,5% per ritardi fino a 90 gg; scaglioni sprint (0,1%/giorno pre; 1/15 di 1/10 del minimo per giorno post), breve 1/10, intermedio 1/9, lungo 1/8 entro il termine del 770 (31/10 dell'anno successivo), oltre 1/7 (post-riforma), 1/7 e 1/6 (pre-riforma); principio del cumulo (tributo + interessi sullo stesso codice) | `src/ravvedimento.mjs:16-160` | art. 1284 c.c. e decreti MEF; D.Lgs. 87/2024 per violazioni dal 01/09/2024 | 2010-2026 | norma certa per l'impianto e la data di riforma; tassi: prassi-interpretazione (nessun decreto citato per anno) |
| Scadenza per rigo: 16 del mese successivo al Riferimento A, primo feriale se sabato/domenica; proroga di Ferragosto (art. 37 c. 11-bis DL 223/2006, introdotto da art. 3-quater DL 16/2012) **spenta** di default perché per l'F24 EP l'unica conferma trovata è un comunicato AdE del 6/8/2008 | `src/ravvedimento.mjs:205-230`; README | DL 223/2006; comunicato AdE 6/8/2008 | corrente | da verificare (incoerente con l'estrattore, vedi Incoerenze) |
| Mappa tributo -> codice sanzione (100E/102E -> 896E, 104E -> 897E, 380E -> 892E, 381E -> 893E, 384E/385E -> 891E; 175E e 170E a debito -> 896E per deduzione confermata dall'utente; 118E/124E/125E invariati) | `data/sanzioni-ravvedimento.json`; README | mappa del repo Ravvedimento; deduzioni dalle denominazioni 89xE | corrente | prassi-interpretazione ("vanno riviste", dichiarato) |
| Tabelle di decodifica: T0 regioni (21), T2 sigle province (111, AdE 17/10/2017), sedi INPS (218), comuni/catastale ISTAT al 21/02/2026 (7.894), 508 codici tributo | `data/*.json`; `docs/tracciato-f24ep.md` §9 | AdE, ISTAT | date indicate | norma certa |
| Riferimento B per addizionali e 730 (381E, 384E, 126E-128E, 131E-136E) è anno d'imposta, non anno di versamento: il rigo è segnalato "da verificare" | README | file reali | corrente | prassi-interpretazione |

Contratto I/O (output obbligatorio F24 EP):
- Input: XML UniEmens (ListaPosPA e/o PosContributiva), anagrafica ente JSON (denominazione, e-mail, IBAN tesoreria, sigla provincia sezione Q, data di versamento) oppure un F24 EP esistente da cui leggere il record M.
- Output: file `.txt` F24 EP (nome `F24EP` + AAMM della data di versamento + progressivo a 5 cifre), da passare al programma di controllo dell'Agenzia; PDF compilato sul modello ufficiale, una pagina per record V. Il tool non invia.

### 3. estrattore-f24ep-quietanze (sorgenti) e verifica-770 (build)

Scopo: verifica annuale del sostituto d'imposta mettendo a confronto quietanze F24 EP, F24 EP da procedura, estrazione voci, CU telematica, 770 (ST, SV, SX). `verifica-770/index.html` è prodotto da `build.py` dell'estrattore (README di verifica-770): stessa conoscenza, nessuna regola propria.

| Regola / conoscenza | Dove | Fonte dichiarata | Validità | Certezza |
|---|---|---|---|---|
| Agganci voci <-> punti CU (redditi 1-4, 449, 361-375, 21, 469, 511-513, 801/804, 391-395, 725/727, addizionali 22-28, 730 punti 61-327, interessi 141-153, previdenziali 4, 18-30) con le voci della procedura stipendi | `agganci.js:170-290` | "verificati al centesimo su Noto 2025 e per percipiente su altri 4 Comuni" | CU 2026 (anno 2025) | prassi-interpretazione (i codici voce 8118, 9003, 73xx ecc. sono della procedura Halley, non normativi) |
| Agganci voci <-> codici tributo F24 EP (100E con 155E e 6099; 102E; 170E; 175E; 381E/384E/385E con 160E/161E e anno A o A-1; 730: 134E, 148E, 133E, 147E, 129E, 143E, 150E, 118E, 126E, 153E, 124E, 128E, 125E; P201 = CPDEL a carico + 6507; P607; P608; P632 "TFR INPDAP 6,91"; P909; P206 previdenza complementare; DM10) | `agganci.js:338-375` | verifica mese per mese su 5 Comuni | corrente | prassi-interpretazione |
| Guida ai punti CU: contenuto, codici tributo associati, pagina delle istruzioni | `guida-cu.js` | "istruzioni CU 2026 dell'Agenzia" con pagina | CU 2026 | norma certa (fonte e pagina citate) |
| Tracciato CU telematica (fornitura CURnn): record G e H, codici campo = numero del punto (DB001021 = punto 21, DF001804 = punto 804, AU001009 = punto 9); eredi in DF001916 (CF erede) e DF001917 (quota) | `f24ep-core.js:1083-1160` | "Specifiche tecniche CU 2026, par. 3.2 e record G e H" | CU 2026 | norma certa |
| Punti 520-522 non si agganciano alle voci: sono il dettaglio per anno di 511-513; nessuna CU di dipendenti pubblici ha punti TFR perché il TFR lo paga l'INPS | `docs/adr/0004-...md` | dati 2025 di 8 Comuni | CU 2026 | prassi-interpretazione |
| Quadrature 770 <-> CU: chiusura ST 100E + 381E S + 384E S + 385E - SX1 col. 1 = punti 21 - 469 + 24 + 26 + 28; 102E = punto 513; 104E = punto 9 CU autonomi; 110E = punto 804; SX49 col. 2 = punti 391+393+394; 170E = 393; SX49 col. 4 = 394; 170E nota P = 395; SX50 col. 2 = 725+727; 175E = 727; SX2 = rimborsi 730; 730 per codice tributo | `f24ep-core.js:1987-2060` | istruzioni 770/CU (implicite), verifiche su Comuni | 770/2026 | prassi-interpretazione |
| Raccordi quadro SX <-> compensazioni F24 EP: SX1 col. 7 = 155E+160E+161E a credito; SX2 col. 2 = 150E+153E+154E a credito; SX49 col. 6 = 170E a credito; SX49 col. 3+5 = 170E a debito; SX50 col. 6 = 175E a credito; SX50 col. 3 = 175E a debito; filtro per anno della delega, non del rigo | `f24ep-core.js:940-975` | dati reali (Cefalù) | 770 corrente | prassi-interpretazione |
| Tolleranze per confronto: fisco 0; contributi 0,05 contro CU (arrotondamenti CU), 0 contro F24 EP; DM10 1 euro | `docs/adr/0005-...md`; `confronto.js:37-60` | dati reali | corrente | prassi-interpretazione |
| Scadenza F24 EP: 16 del mese successivo, primo feriale; per luglio sempre 20 agosto (proroga di Ferragosto), festività infrasettimanali ignorate | `f24ep-core.js:2491-2515` | nessuna puntuale | corrente | da verificare (vedi Incoerenze) |
| Anno della busta paga per addizionali e rate 730: il mese è quello della busta, l'anno di riferimento è quello d'imposta | `f24ep-core.js:2527-2538` | nessuna | corrente | prassi-interpretazione |

Contratto I/O: solo lettura e verifica. Input: PDF quietanze F24 EP, CSV F24 EP da procedura, estrazione voci (export del gestionale), 770 telematico `.txt`, PDF quadro SX, CU telematica `.txt` (CURnn), elenco ritenute finanziaria. Output: esiti dei confronti, JSON della lavorazione, Excel. Nessun output obbligatorio generato.

### 4. analizzatore-posizioni

Scopo: analizzare le posizioni assicurative PASSWEB (Elenco Quadri, Estratto BDC, Posizione SCAD, flussi ente, questionario ente), proporre correzioni e generare flussi UniEmens di variazione (PROGETTO.md, GLOSSARY.md). Contiene copie dichiarate di uniemens-builder e inps-extractor (`src/vendor/ORIGINE.md`).

| Regola / conoscenza | Dove | Fonte dichiarata | Validità | Certezza |
|---|---|---|---|---|
| Aliquote CPDEL totali (ente + dipendente) storiche: 23,00% dal 1954, 23,05% (1983), 24,00% (05/1985), 24,25% (1989), 24,55% (1990), 25,60% (1991), 26,35% (1992), 27,65% (1993), 28,15% (1994), 28,40% (1995), 28,75% (1996), 32,35% (12/1996), 32,65% dal 2007 | `src/aliquote.ts:7-11` | "INPDAP, Tabella D (vault: Aliquote Contributive Storiche)" | 1954-oggi | prassi-interpretazione (fonte secondaria interna) |
| Gestione previdenziale TFS e TFR insieme: 4,88% fino al 1992, 6,10% dal 1993; TFS imponibile all'80% dal 1993 | `src/aliquote.ts:13-14` | come sopra | 1954-oggi | da verificare (vedi Incoerenze: 6,91% per ulteriori elementi TFR) |
| Fondo Credito 0,35% sempre, anche prima del 12/1996 | `src/aliquote.ts:16-17` | "prassi dell'operatore, 10/10/2026" | sempre | prassi-interpretazione |
| Inizio Fondo Credito (FPRCR) 01/12/1996 | `src/regole/regime.ts:14` | L. 662/1996 | dal 12/1996 | norma certa |
| Regime atteso dalla storia dei contratti: TD in servizio al 30/05/2000 o assunto dopo -> TFR (resta TFR dopo stabilizzazione); TI assunto dopo il 31/12/2000 -> TFR; TI entro il 31/12/2000 -> TFS | `src/regole/regime.ts:16-38` | DPCM 20/12/1999 e 02/03/2001 | dal 2000 | norma certa (fonte puntuale) |
| Imponibile TFS/TFR di prassi ante 2005: 67% del CPDEL (80% fino al 1992), proposto e confermato dall'operatore | `src/regole/comuni.ts:94-106` | "prassi dell'operatore, 11/10/2026" | ante 2005 | prassi-interpretazione |
| Ante 2005 si sistema solo con denunce mensili a variazione, senza prova del versamento; INPS blocca scostamenti oltre il 20%; post 2004 ogni sistemazione va giustificata (CU, 770, ricevute); modifica diretta PASSWEB inibita dal 01/10/2025 | `PROGETTO.md:545-555`; `src/regole/importi.ts:146` (SOGLIA = 0,2) | L. 213/2023 art. 1 c. 131; circ. INPS 118/2025 | dal 2025 | norma certa (fonte puntuale) |
| Dal 10/2012 quadri mono-mese e principio di cassa (AnnoMeseErogazione = mese di GiornoInizio salvo cessati o sospesi, 00356I) | `src/vendor/extractor/uniemens.ts:60`; `src/generatore.ts:351-354` | manuale SCAD § 6.3.4.5; Software di controllo INPS | dal 10/2012 | norma certa per la soglia; prassi-interpretazione per l'eccezione |
| Regole del Software di controllo INPS applicate al generatore: 00064I (Contrib1PerCento solo se diverso da zero), 00720I/00095I (valutabile = imponibile TFR x 1,25 + ulteriori), 00273I/00688I (gestione previdenziale solo con imponibile TFS/TFR > 0), 00383I/00116I/00120I (tabellare e valutabile TFR obbligatori), 00566I (V1 con date almeno due mesi prima di AnnoMeseDenuncia), 00597I/00982I (V1 c6 solo dove nessun V1 c5 copre) | `src/generatore.ts:340-360`; `PROGETTO.md:1037-1038`, `1551` | esiti reali del Software di controllo INPS (Adrano, 11/10 e 15/10/2026) | corrente | norma certa nel senso di "comportamento verificato del controllore ufficiale" |
| Codice cessazione 32 = sospensione di periodo lavorativo utile, sull'ultimo mese lavorato giustifica il periodo vuoto; non è cessazione | `src/regole/fatti.ts:170-175` | manuale DMA2, tabella codice cessazione; prassi confermata | corrente | prassi-interpretazione |
| TipoImpiego TI = 1/8, TD = 17/18 | `src/regole/inquadramento.ts:124`; `src/regole/fatti.ts:256` | Manuale PASSWEB, Tabella 11 | corrente | norma certa |
| Mensilità pagate insieme: totale annuo ripartito in tredicesimi | `src/regole/tipi.ts:68`; `src/regole/importi.ts:89-91` | "prassi INPS, fino al 2011"; PROGETTO.md: "nessuna fonte scritta trovata" | fino al 2011 | prassi-interpretazione |
| Periodo di servizio senza retribuzione ante 2005, in TFR con tabellare: V1 c5 solo giuridico | `src/regole/tipi.ts:89-94` | circ. INPS 118/2025 §3; operatore 20/10/2026 | ante 2005 | prassi-interpretazione |
| Fonti dichiarate esplicitamente "da verificare": tipo servizio 49 = congedo straordinario, codice cessazione 18 = fine incarico, aspettative cariche elettive (circ. INPS 215/2016), arretrati dopo cessazione (msg. INPS 749/2024), allegato 1 msg. INPS 3284/2015 | `PROGETTO.md:1124-1132` | come indicato | — | da verificare (dichiarato) |

Contratto I/O (output obbligatorio UniEmens di variazione): input file PASSWEB (Elenco Quadri e Estratto BDC in Excel, Posizione SCAD), flusso ente XML, questionario e risposte JSON; output XML DMA2 (E0/V1 di variazione) prodotto dalla copia del builder, da passare al Software di controllo INPS, più report e domande all'ente.

### 5. Pensione-2.0

Scopo: ultimo miglio PASSWEB per pratiche di pensione (TFS o TFR), DMA previste, miglioramento contrattuale, cessazioni TFR (README).

| Regola / conoscenza | Dove | Fonte dichiarata | Validità | Certezza |
|---|---|---|---|---|
| Tabellari CCNL Funzioni Locali per area: dal 01/01/2024 Tabella B col. 1 (Funzionari EQ 2.078,47 mensili, Istruttori 1.915,55, Operatori esperti 1.704,38, Operatori 1.637,12); dal 01/01/2026 Tabella B col. 2 con parziale conglobamento del comparto (2.092,84 / 1.928,23 / 1.715,27 / 1.646,09) | `src/tabelle/ccnl-2022-24.ts:140-162` | CCNL FL 2022-24 del 23/02/2026, art. 56 c. 2, art. 60 c. 1, Tabella B p. 83 (URL ARAN) | 2024, 2026 | norma certa (decorrenza 2026 "dedotta", dichiarato) |
| Incrementi 2022-23 pari all'IVC (0,30% dal 04/2022, 0,50% dal 07/2022 e 01/2023), riassorbiti dal 2024; IVC per posizione in centesimi | `src/tabelle/ccnl-2022-24.ts:1-135`, `165-215` | art. 56 c. 1; tabelle IVC RGS 2022-23 "non riscaricate" | 2022-2023 | norma certa per l'articolo; prassi-interpretazione per gli importi (fonte non riscaricata) |
| IVC 2025: 0,6% del tabellare dal 04/2025, 1% dal 07/2025 | `src/tabelle/ccnl-2022-24.ts:195-215` | RGS; L. 207/2024 art. 1 c. 128 | 2025 | norma certa |
| Indennità di comparto: valori di partenza 51,90 / 45,80 / 39,31 / 32,40 (Tabella C col. 1); quota residua dal 2026 36,33 / 32,06 / 27,52 / 22,68 a carico del Fondo; quote conglobate distinte bilancio/fondo | `src/tabelle/ccnl-2022-24.ts:220-250` | CCNL FL 2022-24, Tabella C, p. 84 | 2019, 2026 | norma certa |
| Ipotesi CCNL 2025-27 del 21/07/2026 (non definitiva): Tabella B col. 1-3, comparto residuo con incremento | `src/tabelle/ccnl-2025-27.ts` | Ipotesi, art. 35, 36-bis, Tabella C p. 55 | dal 2025 (ipotesi) | da verificare (non definitiva, dichiarato) |
| Utilità delle voci per pensione / 13a / TFS / TFR (tabellare, differenziali, assegni, RIA, posizione: TFS no per prassi; indennità specifica 5,38: 13a no; comparto: solo pensione; vigilanza, asili, una tantum 1,5% 2023) | `src/tabelle/catalogo.ts:18-36` | ticket interni e vecchio codice; prassi per posizione e comparto | dal 2019 | prassi-interpretazione |
| Soglia TFR: almeno 15 giorni continuativi nel mese, conteggio lun-sab | `src/tabelle/parametri.ts:5-9` | circ. INPS 185/2021 §2.1; calendario per prassi | corrente | norma certa per la soglia, prassi per il conteggio |
| Retribuzione giornaliera = mensile / 26 | `src/tabelle/parametri.ts:10` | CCNL FL 2019-21, art. 74 c. 4 | dal 2019 | norma certa |
| Tetto 26 giorni nel mese parziale (lun-sab) | `src/tabelle/parametri.ts:11-14` | "prassi confermata dall'utente, senza fonte normativa" | corrente | prassi-interpretazione |
| Rateo di 13a in 365esimi di calendario | `src/tabelle/parametri.ts:15-18` | CCNL 2019-21 art. 75; circ. INPS 185/2021 | corrente | norma certa |
| Massimo 6 DMA previste in PASSWEB (non gli 8 mesi della circ. INPS 26/2019) | `src/tabelle/parametri.ts:19-23` | manuale PASSWEB v1.20 p. 60, prassi | corrente | prassi-interpretazione |
| Imponibili DMA: pensionistico = tutte le voci utili alla pensione, comparto compreso (art. 74 c. 2 lett. d); Credito = stesso imponibile CPDEL (msg. INPS 1974/2018 §2); TFS = 80% delle voci utili TFS (INADEL dal 01/01/1993); TFR: teorica = Σ voci utili TFR senza 13a né 80%; valutabile = base al 100% + ulteriori; ulteriori elementi = voci TFR sì e TFS no al 100%, contributo 6,91% (msg. INPS 2440/2019) | `src/tabelle/righe-passweb.ts:125-190` | come indicato | corrente | norma certa dove la fonte è puntuale; prassi per R1-R4 |
| Codici servizio 83 (sospensione cautelare) e 49 (congedo L. 104): retribuzioni utili solo a CPDEL e Credito | `src/motore/dma.ts:25-30` | prassi "Pensionamenti con situazioni particolari in corso" | corrente | prassi-interpretazione |
| Miglioramento contrattuale: per i cessati nella vigenza, incrementi integrali sulla pensione, su TFS/TFR solo quelli maturati alla cessazione | `src/motore/miglioramento.ts:30-40` | CCNL FL 2022-24 art. 57 c. 2; CCNL 2019-21 art. 77 c. 2; circ. INPS 125/2022 §3.2 | contratti 2019-21, 2022-24 | norma certa |

Contratto I/O: input dati della pratica (anche da PDF Halley via lettore); output righe da riportare manualmente nelle maschere PASSWEB, scheda e lettera. Nessun flusso telematico generato: PASSWEB resta compilato a mano.

### 6. costo-dipendente

Scopo: costo annuo a carico dell'ente del trattamento fondamentale (retribuzione, oneri riflessi, IRAP), CCNL FL 2022-24, Tabella B post conglobamento dal 01/01/2026 (README, SPEC).

| Regola / conoscenza | Dove | Fonte dichiarata | Validità | Certezza |
|---|---|---|---|---|
| CPDEL c/ente 23,80% sul fondamentale comparto incluso | `index.html:701-707`; SPEC §1.2 | "aliquota c/ente"; riscontro 108/113 rapporti reali | 2026 | prassi-interpretazione (nessuna norma citata; coerente con 32,65 - 8,85) |
| TFS/TFR c/ente 3,60% su (fondamentale - comparto) x 80% | come sopra | art. 11 L. 152/1968 per l'80%; "ex INADEL quota c/ente" | 2026 | norma certa per l'80%; prassi per l'aliquota (81/113 esatti) |
| DS INPS 1,61% solo su TD | come sopra | "Disoccupazione"; riscontro 2/2 | 2026 | prassi-interpretazione |
| IRAP 8,50% metodo retributivo | come sopra | D.Lgs. 446/1997 | 2026 | norma certa per il metodo; prassi per l'aliquota |
| IVC 1% del tabellare base | come sopra | "IVC 2026" | 2026 | prassi-interpretazione (coerente con Pensione-2.0 dal 07/2025) |
| Comparto escluso da base TFS e da 13a; corrisposto su 12 mensilità; posizione/risultato EQ solo CPDEL e IRAP; tipologia part-time irrilevante sul costo annuo | SPEC §2.2 | nessuna puntuale | 2026 | prassi-interpretazione |
| Tabellari dal 01/01/2026 (uguali a Pensione-2.0); comparto residuo ex B1 = 27,52 + 5,38 e ex A1 = 22,68 + 5,38; differenziali retro-calcolati da dati reali, mancano B2-B7, C3-C6, D2, D4, D5, D7 | `index.html:679-694`; SPEC §3 | file Excel interni | 2026 | da verificare (vedi Incoerenze sul 5,38) |

Nessun output obbligatorio; utile a PIAO e bilancio di previsione (arrotondamento all'euro per eccesso sul totale per atti formali, SPEC §6.1).

### 7. indennita-amministratori

Scopo: indennità di funzione di sindaco, vicesindaco, assessori, presidente del consiglio; tetto gettone; fine mandato.

| Regola / conoscenza | Dove | Fonte dichiarata | Validità | Certezza |
|---|---|---|---|---|
| Base 13.800 euro mensili (TEC presidente di regione) | `index.html:293` | art. 1 c. 583-587 L. 234/2021 | dal 2024 (a regime; transitorie 45% 2022, 68% 2023 superate) | norma certa |
| Percentuale sindaco: metropolitano 100%; capoluogo regione 80%; capoluogo provincia > 100.000 ab. 80%, altrimenti 70%; > 50.000 45%; 30.001-50.000 35%; 10.001-30.000 30%; 5.001-10.000 29%; 3.001-5.000 22%; fino a 3.000 16% | `index.html:321-334` | art. 1 c. 583 L. 234/2021 | dal 2024 | norma certa |
| Vicesindaco, assessori, presidente del consiglio in % dell'indennità del sindaco per fasce demografiche | `index.html:335-338` | DM 119/2000 artt. 4 e 5 | dal 2000 | norma certa |
| Maggiorazioni +5% / +3% / +2% cumulabili | `index.html:222-230`, `348-350` | art. 2 DM 119/2000; "applicabilità dopo il c. 583 controversa" | — | da verificare (dichiarato) |
| Dimezzamento per lavoratore dipendente non in aspettativa; non cumulabilità; tetto gettone consigliere = 1/4 dell'indennità del sindaco | `index.html:202`, `273`, `398` | art. 82 c. 1 e c. 2 TUEL | corrente | norma certa |
| Indennità di fine mandato = una mensilità per 12 mesi di mandato | `index.html:387` | art. 10 DM 119/2000 | corrente | norma certa |

Il README promette "oneri a carico dell'ente" ma il codice non li calcola (nota di chi scrive). Nulla su regime fiscale (redditi assimilati, punto 4 CU: lo dice solo `guida-cu.js` dell'estrattore) né previdenziale degli amministratori.

### 8. cedolino-parlante

Scopo: lettura e spiegazione dei cedolini PDF (Halley, JOB) con LLM. Codifica poca regola propria, ma contiene un **audit del motore di Public-Payroll** con stato di certezza per parametro (`CEDOLINO_PARLANTE_ROADMAP.md:555-615`) e osservazioni sui cedolini reali.

| Regola / conoscenza | Dove | Fonte dichiarata | Certezza |
|---|---|---|---|
| Contributo TFS/TFR dipendente 2,50% sull'80% della retribuzione, esposto come "Ritenute i.n.a.d.e.l." (codice 8117) o "Riduz. 2,50% retribuzione" (codice 1140), mai entrambi | `docs/02-DOMINIO.md:106`, `194`, `222` | indicazione dell'owner (Q-D04); "riferimento normativo puntuale: da indicare" | prassi-interpretazione |
| "Alq:" del riquadro fiscale = imposta lorda / imponibile del mese, non aliquota marginale | `docs/02-DOMINIO.md:105` | osservato | prassi-interpretazione |
| Imponibile e aliquota previdenziale leggibili dal PDF sulle righe di ritenuta | `docs/02-DOMINIO.md:103` | osservato | prassi-interpretazione |
| Audit Public-Payroll: IRPEF 2026 33% sul secondo scaglione (L. 199/2025 art. 1 c. 3) assente; detrazione coniuge "da riscrivere"; coefficiente figli senza +15.000 per figlio successivo; decurtazione malattia "errore certo"; base CPDEL senza accessorio "da riscrivere"; tassazione agevolata accessorio PA (L. 199/2025) da controllare | `CEDOLINO_PARLANTE_ROADMAP.md:557-610` | articoli citati per riga | come marcato nel documento stesso |

### 9. normative-monitor

Scopo: monitoraggio giornaliero di fonti normative (INPS circolari/messaggi/news RSS, Gazzetta Ufficiale SG e S4, Agenzia Entrate, ARAN orientamenti via API WordPress, RGS) con classificazione LLM dell'impatto per area (retributivo, previdenziale, fiscale, presenze-assenze, giuridico) e decorrenza. Conoscenza riusabile: il **registro delle fonti** con URL e note di funzionamento (`src/config.py:106-280`) e la **tassonomia d'impatto** (`CONTEXT.md`). Nessuna regola di calcolo. Certezza: prassi-interpretazione (URL verificati dal tool, non in questa sessione).

### 10. Public-Payroll

Scopo: simulatore di busta paga per dipendente EELL (app generata con AI Studio).

| Regola / conoscenza | Dove | Fonte dichiarata | Certezza |
|---|---|---|---|
| Tabellari annui al 01/01/2024 per posizione (F1-F7, I1-I5, OE1-OE7, O1-O5) con comparto mensile 36,33 / 32,06 / 27,52 / 22,68 e IVC 0 | `constants.ts:20-77` | Tabella B CCNL 23/02/2026 | da verificare (comparto 2026 accostato a tabellari 2024, vedi Incoerenze) |
| CPDEL dipendente 8,85%, Fondo Credito 0,35%, INADEL 0 "placeholder" | `constants.ts:81-86` | "aggiornate al 2025" | da verificare (il TFS dipendente 2,50% sull'80% manca) |
| IRPEF 2025 23/35/43; detrazione lavoro dipendente; cuneo 2025 (7,1% / 5,3% / 4,8% fino a 20.000; 1.000 euro 20.000-32.000 decrescente a 40.000); trattamento integrativo 1.200 euro | `constants.ts:92-128`; `payrollLogic.ts:36-140` | L. 207/2024; D.Lgs. 216/2023; art. 13 TUIR; DL 3/2020 | da verificare (vedi audit in cedolino-parlante) |
| Addizionali regionali come aliquota unica per regione; comunale 0,80% indicativa | `constants.ts:131-158` | MEF | da verificare (molte regioni hanno scaglioni) |
| Decurtazione malattia primi 10 giorni su tabellare + IVC + comparto, giornaliera = mensile / 22 o 26 | `payrollLogic.ts:177-185`; `constants.ts:164-165` | "Art. 71 D.Lgs. 150/2009" | da verificare (riferimento citato dubbio; audit di cedolino-parlante: "errore certo" sulla base) |
| Base CPDEL = tabellare + IVC + comparto, accessorio escluso | `payrollLogic.ts:200-209` | "art. 2 D.Lgs. 181/1997 e circolari INPS GDP" | da verificare (in conflitto con prassi osservata, vedi Incoerenze) |

### 11. payroll-italia-pro

Scopo: calcolatore netto per **CCNL privati** (commercio, metalmeccanica, turismo, multiservizi, sanità privata) con analisi cedolino AI e abbonamenti. Fuori dal dominio Enti Locali; conoscenza fiscale riusabile con cautela.

| Regola / conoscenza | Dove | Fonte dichiarata | Certezza |
|---|---|---|---|
| IRPEF 2026: 23% fino a 28.000, 33% fino a 50.000, 43% oltre | `services/payrollCalculator.ts:9-24` | art. 11 TUIR, L. 199/2025 | norma certa (coerente con cedolino-parlante, che cita art. 1 c. 3) |
| Detrazione lavoro dipendente (stesse formule di Public-Payroll, discontinuità voluta a 15.000) | `services/payrollCalculator.ts:26-37` | art. 13 TUIR; Risoluzione AdE 1/2007 | prassi-interpretazione |
| Detrazioni figli >= 21 anni 950 euro con soglia 95.000 + 15.000 per figlio oltre il primo; coniuge 800 / 690 + 110 x (40.000 - r)/25.000 / 690 x (80.000 - r)/40.000 | `services/payrollCalculator.ts:39-61` | art. 12 TUIR, L. 234/2021 | da verificare (formula coniuge diversa da Public-Payroll e dall'audit di cedolino-parlante) |
| Cuneo 2026 strutturale su RAL; trattamento integrativo 1.200 fino a 15.000, decrescente fino a 28.000; assorbito dal bonus cuneo | `services/payrollCalculator.ts:195-218` | L. 207/2024, L. 199/2025, D.Lgs. 216/2024 | da verificare |
| Prima fascia pensionabile 2026 56.224 euro (+1% L. 438/1992), massimale 122.295 euro, deducibilità previdenza complementare 5.164,57 | `constants.ts:14-24` | circ. INPS 6/2026; L. 335/1995; art. 10 TUIR, D.Lgs. 252/2005 | norma certa per l'impianto; valori 2026 prassi-interpretazione (calcolati "+1,4% ISTAT") |
| Aliquote INPS privati (9,19%, apprendisti 5,84%), TFR = RAL / 13,5, Fondo garanzia 0,5% | `services/payrollCalculator.ts:155-270` | circ. INPS 22/2007; art. 2120 c.c.; L. 297/1982 | non pertinente al pubblico impiego |

## Catalogo trasversale per dominio

### Previdenza (gestione dipendenti pubblici ex INPDAP)

| Regola | Tool | Certezza |
|---|---|---|
| CPDEL totale 32,65% dal 2007 (storico dal 1954) | analizzatore `src/aliquote.ts:7-11` | prassi-interpretazione |
| CPDEL ente 23,80%, dipendente 8,85% | costo-dipendente; Public-Payroll; cedolino-parlante (audit); F24EP-editor (caso 23,80 vs 32,65) | prassi-interpretazione (coerenti fra loro, nessuna norma citata) |
| Contributo aggiuntivo 1% (Contrib1PerCento, TC6) | uniemens-builder; F24EP-editor (dentro P201, provvisorio); analizzatore (00064I) | soglia della prima fascia pensionabile per il pubblico: **assente in tutti i tool PA** (solo payroll-italia-pro, per i privati) |
| TFS: imponibile 80% (art. 11 L. 152/1968; INADEL dal 01/01/1993); totale 6,10% dal 1993 (4,88% prima); ente 3,60%, dipendente 2,50% sull'80% | analizzatore; costo-dipendente; cedolino-parlante; Pensione-2.0 | 80%: norma certa; aliquote: prassi-interpretazione (coerenti fra loro: 3,60 + 2,50 = 6,10) |
| TFR: retribuzione valutabile = imponibile TFR x 1,25 + ulteriori elementi; tabellare TFR dato reale; ulteriori elementi al 6,91% | uniemens-builder; analizzatore; Pensione-2.0 | norma certa (circ. 105/2012, msg. 2440/2019, errori INPS) |
| Regime TFS/TFR dalla storia dei contratti (30/05/2000, 31/12/2000) | analizzatore | norma certa (DPCM 20/12/1999 e 02/03/2001) |
| Fondo Credito 0,35%, dal 12/1996, imponibile = CPDEL | analizzatore; Pensione-2.0 (msg. 1974/2018); uniemens-builder (controllo CPDEL = Credito); Public-Payroll | norma certa per data e imponibile; prassi per l'aliquota |
| Codici errore INPS e loro regole (00032I, 00064I, 00095I, 00116I, 00120I, 00124I, 00171I, 00172I, 00273I, 00356I, 00383I, 00566I, 00597I, 00688I, 00720I, 00879I, 00902I, 00982I) | uniemens-builder; analizzatore | norma certa nel senso di comportamento osservato del Software di controllo |
| Messaggio INPS 3267/2026 (V1C7 CMU 5, IdentAtto 6-22) | uniemens-builder (e copia nell'analizzatore) | norma certa |
| Ante 2005 / post 2004 e PASSWEB inibito dal 01/10/2025 | analizzatore | norma certa (L. 213/2023; circ. 118/2025) |
| Ultimo miglio, DMA previste, soglia 15 giorni TFR, 26esimi, 365esimi | Pensione-2.0 | norma certa con parti di prassi dichiarate |
| Mappatura gestioni -> causali F24 EP (P201, P607, P608, P632, P909, P206, DM10) | F24EP-editor; estrattore | prassi-interpretazione, parte provvisoria |

### Fisco (sostituto d'imposta)

| Regola | Tool | Certezza |
|---|---|---|
| Tracciato F24 EP, tipi riga, scadenze di trasmissione | F24EP-editor | norma certa |
| Scadenza versamento il 16 del mese successivo, primo feriale; proroga di Ferragosto | F24EP-editor (spenta); estrattore (sempre accesa) | da verificare |
| Ravvedimento (tassi legali, scaglioni pre/post D.Lgs. 87/2024, termine 770 al 31/10, codici sanzione) | F24EP-editor (copia di F24EP-Ravvedimento-Operoso-2.0) | norma certa per l'impianto, prassi per tassi e mappa sanzioni |
| Punti CU 2026, tracciato CURnn, eredi (DF001916/7) | estrattore | norma certa |
| Quadrature 770 (ST, SV, SX1, SX2, SX49, SX50) contro CU e F24 EP | estrattore | prassi-interpretazione |
| Codici tributo erariali/regionali/comunali del ciclo stipendiale (100E, 102E, 104E, 110E, 155E, 160E, 161E, 170E, 175E, 381E, 384E, 385E, 118E, 124E-129E, 133E, 134E, 143E, 147E, 148E, 150E, 153E, 154E) | F24EP-editor (`data/codici-tributo.json`); estrattore | norma certa (tabella ufficiale); etichetta errata del 143E nell'estrattore |
| IRPEF 2025 e 2026, detrazioni, cuneo, trattamento integrativo, addizionali | Public-Payroll (2025); payroll-italia-pro (2026); cedolino-parlante (audit) | da verificare |
| Redditi assimilati degli amministratori nel punto 4 CU (art. 13 c. 5 TUIR) | estrattore `guida-cu.js` | norma certa (istruzioni CU citate) |
| IRAP 8,50% metodo retributivo | costo-dipendente | norma certa per il metodo, prassi per l'aliquota |

### CCNL Funzioni Locali

| Regola | Tool | Certezza |
|---|---|---|
| Tabellari 2019-21, 2022-24 (2024 e 2026), Ipotesi 2025-27, IVC, elemento perequativo, differenziali art. 14 | Pensione-2.0 (completo); costo-dipendente e Public-Payroll (sottoinsiemi) | norma certa in Pensione-2.0 |
| Indennità di comparto e conglobamento parziale dal 2026 (quota bilancio/fondo) | Pensione-2.0 | norma certa |
| Giornaliera = mensile/26 (art. 74 c. 4); 13a (art. 75); miglioramento per cessati (art. 57 c. 2 CCNL 2022-24) | Pensione-2.0 | norma certa |
| Utilità voci per pensione/13a/TFS/TFR | Pensione-2.0; costo-dipendente (parziale) | prassi-interpretazione |
| Fondo risorse decentrate, istituti accessori, progressioni | nessun tool (solo "Estensioni previste" di costo-dipendente) | lacuna |
| Indennità amministratori (L. 234/2021, DM 119/2000, art. 82 TUEL) | indennita-amministratori | norma certa, maggiorazioni da verificare |

### Contabilità (armonizzata e di versamento)

| Regola | Tool | Certezza |
|---|---|---|
| Impegni, liquidazioni, mandati, reversali | nessun tool | lacuna |
| Raccordo compensazioni F24 EP <-> quadro SX | estrattore | prassi-interpretazione |
| Conto di tesoreria e CAB nel record M F24 EP (04306) | F24EP-editor | prassi-interpretazione (osservato) |
| Distinzione quota comparto a carico del bilancio / del fondo | Pensione-2.0 | norma certa |
| Costo del personale per PIAO e bilancio (arrotondamento) | costo-dipendente | prassi-interpretazione |

## Contratti di input/output degli output obbligatori

| Output obbligatorio | Tool | Input | Output | Validazione dichiarata |
|---|---|---|---|---|
| UniEmens ListaPosPA (E0, V1 causali 1/5/6/7, V1C7 CMU 5) | uniemens-builder; analizzatore (copia del builder + generatore) | XML UniEmens; JSON INPS Extractor; file PASSWEB (Elenco Quadri, BDC, SCAD); questionario | XML DenunceMensili/PosPA | Software UniEmens Individuale INPS; codici errore riprodotti |
| F24 EP (telematico) | F24EP-editor | XML UniEmens; anagrafica ente; F24 EP precedente | `.txt` F24 EP Allegato 2 2016; PDF sul modello ufficiale | round-trip su 8 file AdE; validatore Python indipendente; programma di controllo AdE |
| F24 EP ravveduto | F24EP-editor | `.txt` F24 EP non versato, data ravvedimento | `.txt` ravveduto con righi sanzione | test; mappa sanzioni da rivedere |
| CU | nessuno genera; estrattore/verifica-770 legge il telematico CURnn | — | — | — |
| 770 | nessuno genera; estrattore/verifica-770 legge il telematico | — | — | — |
| PASSWEB (ultimo miglio, DMA previste) | Pensione-2.0 | dati pratica, PDF Halley | righe da digitare in PASSWEB, scheda, lettera | test di regressione sulle "fotografie" del vecchio sito |
| Conto Annuale, 730-4, conguagli, PIAO | nessuno | — | — | lacuna |

## Duplicazioni

- **uniemens-builder -> analizzatore-posizioni**: copia integrale di `UniEmensBuilder.jsx` e delle funzioni pure (`builder.js`, righe 2-838) al commit `33e22c5`, con regola di riporto manuale (`src/vendor/ORIGINE.md`). Verificato: la copia differisce solo per le righe marcate ADATTAMENTO. Anche il blocco del messaggio 3267 è duplicato.
- **inps-extractor-e0-v1 -> analizzatore-posizioni**: `extractor/inps.ts`, `extractor/uniemens.ts` (repo non incluso nei candidati del ticket, citato in ORIGINE.md e nel README del builder).
- **F24EP-Ravvedimento-Operoso-2.0 -> F24EP-editor**: tassi legali e calcolo sanzioni portati "riga per riga"; "un cambio di tasso va fatto in entrambi i repo" (README). Repo non incluso nei candidati.
- **estrattore-f24ep-quietanze -> verifica-770**: build impacchettato; nessuna regola propria in verifica-770.
- **Tabellari CCNL 2026 e comparto residuo**: Pensione-2.0, costo-dipendente, Public-Payroll (tre copie, non derivate l'una dall'altra).
- **Detrazioni e cuneo**: Public-Payroll e payroll-italia-pro (due copie con formule diverse).
- **Mappatura gestioni -> causali P2xx/P6xx/P9xx**: F24EP-editor e estrattore (stessi codici, etichette diverse).

## Incoerenze fra tool

| # | Tema | Tool A | Tool B | Nota |
|---|---|---|---|---|
| 1 | Aliquota gestione previdenziale | analizzatore: TFS e TFR insieme 6,10% dal 1993 (`src/aliquote.ts:13-14`) | Pensione-2.0: ulteriori elementi TFR 6,91% (msg. 2440/2019, `src/tabelle/righe-passweb.ts:185`); estrattore: voce "TFR INPDAP 6,91" su P632 (`agganci.js:371`) | il calcolo "di legge" dell'analizzatore può essere errato sui quadri TFR con ulteriori elementi; da verificare |
| 2 | Proroga di Ferragosto | F24EP-editor: spenta di default (`src/ravvedimento.mjs:205-220`) | estrattore: sempre applicata (`f24ep-core.js:2507-2515`) | stessa scadenza, due risposte; da verificare la fonte per l'F24 EP |
| 3 | Codice tributo 143E | estrattore `guida-cu.js:47`: punto 101 = sostitutiva premi 730, tributi 141E/142E/143E | estrattore `f24ep-core.js:2038`: 143E = "Acconto tassazione separata", punti 101 + 301 (mentre 129E = acconto tassazione separata sui punti 111 + 311) | incoerenza interna allo stesso tool. La tabella ufficiale nel repo F24EP-editor (`data/codici-tributo-slim.json`) descrive 143E come "imposta sostitutiva IRPEF e addizionali su premi di risultato e partecipazione agli utili" a seguito di assistenza fiscale: il raccordo sui punti 101 + 301 è giusto, l'etichetta in `f24ep-core.js:2038` è sbagliata (norma certa sulla tabella, prassi sull'errore di etichetta) |
| 4 | Indennità specifica 5,38 | Pensione-2.0: utile a pensione, TFS e TFR, non a 13a (`src/tabelle/catalogo.ts:26`) | costo-dipendente: sommata al comparto residuo (ex B1 27,52 + 5,38; ex A1 22,68 + 5,38), quindi esclusa dalla base TFS (SPEC §3) | sottostima del TFS in costo-dipendente; da verificare |
| 5 | Indennità di comparto con tabellari 2024 | Public-Payroll: tabellari al 01/01/2024 con comparto 36,33/32,06/27,52/22,68 "invariata" (`constants.ts:20-77`) | Pensione-2.0: 51,90/45,80/39,31/32,40 fino al 2025, 36,33... dal 2026 con tabellari col. 2 (`src/tabelle/ccnl-2022-24.ts:220-250`) | Public-Payroll mescola due decorrenze |
| 6 | Accessorio nell'imponibile CPDEL | Public-Payroll: escluso (`payrollLogic.ts:200-209`) | cedolino-parlante: "nella prassi l'accessorio risulta assoggettato" (`CEDOLINO_PARLANTE_ROADMAP.md`); costo-dipendente: accessorio futuro "imponibile CPDEL/IRAP" (SPEC §6.2) | da verificare su cedolini reali |
| 7 | Detrazione coniuge | Public-Payroll: 800 fino a 15.000, poi formule fino a 29.000/35.000/40.000 (`payrollLogic.ts:66-72`) | payroll-italia-pro: 690 + 110 x (40.000 - r)/25.000 fino a 40.000, 690 x (80.000 - r)/40.000 fino a 80.000 (`services/payrollCalculator.ts:54-61`); cedolino-parlante indica una terza formula come corretta | nessuna delle due coincide con l'audit; da verificare sul testo dell'art. 12 TUIR |
| 8 | Trattamento integrativo 15.000-28.000 | Public-Payroll: 1.200 "assunto spettante" | payroll-italia-pro: decrescente lineare fino a 28.000 | cedolino-parlante: in verifica diventa "non verificabile" |
| 9 | Contributo TFS dipendente | Public-Payroll: INADEL = 0 | cedolino-parlante e costo-dipendente: 2,50% sull'80% (implicito 6,10 - 3,60) | Public-Payroll sovrastima il netto |
| 10 | Tipo servizio 49 | uniemens-builder (tabella 3267): 49 = congedo straordinario art. 42 c. 5 D.Lgs. 151/2001 | analizzatore PROGETTO.md: "49 non confermato da nessuna fonte"; Pensione-2.0: "49 (congedo L. 104)" | il messaggio 3267, già codificato nel builder, sembra chiudere il dubbio dell'analizzatore; da verificare |
| 11 | Imponibile TFS ante 2005 | analizzatore: prassi 67% del CPDEL (80% fino al 1992) | aliquote.ts dello stesso analizzatore e costo-dipendente: imponibile TFS all'80% dal 1993 | grandezze diverse (quota del CPDEL contro quota della retribuzione utile), da non confondere nel modello |
| 12 | Divisore giornaliero | Pensione-2.0: 26 (art. 74 c. 4 CCNL 2019-21) | Public-Payroll: 22 o 26 secondo la settimana | da verificare per la decurtazione malattia |

## Lacune (conoscenza assente in tutti i tool)

- Fondo risorse decentrate, contratto integrativo, capienza e collegamento agli istituti accessori.
- Contabilità armonizzata: impegni, liquidazioni, mandati, reversali, capitoli, missioni/programmi.
- Regimi particolari: co.co.co., LSU/LPU, segretario comunale, dirigenza; amministratori solo sul lato importo (manca fiscale/previdenziale, salvo il punto 4 CU).
- Soglia del contributo aggiuntivo 1% per il pubblico impiego; massimale per i nuovi iscritti nel pubblico.
- Conto Annuale, 730-4 (solo lato verifica nel 770/CU), conguaglio fiscale di fine anno, generazione di CU e 770.
- Tassazione agevolata dell'accessorio e degli incrementi contrattuali nel pubblico impiego (L. 199/2025), segnalata come "da controllare" in cedolino-parlante.

## Domande aperte

1. Quale aliquota TFR usare nel modello per imponibile base e ulteriori elementi (6,10% vs 6,91%), e con quale fonte primaria (msg. INPS 2440/2019, circ. 105/2012)?
2. La proroga di Ferragosto vale per l'F24 EP? Fonte primaria da leggere.
3. Risolta in questa ricerca: 143E è la sostitutiva sui premi di risultato da assistenza fiscale (tabella codici tributo in F24EP-editor); resta da correggere l'etichetta nell'estrattore, fuori dal perimetro di questo ticket.
4. L'indennità specifica 5,38 è utile al TFS? Chi ha ragione fra Pensione-2.0 e costo-dipendente?
5. L'accessorio del fondo è imponibile CPDEL? (Verifica su cedolini reali con accessorio, come propone cedolino-parlante.)
6. Le causali P201 (con l'1%), P608 e P632 della mappatura UniEmens -> F24 EP sono confermate da un F24 EP reale che le contenga?
7. Quale motore fiscale (se uno) è riusabile per il calcolo IRPEF, visto l'audit negativo su Public-Payroll e la natura privatistica di payroll-italia-pro?
8. I repo `inps-extractor-e0-v1` e `F24EP-Ravvedimento-Operoso-2.0`, fuori dai candidati del ticket, contengono conoscenza (tracciato PASSWEB, sgravi, tassi) da estrarre?

## Fonti

Tutte le fonti sono codice e documentazione dei repository `Annaluca17/*` ai commit indicati nella sezione Metodo. I riferimenti normativi citati in questo documento sono quelli presenti nel codice; non sono stati riletti sul testo ufficiale in questa sessione.
