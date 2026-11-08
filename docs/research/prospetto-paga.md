# Prospetto paga (cedolino) di un ente locale: contenuto per legge e consegna

Data: 2026-11-08 · Serve a: la vista «cedolino» del modello (CONTEXT.md: Vista), l'ADR sugli output (0022) e la decisione su amministratori e co.co.co. (ADR 0016, `regimi-titolo-compenso.md`)

## Domanda

Che cosa deve contenere per legge il prospetto paga di un ente locale e come può essere consegnato, così da realizzarlo come **vista** del modello (legge fatti ed esiti già calcolati, non calcola). Quattro temi: contenuto obbligatorio (L. 4/1953, D.L. 112/2008 art. 39, D.M. 9 luglio 2008) e loro applicazione agli enti pubblici; consegna elettronica; titoli diversi dal dipendente (amministratori, co.co.co.); elementi tipici.

## Legenda e metodo

- **norma certa**: testo di legge vigente, con articolo, letto su Normattiva in questa sessione.
- **prassi**: circolari, interpelli, risposte a quesito, guide ufficiali, uso dei gestionali.
- **da verificare**: non riscontrato su fonte primaria; è scritto che cosa è stato cercato.

Come sono state lette le fonti. Gli articoli di Normattiva (L. 4/1953 artt. 1-5, D.L. 112/2008 art. 39, D.Lgs. 165/2001 art. 2, L. 335/1995 art. 2, D.Lgs. 230/2021 art. 10) sono stati letti tramite uno strumento di fetch che **restituisce sintesi e frammenti**, non il testo parola per parola: dove una frase è tra virgolette è un frammento breve, il resto è riassunto. Le parentesi doppie di Normattiva ((...)) segnalano testo modificato; l'atto modificatore non è sempre leggibile. Il PDF dell'**interpello del 30/09/2026** e la raccolta di quesiti **DPL Macerata 2009** sono stati letti per intero con `pdftotext`. La **circolare Min. Lavoro 20/2008** (21/08/2008) è un PDF scansionato non leggibile in questa sessione: nulla qui poggia sul suo testo. Il vault `vault-pa` non è stato consultato.

## Sintesi

1. **L. 4/1953: per i Comuni e le Province l'art. 1 non si applica.** L'art. 4 dice che «la norma contenuta nel precedente art. 1» non si applica a Amministrazioni dello Stato e aziende autonome, Regioni, Province e Comuni. L'art. 1 è quello che fissa il contenuto minimo del prospetto. **norma certa** (testo letto in sintesi).
2. **Eppure la prassi ministeriale dice il contrario sul prospetto.** Secondo una FAQ del Ministero del lavoro (sezione LUL, risposta n. 12, sezione A), riportata da un ufficio territoriale del Ministero, gli enti pubblici sono esclusi dal LUL ma «resta fermo» l'obbligo di documentare la prestazione, «ivi compresa la predisposizione di un prospetto di paga». **prassi** (la FAQ non è stata letta direttamente). Le due fonti non sono conciliate da nessun testo letto: **da verificare**.
3. **Il LUL non si applica alle PA.** L'art. 39 c. 1 D.L. 112/2008 obbliga il «datore di lavoro privato». **norma certa**. Conferme ministeriali (quesiti 11 e 44/2009 DPL Macerata, interpello 3/2009). **prassi**.
4. **Contenuto minimo dell'art. 1** (se si applicasse, e come riferimento): nome, cognome, qualifica, periodo di riferimento, assegni familiari e altre voci della retribuzione, singole trattenute, contratto collettivo applicato (codice alfanumerico unico), firma, sigla o timbro del datore. Esclusi i dirigenti. **norma certa** (sintesi). Non sono nell'elenco: dati del datore, netto, ferie, TFR/TFS.
5. **Consegna al momento del pagamento** (art. 3). **norma certa**. Consegna elettronica ammessa dalla prassi: posta elettronica (interpello 1/2008), area riservata e posta ordinaria (interpello 13/2012), principi riconfermati dall'interpello del 30/09/2026. **prassi**, tutti riferiti al datore **privato**. Per le PA lo stesso interpello 1/2008 osserva che la pratica è «già ampiamente utilizzata» (da una riproduzione ANCE). **prassi**. NoiPA consegna il cedolino solo in formato elettronico in area riservata. **prassi**.
6. **Amministratori e co.co.co.**: non sono «lavoratori dipendenti» dell'art. 1, quindi nessun prospetto di legge. Per i co.co.co. l'iscrizione nel LUL c'è solo per il committente privato (art. 39 c. 1); per un ente no. Restano ritenuta, contributo e CU. Una «nota di pagamento» non ha fonte che la imponga. **norma certa** (campo di applicazione) + **da verificare** (prassi della nota).
7. **Ferie residue e TFR/TFS** non sono richiesti da nessuna fonte letta per il prospetto. Il cedolino NoiPA mostra la tipologia di liquidazione (TFS/TFR), non gli importi. **prassi**.

