# AI nelle verifiche paghe: tecniche e vincoli

Ticket: #9 (mappa #1). Branch: `research/ai-verifiche`. Data: 21/10/2026.

## Domanda

Quali tecniche di AI (e non) sono applicabili alle verifiche delle retribuzioni dell'Ente (anomaly detection, controlli di coerenza, spiegazione degli scostamenti, verifica di conformità rispetto a norme) e con quali vincoli (GDPR, AI Act, AgID, normativa italiana)? Dove l'AI aggiunge valore rispetto ai controlli deterministici e dove no.

## Legenda e nota sulle fonti

- **norma certa**: contenuto di un atto normativo identificato per numero e articolo, con URL della fonte ufficiale.
- **prassi-interpretazione**: giurisprudenza, circolari, pareri, letteratura tecnica, oppure deduzione di chi scrive applicata al caso paghe.
- **da verificare**: dato non confermato sul testo ufficiale, o fonti discordanti.

Limite di metodo dichiarato: in questa sessione i siti EUR-Lex, Normattiva, Gazzetta Ufficiale, Garante e AgID non erano raggiungibili in lettura diretta (proxy di rete). Le fonti ufficiali sono state individuate tramite motore di ricerca (estratti indicizzati delle pagine ufficiali), incrociati con commenti secondari. Dove l'estratto ufficiale e la conoscenza consolidata del testo coincidono la marcatura è **norma certa**; dove il contenuto è emerso solo da fonti secondarie o da atti recenti (2026) la marcatura è **da verificare**. Prima di citare un articolo in un atto dell'Ente, rileggere il testo vigente all'URL indicato.

## Sintesi

1. Le verifiche paghe si dividono in due famiglie: controlli **deterministici** (la regola è nota: aliquote, massimali, capienza del fondo, quadrature tra output) e controlli **statistici/linguistici** (la regola non è nota o non è scritta: scostamenti insoliti, casi mai visti, lettura di atti). L'AI serve solo alla seconda famiglia.
2. Dove esiste una regola normativa o contrattuale calcolabile, il controllo deve restare deterministico: è riproducibile, spiegabile, tracciabile fino alla fonte (requisito della mappa) e non introduce errori probabilistici. Un LLM non deve "ricalcolare" importi.
3. L'AI aggiunge valore come **rete di sicurezza** sui casi che le regole non coprono (anomaly detection sugli scostamenti mese su mese o rispetto a gruppi omogenei), nella **spiegazione** degli scostamenti in linguaggio naturale a partire dalla catena di provenienza già calcolata, e nella **lettura assistita** di atti e testi normativi per proporre regole da far validare a un umano.
4. Vincolo normativo centrale: nella PA l'AI ha funzione strumentale e la responsabilità del provvedimento resta della persona (L. 132/2025, art. 14, **da verificare** sul testo GU). Il GDPR art. 22 vieta decisioni basate unicamente su trattamento automatizzato con effetti giuridici o analoghi significativi (**norma certa**): l'AI può segnalare, non decidere né bloccare pagamenti in automatico.
5. Classificazione AI Act: un verificatore che segnala anomalie sugli importi non rientra di per sé tra gli usi "occupazione e gestione dei lavoratori" dell'Allegato III, punto 4 (**prassi-interpretazione**), ma diventa ad alto rischio se usato per monitorare o valutare prestazioni e comportamento dei lavoratori, o se effettua profilazione (Allegato III punto 4 b e art. 6 par. 3, **norma certa**). Il disegno deve tenere separati "anomalia dell'importo" e "anomalia della persona".
6. Le scadenze AI Act per i sistemi dell'Allegato III sono state differite al 2 dicembre 2027 dal Regolamento (UE) 2026/1744 ("Omnibus digitale sull'IA") (**da verificare** sul testo GUUE).

## Tecniche

### 1. Controlli di coerenza deterministici (non AI)