---

## Tema 1. Contenuto obbligatorio e applicazione agli enti pubblici

### L. 5 gennaio 1953 n. 4

Letta su Normattiva il 08/11/2026 (art. 1 «in vigore dal 28-6-2026»; art. 5 «in vigore dal 24-9-2015»).

| Articolo | Contenuto | Marcatura |
|---|---|---|
| Art. 1 | Il datore di lavoro consegna ai lavoratori dipendenti, «con esclusione dei dirigenti», un prospetto di paga con: nome, cognome e qualifica del lavoratore; periodo di riferimento; assegni familiari e ogni altra voce della retribuzione; singole trattenute; il contratto collettivo nazionale applicato, con il codice alfanumerico unico dell'art. 16-quater D.L. 76/2020 (testo tra doppie parentesi, cioè modificato: atto modificatore non letto); firma, sigla o timbro del datore o di chi ne fa le veci | **norma certa**. Chi ha introdotto il codice del contratto: **da verificare** (la data 28/06/2026 coincide con l'ultima legge di conversione citata nell'interpello 1/2026, L. 112/2026, ma non è provato) |
| Art. 2 | Le annotazioni del prospetto devono corrispondere esattamente alle registrazioni dei libri di paga (o registri equipollenti) per lo stesso periodo | **norma certa** |
| Art. 3 | Il prospetto è consegnato «nel momento stesso» in cui è consegnata la retribuzione | **norma certa** |
| Art. 4 | L'art. 1 non si applica: a) Amministrazioni dello Stato e relative aziende autonome; b) Regioni, Province e Comuni; c) aziende agricole fino a 3.000 giornate; d) datori privati per il personale esclusivamente di servizi familiari | **norma certa** (nessuna modifica segnalata sulla pagina). Conferma indipendente: scheda di lettura Camera dei deputati, dossier 11/03/2015 («Regioni ed enti locali») |
| Art. 5 | Sanzione amministrativa per mancata o ritardata consegna, o per omissioni e inesattezze: 150-900 euro; da 600 a 3.600 se più di 5 lavoratori o più di 6 mesi; da 1.200 a 7.200 se più di 10 lavoratori o più di 12 mesi. Se il datore consegna copia delle scritturazioni del LUL, queste sanzioni non si applicano e vale l'art. 39 c. 7 D.L. 112/2008 | **norma certa** (sintesi). Prima del 2015 la sanzione era di 25,82-154,94 euro (dossier Camera). Atto del 2015: **da verificare** (probabile D.Lgs. 151/2015, non letto) |

Tre note.

- **Elenco chiuso.** L'art. 1 non nomina il datore (denominazione, codice fiscale, sede), il netto, le ore o i giorni, le ferie, il TFR. Che compaiano sul cedolino è prassi dei gestionali, non legge. **norma certa** per l'assenza nell'elenco letto (sintesi: da riscontrare sul testo integrale).
- **Dirigenti.** Escluse dall'art. 1 («con esclusione dei dirigenti»). La L. 4/1953 non è un limite per la vista: il modello li tratta come personale correlato. **norma certa**
- **Art. 4 esclude solo l'art. 1.** Gli artt. 2, 3 e 5 non hanno un'esclusione espressa. Se sia conseguente è un'interpretazione; nessuna fonte letta la tratta. **da verificare**.

### Applicazione agli enti pubblici: due strati

**Strato 1: il testo.** L'art. 4 esclude Comuni e Province dal contenuto minimo dell'art. 1. Non nomina: Unioni di comuni, Città metropolitane, comunità montane, consorzi, aziende speciali, IPAB. **norma certa** per l'elenco; per gli altri enti **da verificare**. L'art. 2 c. 2 D.Lgs. 165/2001 porta i rapporti di lavoro pubblici sotto il codice civile e «le leggi sui rapporti di lavoro subordinato nell'impresa», ma salvo diversa disposizione, e l'art. 4 L. 4/1953 è una disposizione specifica: non basta a dire che l'art. 1 torni applicabile ai Comuni. **norma certa** per il testo dell'art. 2 c. 2 (sintesi); la conclusione è una **interpretazione**.

**Strato 2: la prassi ministeriale.** Una FAQ ministeriale (risposta n. 12 sez. A, sito lavoro.gov.it) è riportata dal quesito n. 44 del 1° giugno 2009 della DPL di Macerata: gli enti pubblici di qualsiasi natura sono esclusi dal LUL; «resta fermo anche per tali enti l'obbligo di documentare lo svolgimento della prestazione lavorativa a tutti i fini di legge, ivi compresa la predisposizione di un prospetto di paga per i lavoratori dipendenti». **prassi** (testo della FAQ non letto sul sito; il quesito DPL Macerata è letto per intero). Nello stesso senso l'interpello n. 3 del 06/02/2009 (FICEI, enti pubblici economici: esclusi dal LUL, ma restano gli altri obblighi, compreso il prospetto della L. 4/1953), letto in sintesi su dottrinalavoro.it. **prassi**

**Conclusione di lavoro.** Per un Comune l'obbligo giuridico puntuale di contenuto è incerto (art. 4 lo esclude; la FAQ lo presuppone). Il comportamento reale e il riferimento prudente sono gli stessi: produrre un prospetto che contenga almeno l'elenco dell'art. 1. Il modello non ha bisogno di decidere la questione per costruire la vista; deve solo non ridurre il contenuto sotto l'art. 1. **da verificare** la qualificazione giuridica.

### D.L. 25 giugno 2008 n. 112, art. 39 (Libro Unico del Lavoro) e D.M. 9 luglio 2008