Cosa sono: regole esplicite con esito vero/falso. Esempi nel dominio:
- quadrature tra output obbligatori (totali contributivi per gestione tra denuncia mensile e versamenti F24EP; imponibili annui tra conguaglio e CU);
- vincoli di capienza (somma degli istituti accessori pagati contro le risorse del fondo risorse decentrate disponibili per l'anno);
- vincoli di dominio (aliquote, massimali e minimali, soglie, incompatibilità tra regimi: amministratori, co.co.co., LSU/LPU);
- coerenza tra input giuridico e importo (un atto di progressione produce l'importo atteso dalla tabella contrattuale vigente).

Valutazione: **prassi-interpretazione**. Sono il nucleo del sistema di verifica; i tool esistenti dell'utente ne contengono già la conoscenza normativa. Ogni violazione ha una spiegazione esatta (regola, fonte, dato). Limite: coprono solo ciò che è stato previsto.

### 2. Anomaly detection (AI/statistica)

Cosa è: individuare valori insoliti senza una regola esplicita. Tecniche di riferimento:
- metodi semplici e spiegabili: scostamento rispetto al mese precedente o allo stesso mese dell'anno precedente, z-score/IQR per gruppo omogeneo (stessa categoria, profilo, tipo di rapporto);
- metodi multivariati: Isolation Forest (Liu, Ting, Zhou, ICDM 2008, pp. 413-422, DOI 10.1109/ICDM.2008.17; implementazione documentata in scikit-learn: https://scikit-learn.org/stable/modules/generated/sklearn.ensemble.IsolationForest.html) isola i punti anomali con alberi casuali; costo lineare, nessun bisogno di esempi etichettati.

Valutazione (**prassi-interpretazione**):
- utile su enti da 10 a 400 persone soprattutto nella forma semplice (confronto temporale e per gruppo); i modelli multivariati soffrono di pochi dati per ente e di forte stagionalità (arretrati, rinnovi contrattuali, conguagli, tredicesima) che generano falsi positivi;
- l'unità di analisi deve essere l'**importo e la sua provenienza** (es. "componente X del mese di ottobre è 3 volte la mediana degli ultimi 12 mesi senza un atto nuovo collegato"), non il lavoratore; altrimenti si scivola nel monitoraggio del comportamento (vedi vincoli);
- il segnale più forte è l'**importo senza provenienza**: un importo che non risale a norma, atto o input è un'anomalia rilevabile deterministicamente se il modello registra la catena di provenienza.

### 3. Spiegazione degli scostamenti

Due livelli distinti:
- **spiegazione calcolata** (deterministica): differenza tra due periodi scomposta per causa, ricostruita dalla catena norma, atto, input, importo. È l'unica spiegazione con valore probatorio. **prassi-interpretazione**
- **spiegazione redatta** (LLM): un modello linguistico trasforma la scomposizione già calcolata in un testo leggibile per l'ufficio personale o per il dipendente. Il modello non deve introdurre cifre proprie; ogni numero nel testo deve essere copiato dalla scomposizione e verificabile automaticamente (controllo di uguaglianza tra numeri citati e numeri calcolati). **prassi-interpretazione**
- per i modelli statistici, tecniche di attribuzione come SHAP (Lundberg, Lee, NeurIPS 2017, https://arxiv.org/abs/1705.07874) indicano quali variabili hanno spinto il punteggio di anomalia; utili al tecnico, poco leggibili per l'operatore. **prassi-interpretazione**

### 4. Verifica di conformità normativa

- La conformità a una norma calcolabile (aliquota, limite, scadenza) si verifica con regole deterministiche con riferimento alla fonte. **prassi-interpretazione**
- Un LLM può aiutare a: leggere un nuovo testo (circolare, contratto integrativo, delibera) e proporre una regola o un parametro in forma strutturata; segnalare quali regole esistenti potrebbero essere toccate da una novità; controllare che una regola abbia una fonte citata. La regola proposta entra nel sistema solo dopo validazione umana e test su casi noti. **prassi-interpretazione**
- Rischio noto dei modelli linguistici: generazione di riferimenti o contenuti plausibili ma falsi. Per questo ogni citazione prodotta va verificata contro un archivio di fonti (recupero del testo, confronto della citazione). **prassi-interpretazione**

### 5. LLM come revisori

Uso possibile: "secondo revisore" che legge il riepilogo di un periodo (scostamenti, regole violate, anomalie) e produce una lista di domande o casi da guardare; revisione di una regola nuova contro il testo della fonte; controllo di plausibilità di comunicazioni ai dipendenti.

Limiti (**prassi-interpretazione**): non deterministici (stessa domanda, risposte diverse), non affidabili come calcolatori, sensibili a dati incompleti; costo di revisione umana dei falsi positivi. Il ruolo corretto è generare **ipotesi di controllo**, mai esiti. Ogni passaggio va registrato (input, versione del modello, output, decisione umana) per la tracciabilità richiesta dalla L. 132/2025 art. 14 (**da verificare**) e per la non esclusività della decisione (vedi giurisprudenza amministrativa).

## Dove l'AI aggiunge valore e dove no

| Ambito | Strumento adatto | AI utile? |
|---|---|---|
| Calcolo e ricalcolo di importi | regole deterministiche | No |
| Quadrature tra output obbligatori | regole deterministiche | No |
| Capienza fondo risorse decentrate | regole deterministiche | No |
| Importo privo di provenienza | controllo deterministico sulla catena | No |
| Scostamenti insoliti senza regola nota | anomaly detection semplice (temporale, per gruppo) | Sì, come segnalazione |
| Errori di inserimento (zeri in più, periodi sbagliati) | soglie + anomaly detection | Sì |
| Spiegazione leggibile di uno scostamento | scomposizione deterministica + testo generato da LLM | Sì, solo per la redazione |
| Lettura di nuovi atti e norme | LLM con validazione umana | Sì, come proposta |
| Ricerca di regole mancanti (casi non coperti) | analisi dei falsi negativi storici, LLM come revisore | Sì, come ipotesi |
| Decisione su recuperi, sospensioni, rettifiche | persona responsabile | No (vincolo normativo) |
| Valutazione del comportamento del lavoratore | fuori scopo | No (rischio alto, vedi sotto) |

Tutta la tabella è **prassi-interpretazione**.

## Vincoli normativi

### GDPR (Reg. UE 2016/679) - https://eur-lex.europa.eu/legal-content/IT/TXT/?uri=CELEX:32016R0679

- Art. 22 par. 1: diritto a non essere sottoposti a una decisione basata unicamente sul trattamento automatizzato, compresa la profilazione, che produca effetti giuridici o incida in modo analogo significativamente. **norma certa** (testo riportato anche in CGUE C-203/22, 27/02/2025: https://eur-lex.europa.eu/legal-content/IT/TXT/HTML/?uri=CELEX:62022CJ0203)
- Art. 22 par. 2 lett. b: eccezione se la decisione è autorizzata dal diritto dell'Unione o dello Stato membro che preveda misure adeguate di tutela. Par. 3: per le lettere a) e c) il titolare garantisce almeno intervento umano, possibilità di esprimere opinione e contestare. **norma certa** (contenuto consolidato; testo non riletto in questa sessione)
- Applicazione al caso: una segnalazione AI che passa al vaglio di un operatore non è decisione "unicamente" automatizzata; lo diventa se l'esito (es. trattenuta di recupero, blocco del pagamento) scatta senza intervento umano effettivo. L'intervento umano deve essere sostanziale, non formale. **prassi-interpretazione** (la CGUE nella causa C-634/21 SCHUFA, 7/12/2023, ha dato una lettura ampia di "decisione": **da verificare** l'estensione al caso)
- Art. 35 (DPIA) e art. 88 (trattamento nel contesto lavorativo) sono rilevanti per sistemi che trattano dati dei dipendenti con tecnologie nuove. **prassi-interpretazione** sull'obbligatorietà della DPIA nel caso concreto; **da verificare**.

### AI Act (Reg. UE 2024/1689) - https://eur-lex.europa.eu/legal-content/IT/TXT/?uri=CELEX:32024R1689

- Allegato III, punto 4 b): sono ad alto rischio i sistemi destinati a essere usati per adottare decisioni riguardanti le condizioni dei rapporti di lavoro, la promozione o cessazione, per assegnare compiti in base al comportamento individuale o a tratti personali, o per monitorare e valutare le prestazioni e il comportamento delle persone in tali rapporti. **norma certa**
- Art. 6 par. 3: un sistema dell'Allegato III non è ad alto rischio se non presenta un rischio significativo, in particolare quando esegue un compito procedurale limitato, migliora il risultato di un'attività umana già completata, rileva schemi decisionali o deviazioni da schemi precedenti senza sostituire o influenzare la valutazione umana senza adeguata revisione, oppure svolge un compito preparatorio. La deroga non si applica se il sistema effettua profilazione di persone fisiche. **norma certa** (il considerando 53 cita come esempi trasformazione di dati non strutturati, classificazione documenti, rilevamento di duplicati)
- Applicazione al caso (**prassi-interpretazione**):
  - un verificatore che controlla la correttezza di importi già determinati da norma e atti non adotta "decisioni sulle condizioni del rapporto": le condizioni sono fissate da contratto e atti. È argomentabile che resti fuori dal punto 4 b), o che rientri nelle deroghe dell'art. 6 par. 3 (rilevare deviazioni da schemi precedenti, compito preparatorio) purché non sostituisca la valutazione umana;
  - diventa ad alto rischio, senza deroga possibile, se costruisce profili delle persone (es. "dipendente che tende ad avere straordinari anomali", indici di rischio individuali): è profilazione e monitoraggio del comportamento;
  - se l'Ente fosse deployer di un sistema ad alto rischio: art. 26 par. 7 (informare rappresentanti dei lavoratori e lavoratori prima della messa in servizio sul luogo di lavoro) **norma certa** (testo non riletto in questa sessione) e art. 27 (valutazione d'impatto sui diritti fondamentali per deployer che sono organismi di diritto pubblico; par. 4: integrazione con la DPIA) **norma certa**.
- Art. 5: vieta i sistemi per inferire le emozioni sul luogo di lavoro (salvo motivi medici o di sicurezza). Richiamato dal Garante nel provvedimento 14/05/2026 su un plug-in IA usato da PA (https://www.garanteprivacy.it/home/docweb/-/docweb-display/docweb/10255494). **norma certa** il divieto; **da verificare** il dettaglio del provvedimento.
- Art. 4 (alfabetizzazione in materia di IA): riscritto dall'Omnibus 2026/1744 come obbligo di mezzi. **da verificare**
- Regolamento (UE) 2026/1744 (Omnibus digitale sull'IA), pubblicato in GUUE il 24/07/2026, in vigore dal 27/07/2026: differisce al 2 dicembre 2027 l'applicazione degli obblighi per i sistemi ad alto rischio dell'Allegato III e introduce l'obbligo per il fornitore che invoca l'art. 6 par. 3 di documentare la valutazione. https://eur-lex.europa.eu/eli/reg/2026/1744/oj/ita **da verificare** (fonti secondarie concordi, testo ufficiale non riletto)
- La Commissione ha messo in consultazione (maggio-luglio 2026) linee guida sulla classificazione dei sistemi ad alto rischio. **da verificare** se adottate.

### Normativa italiana

- Legge 23 settembre 2025, n. 132 (Disposizioni e deleghe al Governo in materia di intelligenza artificiale), GU 25/09/2025, in vigore dal 10/10/2025. **norma certa** l'esistenza e gli estremi.
  - Art. 14 (PA): uso dell'IA per efficienza e qualità, garantendo conoscibilità del funzionamento e tracciabilità dell'utilizzo; funzione strumentale e di supporto all'attività provvedimentale; la persona resta unica responsabile dei provvedimenti; misure tecniche, organizzative e formative; nessun nuovo onere. **da verificare** sul testo GU (fonte consultata: estratto indicizzato, https://www.normattiva.it/uri-res/N2Ls?urn:nir:stato:legge:2025-09-23;132)
  - Art. 11 (lavoro): IA usata in modo sicuro, affidabile, trasparente, non lesivo della dignità e della riservatezza; obbligo di informare il lavoratore nei casi dell'art. 1-bis d.lgs. 152/1997; divieto di discriminazioni. **da verificare** (numerazione degli articoli riportata in modo non uniforme da fonti secondarie)
- D.lgs. 152/1997, art. 1-bis (inserito dal d.lgs. 104/2022, "decreto trasparenza", modificato dal d.l. 48/2023): obblighi informativi del datore di lavoro, anche pubblico, quando usa sistemi decisionali o di monitoraggio automatizzati rilevanti per gestione del rapporto, assegnazione di compiti, valutazione delle prestazioni. **norma certa** l'esistenza; **da verificare** il testo vigente del comma 1 (eliminazione di "integralmente").
  - Circolare Ministero del lavoro n. 19 del 20/09/2022: l'intervento umano esclude l'obbligo solo se non "meramente accessorio". **prassi-interpretazione** (**da verificare** se ancora attuale dopo il d.l. 48/2023)
  - Applicazione al caso: un verificatore di importi non è un sistema di valutazione delle prestazioni; ma se un'anomalia porta a decisioni sul rapporto (recuperi, contestazioni), l'Ente deve valutare l'obbligo informativo. **prassi-interpretazione**
- Schema di decreto legislativo di adeguamento al Reg. IA (delega L. 132/2025): il parere del Garante del 14/07/2026 (https://www.garanteprivacy.it/home/docweb/-/docweb-display/docweb/10275626) riferisce che lo schema prevede che le decisioni del datore di lavoro non siano basate solo su trattamenti automatizzati e che la decisione finale spetti a una persona fisica. **da verificare** (atto non ancora individuato in GU).
- Giurisprudenza amministrativa: Consiglio di Stato, sez. VI, n. 2270/2019 e n. 8472/2019 (algoritmo mobilità docenti): legittimità della decisione algoritmica a condizione di piena conoscibilità, imputabilità all'organo titolare del potere, non discriminazione. **prassi-interpretazione** (testo delle sentenze non riletto; **da verificare** prima di citarle).
- Statuto dei lavoratori, art. 4 (controlli a distanza): resta applicabile ai sistemi che consentono controllo dell'attività. **prassi-interpretazione** sulla rilevanza per un sistema di verifica degli importi.

### AgID

- Bozza "Linee guida per l'adozione di IA nella pubblica amministrazione", v1.0 del 14/02/2025, consultazione chiusa a marzo 2025 (https://www.agid.gov.it/sites/agid/files/2025-02/Linee_Guida_adozione_IA_nella_PA.pdf) con appendice sulla valutazione d'impatto (https://www.agid.gov.it/sites/agid/files/2025-02/Appendice_Linee_Guida_IA_nella_PA_Valutazione_impatto.pdf). **da verificare** se adottate in via definitiva: non trovata conferma.
- Bozze 2026 di linee guida su procurement e sviluppo di IA nella PA (Determinazione AgID n. 43/2026, consultazione marzo-aprile 2026) (https://www.agid.gov.it/sites/agid/files/2026-03/LLGG%20procurement_per%20consultazione%20pubblica.pdf). **da verificare** stato e vincolatività.

## Implicazioni per il modello

1. **Due livelli di verifica separati**: un motore di regole deterministiche (obbligatorio, autorevole, con fonte per ogni regola) e un livello di segnalazione AI (facoltativo, consultivo). Gli esiti dell'AI non hanno mai lo stesso stato di una violazione di regola.
2. **La provenienza è il primo controllo**: se ogni importo risale a norma, atto o input, il controllo "importo senza fonte" è deterministico e copre una parte grande di ciò che oggi si chiede all'AI.
3. **Unità di analisi = importo e periodo, non persona**: niente punteggi o profili individuali dei lavoratori; ciò tiene il sistema lontano dall'Allegato III punto 4 b) e dalla profilazione (che impedisce la deroga dell'art. 6 par. 3).
4. **Decisione umana registrata**: ogni segnalazione AI richiede presa d'atto (confermata, respinta con motivo) da parte di un operatore dell'ufficio personale; nessuna azione automatica su importi (art. 22 GDPR, L. 132/2025 art. 14).
5. **Registro di uso dell'AI**: input, versione del modello, output, decisione, autore. Serve per conoscibilità e tracciabilità (L. 132/2025 art. 14, giurisprudenza amministrativa) e per eventuale documentazione ex art. 6 par. 3 AI Act.
6. **LLM confinati a redazione e proposta**: testo delle spiegazioni (con controllo automatico che i numeri citati coincidano con quelli calcolati) e proposte di regole da atti nuovi (con validazione e test).
7. **Valutazioni di impatto**: prevedere una DPIA per il livello AI; FRIA solo se il sistema risultasse ad alto rischio. **prassi-interpretazione**
8. **Dati e fornitori**: se il livello AI usa modelli esterni, i dati retributivi sono dati personali (e talvolta di categorie particolari, es. trattenute sindacali, assenze per malattia): minimizzazione, pseudonimizzazione, valutazione del fornitore. **prassi-interpretazione**

## Domande aperte

1. Il verificatore AI rientra davvero fuori dall'Allegato III punto 4 b)? Dipende dalle linee guida della Commissione sulla classificazione (consultazione 2026): verificarne l'adozione e il testo.
2. Testo vigente di L. 132/2025 artt. 11 e 14 e del decreto legislativo attuativo (se pubblicato): introduce vincoli ulteriori per il datore di lavoro pubblico?
3. Linee guida AgID per l'adozione dell'IA nella PA: adottate in via definitiva? Prevedono obblighi (registro dei sistemi, valutazione d'impatto, responsabile) applicabili a un ente da 10 a 400 dipendenti?
4. Una trattenuta di recupero proposta da una segnalazione e confermata da un operatore: quale livello di revisione rende l'intervento umano "sostanziale" ai fini dell'art. 22 GDPR e della circolare 19/2022?
5. Quanti dati servono a un ente piccolo perché l'anomaly detection non produca più rumore che segnale? Serve un esperimento sul prototipo con dati storici di almeno un ente (fuori scopo la migrazione, ma non il test).
6. Con quali dati è lecito addestrare o calibrare modelli (dati di più enti, se l'operatore esterno su più enti venisse riattivato)?
7. Il d.lgs. 152/1997 art. 1-bis si applica a un sistema che verifica importi e non valuta prestazioni? Serve un parere o una prassi consolidata.

## Fonti

- Reg. (UE) 2024/1689 (AI Act): https://eur-lex.europa.eu/legal-content/IT/TXT/?uri=CELEX:32024R1689
- Reg. (UE) 2026/1744 (Omnibus digitale sull'IA): https://eur-lex.europa.eu/eli/reg/2026/1744/oj/ita
- Reg. (UE) 2016/679 (GDPR): https://eur-lex.europa.eu/legal-content/IT/TXT/?uri=CELEX:32016R0679
- CGUE C-203/22: https://eur-lex.europa.eu/legal-content/IT/TXT/HTML/?uri=CELEX:62022CJ0203
- L. 132/2025: https://www.normattiva.it/uri-res/N2Ls?urn:nir:stato:legge:2025-09-23;132
- D.lgs. 152/1997: https://www.normattiva.it/uri-res/N2Ls?urn:nir:stato:decreto.legislativo:1997-05-26;152
- Garante, provv. 14/05/2026: https://www.garanteprivacy.it/home/docweb/-/docweb-display/docweb/10255494
- Garante, parere 14/07/2026 su schema d.lgs. adeguamento: https://www.garanteprivacy.it/home/docweb/-/docweb-display/docweb/10275626
- AgID, bozza linee guida adozione IA nella PA (2025): https://www.agid.gov.it/sites/agid/files/2025-02/Linee_Guida_adozione_IA_nella_PA.pdf
- AgID, bozza linee guida procurement IA (2026): https://www.agid.gov.it/sites/agid/files/2026-03/LLGG%20procurement_per%20consultazione%20pubblica.pdf
- Liu, Ting, Zhou, Isolation Forest, ICDM 2008, DOI 10.1109/ICDM.2008.17
- scikit-learn IsolationForest: https://scikit-learn.org/stable/modules/generated/sklearn.ensemble.IsolationForest.html
- Lundberg, Lee, A Unified Approach to Interpreting Model Predictions (SHAP), 2017: https://arxiv.org/abs/1705.07874