| Punto | Esito | Marcatura |
|---|---|---|
| Soggetti | Art. 39 c. 1: «Il datore di lavoro privato», salvo il domestico. Il LUL riguarda lavoratori subordinati, collaboratori coordinati e continuativi, associati in partecipazione con apporto di lavoro | **norma certa** (testo dell'articolo «in vigore dal 24-9-2015») |
| Contenuto del LUL | c. 2: pagamenti, trattenute, assegni familiari e prestazioni, voci di premi e straordinari, calendario delle presenze | **norma certa** (sintesi) |
| Termine di compilazione | c. 3: registrazioni entro il mese successivo | **norma certa** (sintesi) |
| Rapporto col prospetto | **c. 5**: con la consegna al lavoratore di copia delle scritturazioni del LUL il datore adempie agli obblighi della L. 4/1953. Art. 5 L. 4/1953 lo ripete per le sanzioni | **norma certa** (esordio del c. 5 e art. 5 letti) |
| Firma sulla copia del LUL | Una fonte professionale dice che chi consegna copia del LUL non ha obbligo di firma, sigla o timbro | **prassi** (fonte secondaria, nessuna circolare riscontrata): **da verificare** |
| Sanzioni LUL | c. 6-7: omessa tenuta 500-2.500; omessa esibizione 200-2.000; omesse o inesatte registrazioni a scaglioni; omessa conservazione 100-600 | **norma certa** (sintesi) |
| Tenuta e conservazione | D.M. 9 luglio 2008: tre sistemi di tenuta (fogli mobili, laser, supporti magnetici), conservazione **cinque anni** dall'ultima registrazione (art. 6); co.co.co. e associati contano ai fini delle soglie solo se iscritti (art. 5) | **da verificare**: letto su una riproduzione di terzi (Certifico), non su Normattiva |
| Termine del regime transitorio | Fino al periodo di paga di dicembre 2008 | **da verificare** (stessa fonte) |

**Il LUL si applica alle PA?** No.

- Testo: obbligo per il «datore di lavoro privato». **norma certa**
- Ministero (via DPL Macerata): quesito n. 11 del 12/02/2009: il legislatore «ha escluso dalla disciplina» le amministrazioni pubbliche, «esonerate dall'istituzione e tenuta» del libro; quesito n. 44 del 01/06/2009: un ente forestale regionale, ente pubblico non economico, è esonerato; la FAQ ministeriale n. 12 sez. A estende l'esonero agli enti pubblici di qualsiasi natura. **prassi** (quesiti letti per intero; atti ministeriali citati non letti).
- Facoltà: l'interpello 3/2009 non esclude che gli enti pubblici adottino modalità di tenuta analoghe a quelle dei privati (sintesi dottrinalavoro.it). **prassi**
- Circolare Min. Lavoro 20/2008: due siti professionali (Fisco e Tasse, 2010) scrivono che le PA registrano «mediante fogli o cedolini o ruoli di paga elaborati individualmente». Il testo della circolare non è stato letto, quindi l'attribuzione alla circolare è **da verificare**. Cercato: PDF scansionato su fiscoetasse.com, nessun testo estraibile.
- Nota: la circolare 20/2008 (secondo il sito citato) esclude dal LUL anche amministratori, sindaci e componenti di collegi quando i compensi sono di natura professionale. Riguarda le imprese private, non gli amministratori locali: non va confusa. **da verificare**

**Se il LUL non vale, la L. 4/1953 vale?** Vedi sopra: per Comuni e Province l'art. 1 è escluso dal testo (art. 4), ma la prassi ministeriale presuppone un prospetto di paga per i dipendenti degli enti pubblici. Chi non è nominato dall'art. 4 (Unioni, Città metropolitane, comunità montane) rientra nel testo dell'art. 1 salvo diversa lettura. **da verificare**.

## Tema 2. Consegna elettronica, firma, conservazione

| Punto | Esito | Marcatura |
|---|---|---|
| Momento | Alla corresponsione della retribuzione (art. 3 L. 4/1953) | **norma certa** |
| Posta elettronica, interpello 1/2008 (nota 11/02/2008, istanza CNA) | La trasmissione telematica del prospetto è legittima nel rispetto della normativa su PEC (D.P.R. 68/2005), sui documenti informatici (capo IV D.Lgs. 82/2005) e sulla protezione dei dati; condizione essenziale: prova della ricezione alla scadenza del pagamento; il datore mette il lavoratore in condizione di ricevere con spese a proprio carico e un indirizzo personale con password. Il Ministero ricorda che «presso la P.A. la pratica in oggetto risulta già ampiamente utilizzata» e può essere estesa al privato | **prassi**: letto sul comunicato ANCE del 15/02/2008 (riproduzione); l'interpello del 30/09/2026 lo richiama con lo stesso contenuto (PEC, prova dell'effettiva consegna, tecnologie di ricezione e stampa) |
| Posta ordinaria e area riservata, interpello 13/2012 | La consegna può avvenire anche con posta elettronica ordinaria o con documento in area riservata accessibile con password o codice personale, purché il lavoratore possa entrare nella disponibilità del documento e **materializzarlo**, e la messa a disposizione sia **tracciabile** | **prassi**: letto come richiamo nell'interpello del 30/09/2026; testo del 2012 non letto |
| Interpello del 30/09/2026 (prot. 15911; sul sito: «interpello-2-del-30092026», istanza del Consiglio nazionale dei consulenti del lavoro) | Per i documenti del rapporto che non richiedono dichiarazione del lavoratore basta la messa a disposizione in area riservata se garantiti: a) identificazione e sicurezza dell'accesso; b) accessibilità e disponibilità (visionare, conservare, riprodurre); c) integrità; d) tracciabilità della data di messa a disposizione e, se richiesta, della presa visione. Valgono anche PEC e altri strumenti con prova di consegna. Se la piattaforma è indisponibile i termini restano: servono modalità alternative con evidenza. Il datore deve poter dimostrare l'adempimento con le **evidenze informatiche** conservate. Richiama il CAD e le Linee guida AgID sui documenti informatici (art. 71 CAD) | **prassi** (testo letto per intero). Il quesito riguarda il **datore privato**: l'interpello esclude di fondare sull'art. 65 CAD le dichiarazioni verso il datore privato, perché quell'articolo vale per le istanze alle PA |
| Firma del datore sul prospetto | L'art. 1 richiede firma, sigla o timbro; con la copia del LUL non serve (fonte secondaria). Per il cedolino elettronico non ho trovato una fonte primaria sul modo di apporla | **norma certa** (art. 1) + **da verificare** (cedolino elettronico). Cercato: interpelli sopra, NoiPA |
| Firma del lavoratore | La firma del lavoratore sulla busta paga non prova l'avvenuto pagamento. Una fonte la attribuisce a L. 205/2017; comma non verificato | **da verificare** (fonte secondaria ecnews.it) |
| NoiPA (PA) | Il cedolino è disponibile **esclusivamente in formato elettronico**, nell'area riservata (sezione «Documenti Personali»), con credenziali o CNS; non c'è copia cartacea; è PDF; la guida MEF dice che è disponibile anche per chi non ha la casella istituzionale. L'ID del cedolino ha numerazione progressiva convenzionale | **prassi** (pagine NoiPA e guida alla lettura, MEF) |
| Conservazione per l'ente | Per il LUL, cinque anni (D.M. art. 6): vale per il privato. Per la PA: CAD e Linee guida AgID richiamate dall'interpello; durata dei cedolini negli enti locali non trovata | **da verificare** (cercato: normattiva, lavoro.gov.it, AgID) |
| Privacy | Il Garante, secondo una pagina del suo sito, ha ritenuto conforme (decisione 16/07/2003) la consegna del cedolino in busta chiusa sigillata a incaricati. Nessun provvedimento del Garante specifico sulla posta elettronica del cedolino nella PA trovato | **da verificare** (testo del Garante non letto) |

Lettura per il modello. Il prospetto va **reso disponibile al pagamento** in modo **tracciabile e materializzabile**: sono requisiti di consegna, non di contenuto. Il modello può offrire la vista (PDF o dati strutturati) e registrare la **messa a disposizione** come fatto, ma non è chi consegna. **prassi** (interpretazione da ratificare).

## Tema 3. Titoli diversi dal dipendente

### Amministratori locali (indennità di funzione, gettoni)

- **Prospetto di legge?** No: l'art. 1 L. 4/1953 riguarda i «lavoratori dipendenti»; il mandato di amministratore non è rapporto di lavoro dipendente (CONTEXT: Mandato di amministratore, titolo di compenso diverso). **norma certa** (campo di applicazione dell'art. 1) e interpretazione per la conclusione. Il LUL non vale (ente pubblico) né varrebbe: non sono nominati dall'art. 39 c. 1.
- **Che cosa si consegna in pratica.** Non ho trovato una fonte che imponga o descriva una «nota di pagamento» o un cedolino per gli amministratori. **da verificare**. Cercato: L. 4/1953, D.L. 112/2008, TUEL art. 82 (letto in `regimi-titolo-compenso.md`), nessuna prassi trovata.
- **Dati minimi che comunque esistono.** Ritenuta a titolo d'acconto con rivalsa all'atto del pagamento (art. 24 c. 1 D.P.R. 600/1973, regola dell'art. 23 in quanto compatibile), reddito assimilato (art. 50 c. 1 lett. f e g TUIR; dal 01/01/2027 numerazione del TU, D.Lgs. 117/2026), detrazione dell'art. 13 c. 5, addizionali. **norma certa** secondo `regimi-titolo-compenso.md` (letto in sessione precedente, non riletto qui). Né la ricerca precedente né questa trovano una ritenuta previdenziale in busta per l'indennità: gli oneri dell'art. 86 sono a carico dell'ente. **prassi** (da quel documento).
- **Certificazione.** Il sostituito riceve la CU; il modello la produce come vista (ADR 0020). **norma certa** nella sostanza (ADR 0020), norma non riletta qui.

### Collaboratori coordinati e continuativi

- **Prospetto di legge?** Anche qui l'art. 1 parla di lavoratori dipendenti: nessun prospetto della L. 4/1953. **norma certa** (scopo) + interpretazione.
- **Iscrizione nel LUL.** Art. 39 c. 1: i co.co.co. sono compresi, ma l'obbligo è del **datore privato**. Nell'ente non c'è LUL, quindi nessuna iscrizione. **norma certa** + **prassi** (esonero delle PA). Un quesito DPL Macerata (n. 86/2009) tratta le co.co.co. delle PA, ma sul vecchio regime a progetto: superato, non è fonte per questo punto. **da verificare** se un chiarimento recente riguardi i co.co.co. delle PA. Nel privato un'interpretazione ministeriale più recente (interpello 1/2026, riders con contratto autonomo) estende il LUL anche ai lavoratori autonomi delle piattaforme: non riguarda gli enti.
- **Dati che il committente deve comunque determinare.** Compenso, ritenuta fiscale (art. 50 c. 1 lett. c-bis TUIR; art. 23-24 D.P.R. 600/1973), contributo alla Gestione separata (obbligo di iscrizione art. 2 c. 26 L. 335/1995; riparto un terzo al collaboratore, due terzi al committente, c. 30; dalla circolare INPS 8/2026 aliquota 2026 tipo 11 35,03%), addizionali, premio INAIL se dovuto (1/3 lavoratore). Versamento del committente entro il 16 del mese successivo. Tutto questo è già nel modello; per le fonti si rinvia a `regimi-titolo-compenso.md`. **norma certa** per l'art. 2 c. 26 e c. 30 L. 335/1995 (letti in sintesi); il resto **norma certa** secondo quel documento.
- **Consegna.** Nessuna fonte letta dice che il committente debba consegnare al co.co.co. un cedolino. Resta la CU. Una nota di compenso a scopo informativo è una scelta dell'ente. **da verificare**.
- **Quota a carico del collaboratore e visibilità.** Il testo letto di c. 30 non dice come si recupera la quota del collaboratore (trattenuta o altro): **da verificare**.

## Tema 4. Elementi tipici di un cedolino

Colonna «Fonte» in ordine di forza: L. 4/1953 art. 1 (legge, se applicabile), prassi ministeriale, uso dei gestionali (guida NoiPA letta per intero).

| Elemento | Obbligo o prassi | Marcatura | Nel modello (lettura, non decisione) |
|---|---|---|---|
| Nome, cognome, qualifica | Obbligo dell'art. 1 | **norma certa** | Persona, rapporto, qualifica (fatto giuridico) |
| Periodo di riferimento | Obbligo dell'art. 1 | **norma certa** | Periodo di competenza, frazioni |
| Assegni familiari e altre voci | Obbligo dell'art. 1 | **norma certa** | Importi per istituto |
| Singole trattenute | Obbligo dell'art. 1 | **norma certa** | Righe di composizione |
| Codice del contratto collettivo | Obbligo dell'art. 1 dalla modifica (D.L. 76/2020 art. 16-quater cita il codice) | **norma certa** per l'inserimento nell'art. 1; per i CCNL pubblici il codice CNEL: **da verificare** | Dichiarazione del titolo/CCNL: dato mancante se assente |
| Firma, sigla o timbro del datore | Obbligo dell'art. 1 (non per copia del LUL) | **norma certa** + **da verificare** per l'elettronico | Fuori dal calcolo; la vista porta il segnaposto o l'identificativo del documento |
| Dati dell'ente (denominazione, codice fiscale, ufficio) | Non nell'elenco dell'art. 1; il cedolino NoiPA li riporta (amministrazione, codice fiscale, ufficio responsabile e di servizio) | **prassi** | Fatti sull'ente, sede di lavoro |
| Dati del lavoratore (codice fiscale, nascita, domicilio fiscale, matricola) | Non nell'art. 1; NoiPA li riporta | **prassi** | Persona; domicilio fiscale; il codice fiscale è dato personale |
| Rata di riferimento, identificativo del cedolino | Non nell'art. 1; NoiPA: mese e anno, ID progressivo | **prassi** | Identificativo della versione della vista |
| Tipologia di contratto, livello di inquadramento, cassa, regime di fine servizio | Non nell'art. 1; NoiPA: posizione giuridico economica con TFS/TFR e cassa previdenziale | **prassi** | Regime di fine servizio (CONTEXT); inquadramento: fatto giuridico |
| Competenze fisse e accessorie | Art. 1 («ogni altra voce»); NoiPA le divide in fisse e accessorie | **norma certa** + **prassi** | Istituti per maturazione |
| Ritenute previdenziali, fiscali, altre (sindacali, terzi) | Art. 1 («singole trattenute»); NoiPA suddivide in previdenziali, fiscali, altre | **norma certa** + **prassi** | Basi e ritenuta; trattenute a terzi |
| Addizionali, conguagli | NoiPA le riporta nei conguagli fiscali e previdenziali (addizionale regionale, comunale saldo e acconto) | **prassi** | Conguaglio fiscale, regola delle addizionali |
| Detrazioni | NoiPA riporta il totale (base e carichi di famiglia) | **prassi** | Dichiarazione del sostituito |
| Assegni al nucleo familiare e assegno unico | Art. 1 cita gli assegni familiari. Dal 01/03/2022 l'ANF per i nuclei con figli e orfanili è cessato (art. 10 D.Lgs. 230/2021, letto in sintesi); l'assegno unico è erogato dall'INPS, non passa dalla busta paga; ANF per gli altri nuclei: testo non letto | **norma certa** (cessazione) + **prassi** per l'AUU e per l'ANF residuo (fonti secondarie) | La voce ANF compare solo se esiste come istituto vigente; l'AUU non entra |
| Imponibili e progressivi | NoiPA: imponibile e IRPEF anno corrente e precedente, aliquote media e massima | **prassi** | Imponibile fiscale per persona |
| Netto, lordo, quinto cedibile | NoiPA: totali lordi e netti e quinto cedibile; l'art. 1 non nomina il netto | **prassi** | Netto (CONTEXT); quinto: dato della trattenuta a terzi |
| Estremi di pagamento (IBAN, valuta) | Non nell'art. 1; NoiPA li riporta | **prassi** | Pagamento, data di pagamento |
| Giorni, ore, presenze | Art. 1: non richiesti. Nel LUL il calendario delle presenze con assenze (ferie, malattia) è obbligatorio; per le PA no | **norma certa** (art. 39 c. 2, solo privati) + **prassi** (quesito 12/2009 DPL Macerata sulle causali) | Assenze e causali come fatti; nessun obbligo di esporli |
| Ferie e permessi residui | Non sono nell'art. 1 né in nessuna fonte letta per il prospetto; la guida NoiPA letta non li cita | **prassi** (assenza nella guida NoiPA); resta **da verificare** per gestionali specifici | Fuori dalla vista, salvo scelta |
| TFR/TFS | Non nell'art. 1; NoiPA espone il **tipo** di liquidazione (TFS/TFR), non l'importo accantonato | **prassi** | Regime di fine servizio sì; accantonamento no |
| Dirigenti | Esclusi dall'art. 1 | **norma certa** | Stessa vista |

Nota: l'elenco dell'art. 1 è **breve** (qualifica, periodo, voci, trattenute, contratto, firma). Quasi tutti gli altri campi sono prassi, e il riferimento di prassi qui usato è il cedolino NoiPA, non una norma.

---

## Esito per il grilling

1. **Quale insieme di campi è obbligatorio nella vista.** Opzioni: (a) solo l'elenco dell'art. 1 L. 4/1953; (b) art. 1 più il blocco di prassi NoiPA (ente, dati del lavoratore, rata, regime di fine servizio, detrazioni, progressivi, netto, estremi di pagamento); (c) tutto ciò che il modello sa. Raccomandazione: **(b)**. Perché: l'art. 1 non vale in modo certo per Comuni e Province (art. 4), ma la prassi ministeriale presuppone un prospetto, e il cedolino della PA di riferimento contiene tutto il blocco di prassi; così la vista non scende sotto l'art. 1 e somiglia a ciò che il personale conosce.
2. **Che cosa fa la vista se manca un dato.** Opzioni: (a) fermo; (b) avviso e campo vuoto; (c) fermo solo per il contenuto dell'art. 1, avviso per il resto. Raccomandazione: **(c)**. Perché: CONTEXT dice che il dato mancante è chiesto, non stimato; qualifica, periodo, voci e trattenute sono i campi di legge e senza di essi il documento è incompleto; i campi di prassi (ufficio di servizio, matricola) non devono bloccare il cedolino.
3. **Codice del contratto collettivo.** Opzioni: (a) campo obbligatorio con fermo se manca; (b) campo di prassi senza fermo; (c) fuori finché non c'è fonte. Raccomandazione: **(b)**, con nota **da verificare**. Perché: l'art. 1 lo richiede nel testo letto, ma per i CCNL pubblici il codice unico (CNEL) non è stato verificato e per i Comuni l'art. 1 è escluso dall'art. 4.
4. **Amministratori e co.co.co.**: stessa vista? Opzioni: (a) stessa struttura del cedolino con titolo nell'intestazione; (b) vista distinta di «nota di pagamento» con campi minimi (compenso, ritenuta, contributo e addizionali, netto); (c) nessuna vista, solo CU. Raccomandazione: **(a)**. Perché: nessuna fonte impone un prospetto; il modello ha già gli importi per titolo con la composizione; una struttura unica evita un secondo documento. Resta **da verificare** la prassi dell'ente. Per gli amministratori la vista non mostra una ritenuta previdenziale (gli oneri dell'art. 86 sono a carico dell'ente).
5. **Ferie e TFR/TFS entrano nella vista?** Opzioni: (a) né l'uno né l'altro; (b) ferie residue sì (da fatti di assenza), TFR/TFS solo come tipo di liquidazione; (c) entrambi con importi. Raccomandazione: **(a)** più il tipo di liquidazione. Perché: nessuna fonte letta li richiede per il prospetto; le ferie residue richiederebbero un saldo che il modello non ha come fatto; l'importo accantonato non è un esito pagato; il tipo (TFS/TFR) è già un dato del regime di fine servizio.
6. **La consegna elettronica è affare del modello?** Opzioni: (a) fuori dal modello, adattatore; (b) il modello registra solo il fatto «messa a disposizione» con data e riferimento, la trasmissione resta fuori; (c) il modello consegna. Raccomandazione: **(b)**. Perché: i requisiti di consegna (identificazione, tracciabilità, integrità, evidenze) sono di piattaforma, ma l'interpello del 30/09/2026 chiede di poter dimostrare l'adempimento; un fatto di messa a disposizione dà la prova senza che il modello diventi un recapito. Un ente senza sistema di consegna resta senza obbligo di modello.

## Fonti

Fonti primarie lette.

- L. 5 gennaio 1953 n. 4, artt. 1-5: [Normattiva](https://www.normattiva.it/uri-res/N2Ls?urn:nir:stato:legge:1953-01-05;4) (letta per articolo, in sintesi, 08/11/2026).
- D.L. 25 giugno 2008 n. 112, art. 39: [Normattiva](https://www.normattiva.it/uri-res/N2Ls?urn:nir:stato:decreto.legge:2008-06-25;112~art39) (sintesi).
- D.Lgs. 165/2001, art. 2: [Normattiva](https://www.normattiva.it/uri-res/N2Ls?urn:nir:stato:decreto.legislativo:2001-03-30;165~art2) (sintesi).
- L. 335/1995, art. 2 (c. 26, c. 30): [Normattiva](https://www.normattiva.it/uri-res/N2Ls?urn:nir:stato:legge:1995-08-08;335~art2) (sintesi).
- D.Lgs. 230/2021, art. 10: [Normattiva](https://www.normattiva.it/uri-res/N2Ls?urn:nir:stato:decreto.legislativo:2021-12-29;230~art10) (sintesi).
- Interpello del Ministero del lavoro del 30/09/2026 (prot. 15911) sulle modalità digitali di consegna dei documenti del rapporto: [lavoro.gov.it](https://www.lavoro.gov.it/documenti-e-norme/interpelli/interpello-2-del-30092026) (PDF letto per intero).
- Interpello del Ministero del lavoro del 31/08/2026 (prot. 14406, LUL e lavoratori autonomi delle piattaforme): [lavoro.gov.it](https://www.lavoro.gov.it/documenti-e-norme/interpelli/interpello-n-1-2026) (PDF letto per intero; citato come contesto).
- Guida alla lettura del cedolino NoiPA (MEF), anno non indicato nel PDF: [noipa.mef.gov.it](https://noipa.mef.gov.it/documents/27938/34120621/Approfondimento+del+mese+di+settembre+-+Guida+alla+lettura+del+cedolino+NoiPA/6692361d-54bd-48f4-9869-82b8faebfa61) (PDF letto per intero). Pagina NoiPA «Cedolino»: [noipa.mef.gov.it](https://noipa.mef.gov.it/en/web/mypa/notizia-in-primo-piano/-/asset_publisher/U7wB7HhofwvD/content/cedolino?inheritRedirect=false).
- Raccolta quesiti 2009 della Direzione provinciale del lavoro di Macerata (quesiti 11, 12, 44, 86): [lavoro.gov.it](https://www.lavoro.gov.it/sites/default/files/archivio-doc-pregressi/DTL_MC/QuesitiAnno2009.pdf) (PDF letto per intero; risposte di un ufficio territoriale, con la clausola «fino a contrario avviso del Ministero»).
- Camera dei deputati, scheda di lettura sulla proposta C. 2453 (11/03/2015): [documenti.camera.it](https://documenti.camera.it/Leg17/dossier/Testi/LA0393.htm).

Letture di terzi, non primarie.

- Interpello 1/2008 (nota 11/02/2008): [ANCE](https://ance.it/2008/02/interpello-n-1-2008-trasmissione-telematica-del-prospetto-paga/?print=pdf). Testo ministeriale non letto.
- Interpello 3/2009: [dottrinalavoro.it](https://www.dottrinalavoro.it/prassi-c/interpelli-c/min-lavoro-interpello-libro-unico-ed-enti-pubblici-economici).
- D.M. 9 luglio 2008: [Certifico](https://www.certifico.com/news/decreto-9-luglio-2008) (riproduzione; non Gazzetta Ufficiale).
- Consegna del prospetto (firma, area riservata, posta): [EC News](https://www.ecnews.it/lavoro/speciale-della-settimana/consegna-prospetto-paga/).
- LUL e PA, co.co.co. e circolare 20/2008 (sintesi): [Fisco e Tasse](https://www.fiscoetasse.com/approfondimenti/12327-libro-unico-del-lavoro-cose-come-funziona.html), [Fisco e Tasse, soggetti esclusi](https://www.fiscoetasse.com/domande-e-risposte/10485-chi-sono-i-soggetti-esclusi-dall-obbligo-di-tenuta-del-libro-unico-del-lavoro.html), [Consulentia](http://www.consulentia.it/it/news/libro-unico-del-lavoro-enti-pubblici-non-obbligati_1465.htm).
- Altri documenti del repo riletti per i riferimenti: `docs/research/regimi-titolo-compenso.md` (amministratori e co.co.co.), `docs/research/irap-scadenza-riparto.md` (stile).

## Punti ancora da verificare (elenco)

- Testo integrale della circolare Min. Lavoro 20/2008 (21/08/2008): PDF scansionato, non letto. Passaggio sulle PA e sui co.co.co.
- FAQ ministeriale sul LUL, risposta n. 12 sezione A (testo originale); interpello 3/2009 sul sito del Ministero.
- Come si concilia l'art. 4 L. 4/1953 (esclusione di Comuni e Province dall'art. 1) con la prassi che presuppone il prospetto; trattamento di Unioni di comuni, Città metropolitane, comunità montane, consorzi.
- Atto che ha introdotto il codice del contratto nell'art. 1 (testo in vigore dal 28/06/2026) e atto del 2015 sull'art. 5.
- Testo integrale degli artt. 1-5 L. 4/1953 (lettura in sintesi) e degli interpelli 1/2008 e 13/2012 sul sito del Ministero.
- Firma del prospetto elettronico negli enti pubblici; fonte della regola «copia del LUL senza firma»; comma di L. 205/2017 sulla firma del lavoratore.
- Conservazione dei cedolini negli enti locali (durata e regole AgID/CAD per la PA); D.M. 9 luglio 2008 sulla Gazzetta Ufficiale.
- Codice unico dei contratti collettivi (CNEL) per i CCNL pubblici.
- Prassi per amministratori e co.co.co. (nota di pagamento); recupero della quota del collaboratore sul contributo alla Gestione separata.
- Posizione del Garante sulla posta elettronica del cedolino nella PA.
- ANF residuo per i nuclei senza figli nei dipendenti pubblici (fonti secondarie discordi su chi lo gestisce).
