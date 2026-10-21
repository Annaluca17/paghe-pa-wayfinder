# Paradigmi di calcolo alternativi al ciclo mensile batch

Ticket: #2 (mappa #1). Branch: `research/paradigmi-calcolo`. Data: 2026-10-21.

## Domanda

Quali paradigmi di calcolo sono applicabili alle retribuzioni pubbliche (Enti Locali, CCNL Funzioni Locali) in alternativa al ciclo mensile batch, e con quali trade-off? Candidati: event sourcing / ledger, calcolo continuo o event-driven, calcolo incrementale, motori a regole dichiarative, altri. Per ciascuno: casi reali in payroll o sistemi fiscali, determinismo e riproducibilità, costo di adozione, effetto sulla tracciabilità di ogni importo fino a norma, atto o input.

## Legenda di certezza

- **norma certa**: riferimento normativo o specifica ufficiale individuato e confermato da almeno una fonte istituzionale o dal testo stesso.
- **prassi-interpretazione**: pratica documentata, scelta progettuale argomentata, letteratura tecnica, oppure deduzione di chi scrive.
- **da verificare**: non confermato su fonte primaria letta in questa sessione.

Nota di metodo: in questa sessione la rete in uscita era limitata. Sono stati letti direttamente solo file su `raw.githubusercontent.com` (codice sorgente e README di OpenFisca, Catala, Mlang). Le altre fonti (siti istituzionali ATO, HMRC, gov.br, INPS, Agenzia Entrate, OMG, arXiv) sono state raggiunte solo tramite motore di ricerca: le affermazioni relative portano l'URL della fonte primaria individuata, ma dove il contenuto non è stato letto per intero sono marcate **da verificare** o accompagnate da questa avvertenza.

## Sintesi (risposta)

1. Il "ciclo mensile batch" non è imposto come paradigma di calcolo dalla norma: lo sono alcune **cadenze di output** (denuncia mensile analitica ex art. 44 c. 9 DL 269/2003 tramite UniEmens/ListaPosPA; versamenti; adempimenti annuali) e il **principio di cassa** fiscale (ritenuta all'atto del pagamento, art. 23 DPR 600/1973; cassa allargata al 12 gennaio, art. 51 c. 1 TUIR). Il calcolo può quindi essere organizzato diversamente, purché proietti gli output nelle cadenze richieste. **prassi-interpretazione** (deduzione dalle norme citate sotto).
2. Il paradigma più adatto come **spina dorsale** è un **registro di fatti immutabile e bitemporale** (event sourcing / ledger): ogni fatto (atto, presenza, variazione contrattuale, pagamento) è registrato con data di efficacia e data di registrazione; gli importi sono proiezioni derivate. Risolve in modo nativo arretrati, rinnovi contrattuali retroattivi, rettifiche, e la riproducibilità "come risultava alla data X". **prassi-interpretazione**.
3. Per le **regole** il paradigma più adatto è il **"rules as code" dichiarativo con parametri datati e riferimento normativo per parametro** (modello OpenFisca/Catala), non un motore a regole a inferenza (Rete/forward chaining). Le regole diventano funzioni pure di (fatti, periodo, parametri vigenti), quindi deterministiche e citabili. **prassi-interpretazione**, con casi reali governativi verificati (OpenFisca, Catala presso DGFiP/CNAF francesi, linguaggio M della DGFiP).
4. Il **calcolo incrementale** (ricalcolo solo di ciò che dipende da un fatto cambiato) è una tecnica di esecuzione da applicare sopra 2+3, non un paradigma autonomo: vale solo se le regole sono funzioni pure con dipendenze esplicite. Per enti da 10 a 400 persone il guadagno prestazionale è irrilevante; il guadagno vero è l'**analisi d'impatto** (quali importi cambiano se cambia un fatto). **prassi-interpretazione**.
5. Il **calcolo continuo / event-driven** (ricalcolare a ogni fatto e mostrare sempre il "maturato") ha precedenti reali solo sul lato **dichiarativo** verso le amministrazioni (UK RTI, Australia STP, Brasile eSocial, Francia DSN con signalements), non come obbligo di calcolo. Per un ente locale è utile come **anteprima continua e verifica anticipata**, mentre il "pagamento" resta un evento discreto che congela un'istantanea. **prassi-interpretazione**.
6. **Tracciabilità**: la combinazione registro di fatti + regole dichiarative con riferimento normativo + traccia di calcolo (albero delle dipendenze valutate) è l'unica, tra quelle esaminate, che permette di rispondere meccanicamente "da quali norme, atti e input deriva questo euro". Il batch mensile tradizionale produce risultati ma non conserva la derivazione. **prassi-interpretazione**.
7. **Costo di adozione**: alto nel modellare correttamente il tempo (bitemporalità) e nel codificare le regole con riferimenti; basso in infrastruttura (dimensioni minime, nessuna necessità di stream processing distribuito). Il rischio principale è la versione delle regole: riprodurre un calcolo passato richiede di conservare la versione del codice-regola usata, non solo i parametri. **prassi-interpretazione**.

Raccomandazione per la mappa: paradigma ibrido "**registro di fatti bitemporale + regole dichiarative datate e citate + proiezioni per periodo + istantanee congelate al pagamento**", con calcolo incrementale e anteprima continua come proprietà derivate. **prassi-interpretazione**.

## Vincoli normativi che condizionano il paradigma

| Vincolo | Effetto sul paradigma | Certezza | Fonte |
|---|---|---|---|
| Ritenuta IRPEF operata dal sostituto "all'atto del pagamento" | Il fatto fiscalmente rilevante è il pagamento, non il mese di competenza: il pagamento deve essere un evento esplicito | **norma certa** (art. 23 DPR 600/1973; testo letto su copia non ufficiale) | https://archivio.urp.cnr.it/documenti/c08-02a1a4ART.%2023%20DPR%20600-1973.pdf |
| Conguaglio di fine anno o a cessazione tra ritenute operate e imposta annua | Serve una proiezione annuale che riaggrega gli eventi di pagamento | **da verificare** il testo vigente del conguaglio nell'art. 23 (non letto) | https://www.normattiva.it (testo non raggiunto in sessione) |
| Cassa allargata: somme corrisposte entro il 12 gennaio imputate all'anno precedente | La data di pagamento non basta: serve la data di competenza (periodo a cui si riferisce) accanto a quella di pagamento | **norma certa** (art. 51 c. 1 TUIR; confermato da prassi AdE, circ. 2/E/2003 citata) | https://agenziaentrate.gov.it/portale/documents/20143/305947/Risoluzione+n+377+2008_risoluzione377Edel9ottobre2008.pdf/77c64c25-a33a-0ae9-8f65-a3aaa58ee4de |
| Arretrati di anni precedenti a tassazione separata se il ritardo dipende da leggi, contratti, sentenze, atti amministrativi sopravvenuti | La **causa** del ritardo (es. rinnovo CCNL, atto) deve essere registrata come dato collegato all'importo: è tracciabilità con effetto fiscale | **norma certa** (art. 17 c. 1 lett. b TUIR); **prassi-interpretazione** l'orientamento Cass. n. 2310/2023 | https://www.studiocerbone.com/?p=471782 |
| Denuncia mensile analitica per gli iscritti alle gestioni ex INPDAP (ListaPosPA in UniEmens) | Cadenza mensile di **output**, non di calcolo; la ListaPosPA riporta periodi di riferimento, quindi il modello deve saper proiettare per periodo di competenza | **norma certa** (art. 44 c. 9 DL 269/2003; circ. INPS 105/2012) | https://servizi2.inps.it/CircolariZIP/Circolare%20numero%20105%20del%2007-08-2012.pdf |

## Findings per paradigma

### 1. Event sourcing / registro (ledger) bitemporale

**Cos'è.** Lo stato non si aggiorna in place: si registra in append-only ogni fatto; lo stato a una data si ottiene rigiocando i fatti. Le correzioni sono nuovi fatti (storno, rettifica), non sovrascritture. Con la **bitemporalità** ogni fatto ha un tempo di validità (quando vale nella realtà) e un tempo di registrazione (quando il sistema lo ha saputo).

- Il pattern "Retroactive Event" (Fowler, 2005) tratta esplicitamente fatti scoperti dopo che sono accaduti, con due date per evento e proiezioni "as at" / "as of". **prassi-interpretazione** (pagina primaria non raggiunta; esistenza e contenuto confermati da fonte secondaria). https://martinfowler.com/eaaDev/RetroactiveEvent.html ; https://www.infoq.com/news/2018/02/retroactive-future-event-sourced
- Fowler indica che i suoi "accounting patterns" (posting rule: un evento attiva una regola che genera scritture) sostituiscono il capitolo contabile di *Analysis Patterns*; è il modello concettuale più vicino a "fatto → regola → importo". **da verificare** (documento non letto). https://martinfowler.com/apsupp/apchap6.pdf
- SQL:2011 standardizza tabelle con application-time period (validità) e system-versioned (registrazione); la combinazione è la bitemporalità. **da verificare** sul testo ISO/IEC 9075-2 (letto solo tramite sintesi secondarie). https://en.wikipedia.org/wiki/Temporal_database

**Casi reali in payroll/fisco (lato dichiarativo).**
- Brasile, eSocial: gli obblighi del datore sono trasmessi come **eventi** codificati (S-1200 remunerazione per periodo, S-1210 pagamenti, S-2200 ammissione, ecc.); una rettifica è lo stesso evento con `indRetif=2` e il numero di ricevuta dell'originale; l'annullamento è l'evento S-3000 che referenzia la ricevuta. È un registro di eventi con correzioni per compensazione, gestito dall'amministrazione. **prassi-interpretazione** (fonti lette: documentazione di fornitori che riporta il Manual de Orientação; leiaute ufficiale S-1.3 non letto, quindi i nomi dei campi sono **da verificare**). https://documentacao.senior.com.br/gestao-de-pessoas-hcm/esocial/leiautes/periodicos/s-1200.htm ; https://documentacao.senior.com.br/gestao-de-pessoas-hcm/esocial/leiautes/nao-periodicos/s-3000.htm
- eSocial distingue S-1200 (remunerazione per periodo di competenza) da S-1210 (pagamenti): la stessa separazione competenza/cassa richiesta in Italia da art. 51 e art. 17 TUIR. **prassi-interpretazione**.
- Australia, STP: "pay event" a ogni pagamento e "update event" per correggere i progressivi senza un pagamento associato. **da verificare** (guida ufficiale SBR individuata ma non letta). https://www.sbr.gov.au/sites/default/files/ato_payevnt.0004_2020_business_implementation_guide.docx

**Determinismo e riproducibilità.** Alti, a condizione che: (a) le regole siano versionate e che ogni proiezione registri la versione regola usata; (b) gli eventi siano immutabili e ordinati; (c) l'aritmetica (arrotondamenti) sia definita. Una proiezione "come risultava al pagamento di marzo" è ricostruibile filtrando per tempo di registrazione. **prassi-interpretazione**.

**Costo di adozione.** Medio-alto concettualmente (modellare due assi temporali, schema degli eventi che evolve nel tempo, proiezioni), basso infrastrutturalmente per 10-400 persone: un database relazionale con tabelle append-only basta, non serve un event store dedicato. **prassi-interpretazione**.

**Tracciabilità.** Ottima sugli **input**: ogni importo deriva da fatti identificabili con data, autore e atto di origine. Da sola non traccia la **norma**: serve il paradigma 2. **prassi-interpretazione**.

### 2. Regole dichiarative "rules as code" (parametri datati, riferimenti normativi)

**Cos'è.** La norma è codificata come insieme di definizioni pure (variabile = formula di altre variabili e parametri), con parametri che hanno valori datati e un riferimento alla fonte. Il motore valuta le definizioni per una entità e un periodo.

- OpenFisca: ogni variabile dichiara `definition_period` (es. MONTH, YEAR) e `reference` ("Always use the most official source"); la formula riceve `(person, period, parameters)` e legge `parameters(period)`, cioè il valore vigente nel periodo. **norma certa** come specifica del software (codice sorgente letto). https://raw.githubusercontent.com/openfisca/country-template/main/openfisca_country_template/variables/taxes.py
- OpenFisca: i parametri sono file YAML con valori indicizzati per data di decorrenza e `metadata.reference` anche per singolo valore datato; un valore `expected` segnala una variazione attesa senza effetto sul calcolo. **norma certa** come specifica del software (file letti). https://raw.githubusercontent.com/openfisca/country-template/main/openfisca_country_template/parameters/benefits/basic_income.yaml ; https://raw.githubusercontent.com/openfisca/country-template/main/openfisca_country_template/parameters/taxes/income_tax_rate.yaml
- Catala: DSL per "derivare algoritmi fedeli per costruzione dai testi legislativi", con programmazione letterata (ogni riga di codice annota l'articolo di legge) e produzione di un PDF leggibile da giuristi. Il README dichiara il compilatore "yet unstable". **norma certa** come descrizione ufficiale del progetto (README letto). https://raw.githubusercontent.com/CatalaLang/catala/master/README.md
- Catala: esempi ufficiali sulle prestazioni familiari francesi (Code de la sécurité sociale) e sugli aiuti per l'alloggio, "il caso più grande e ambizioso". **norma certa** come contenuto del repository (letto). https://raw.githubusercontent.com/CatalaLang/catala-examples/master/README.md
- Catala: il paper ICFP 2021 (Merigoux, Chataing, Protzenko) modella la struttura "regola generale più eccezioni" con default logic e riporta di aver trovato un errore nell'implementazione ufficiale francese delle prestazioni familiari; il catalogo open source UE indica la DGFiP come utilizzatore. **da verificare** (abstract letto solo tramite sintesi). https://arxiv.org/abs/2103.03198 ; https://interoperable-europe.ec.europa.eu/eu-oss-catalogue/solutions/catala
- Linguaggio M della DGFiP: DSL inventato dall'amministrazione fiscale francese per trascrivere il codice tributario; il codice del calcolo dell'imposta sul reddito è pubblicato; Mlang ne è una reingegnerizzazione che passa i test privati DGFiP (redditi 2018-2021, al settembre 2022) ma "senza garanzia legale". **norma certa** come descrizione del progetto (README letto). https://raw.githubusercontent.com/MLanguage/mlang/master/README.md
- OCSE/OPSI "Cracking the Code" (2020) indica tra i principi del rules as code trasparenza, accountability, **tracciabilità**, appellabilità. **da verificare** (rapporto non letto). https://oecd-opsi.org/publications/cracking-the-code/

**Motori a regole a inferenza (Rete, Drools) e DMN.** DMN (OMG) offre tabelle di decisione con linguaggio FEEL e "hit policy" (Unique, Any, Priority, First, Collect...). Sono adatti a decisioni tabellari (es. classificazione di un istituto, aliquota per fascia), meno al calcolo aritmetico concatenato e al tempo. I motori a inferenza in avanti rendono l'ordine di attivazione meno leggibile e quindi la traccia più difficile da spiegare. **prassi-interpretazione**; dettagli DMN **da verificare** sulla specifica OMG (non raggiunta). https://www.omg.org/spec/DMN/ ; https://docs.camunda.io/docs/components/modeler/dmn/decision-table-hit-policy/

**Determinismo e riproducibilità.** Massimi: funzioni pure di input datati. Due avvertenze: aritmetica decimale e arrotondamenti vanno fissati (Mlang richiede precisione multipla MPFR per riprodurre i risultati DGFiP: **norma certa** come requisito del progetto, README letto); per rifare un calcolo passato occorre la versione del codice-regola, non solo dei parametri. **prassi-interpretazione**.

**Costo di adozione.** Alto in conoscenza (codificare CCNL Funzioni Locali, integrativo, fiscale, previdenziale con riferimenti), basso in tecnologia. Le regole deterministiche già presenti nei tool esistenti dell'utente sono materia prima riusabile. **prassi-interpretazione**.

**Tracciabilità.** Ottima sulla **norma**: ogni variabile e ogni valore di parametro porta il riferimento; la valutazione produce un albero di dipendenze ispezionabile. **prassi-interpretazione** (OpenFisca dispone di strumenti di tracing: **da verificare**, documentazione non raggiunta).

### 3. Calcolo continuo / event-driven

**Cos'è.** Ogni nuovo fatto innesca il ricalcolo delle proiezioni interessate; il "maturato" è sempre aggiornato; la chiusura è solo una istantanea.

- UK RTI: la Full Payment Submission va inviata "on or before" il giorno di pagamento. **da verificare** (pagina gov.uk non raggiunta; confermato da fonti secondarie). https://www.gov.uk/running-payroll/reporting-to-hmrc
- Australia STP: rendicontazione per ogni dipendente "on or before each payday", dichiarazione di finalizzazione annuale. **da verificare** (pagina ATO non letta direttamente). https://www.ato.gov.au/businesses-and-organisations/hiring-and-paying-your-workers/single-touch-payroll
- Francia DSN: DSN mensile più "signalements d'événements" (arresto di lavoro, fine contratto) entro 5 giorni lavorativi quando l'evento non può attendere la DSN mensile. **da verificare** (charte DSN non letta). https://www.net-entreprises.fr/media/documentation/charte-dsn.pdf ; https://entreprendre.service-public.gouv.fr/vosdroits/F23892
- Questi casi sono **reporting event-driven imposto dall'amministrazione**, non calcolo continuo interno. In Italia non risulta un obbligo analogo per gli enti locali: gli output individuati sono a cadenza mensile o annuale. **prassi-interpretazione**; assenza di obbligo event-driven italiano **da verificare**.

**Determinismo.** Il ricalcolo continuo è deterministico solo se è una proiezione pura del registro (paradigmi 1+2). Se il calcolo continuo aggiorna stati mutabili, l'ordine di arrivo dei fatti cambia i risultati: è il rischio principale. **prassi-interpretazione**.

**Costo.** Basso se costruito sopra 1+2 (si ricalcola al salvataggio di un fatto); alto se implementato come pipeline a messaggi. **prassi-interpretazione**.

**Tracciabilità.** Neutra di per sé; il valore è anticipare le verifiche (anche con AI) al momento in cui il fatto entra, non a fine mese. È collegato al pain point "AI assente nelle verifiche". **prassi-interpretazione**.

### 4. Calcolo incrementale

**Cos'è.** Si mantiene il grafo delle dipendenze tra valori calcolati e si ricalcola solo ciò che dipende da input cambiati.

- "Build systems à la carte" (Mokhov, Mitchell, Peyton Jones, ICFP 2018; JFP 2020) mostra che i sistemi incrementali si descrivono con due scelte ortogonali: strategia di scheduling e strategia di ricostruzione. **da verificare** (paper non letto, solo abstract tramite ricerca). https://www.microsoft.com/en-us/research/publication/build-systems-a-la-carte/

**Determinismo.** Garantito se le regole sono pure e le dipendenze sono dichiarate; altrimenti il ricalcolo parziale può divergere dal ricalcolo totale. Prova pratica: il ricalcolo totale deve dare lo stesso risultato dell'incrementale (test di equivalenza). **prassi-interpretazione**.

**Costo.** Inutile per prestazioni a questa scala (10-400 persone si ricalcolano per intero in tempi trascurabili); utile per **analisi d'impatto** di un rinnovo contrattuale o di un atto ("quali importi, di chi, in quali periodi cambiano"). **prassi-interpretazione**.

**Tracciabilità.** Il grafo delle dipendenze è la stessa struttura che serve per spiegare un importo. **prassi-interpretazione**.

### 5. Altri paradigmi considerati

- **Calcolo per periodo di competenza con istantanee al pagamento** (variante del batch): si calcola per periodo, ma ogni pagamento congela una fotografia firmata degli importi e delle versioni di regole usate. È il "minimo" che conserva la compatibilità con le cadenze di output. **prassi-interpretazione**.
- **Partita doppia come modello del dovuto** (ogni importo è una scrittura tra conti: ente, persona, erario, INPS, fondo risorse decentrate): rende naturale il passaggio a **proposte di movimento contabile** verso la ragioneria e la verifica di capienza del fondo come saldo. **prassi-interpretazione**; la mappatura sui piani dei conti della contabilità armonizzata è **da verificare** in altro ticket.

## Trade-off sintetici

| Paradigma | Determinismo / riproducibilità | Costo di adozione | Tracciabilità fino a norma/atto/input | Casi reali |
|---|---|---|---|---|
| Batch mensile | Alto sul singolo run, basso nel tempo (stato sovrascritto, arretrati come differenze) | Basso (noto) | Debole: risultato senza derivazione | Prassi diffusa |
| Registro di fatti bitemporale | Alto con regole versionate | Medio-alto concettuale, basso infrastruttura | Forte su input e atti | eSocial, STP (lato dichiarativo) |
| Regole dichiarative datate | Massimo (funzioni pure) | Alto in conoscenza | Forte su norma | OpenFisca, Catala, M/DGFiP |
| Motore a inferenza / DMN | Alto se hit policy univoca | Medio | Media (ordine di attivazione opaco) | Uso generale in BPM |
| Event-driven continuo | Alto solo come proiezione pura | Basso sopra 1+2 | Neutra; anticipa le verifiche | RTI, STP, DSN (obblighi di reporting) |
| Incrementale | Alto con dipendenze esplicite | Basso sopra 2 | Il grafo è la spiegazione | Build system, compilatori |

## Implicazioni per la mappa

- **Concetti del dominio** (punto "Not yet specified"): candidati a sostituire anagrafica/voci/cedolino sono *fatto* (con validità e registrazione), *regola* (con riferimento normativo e versione), *parametro datato*, *proiezione per periodo*, *istantanea di pagamento*. Da portare al grilling. **prassi-interpretazione**.
- **Provenienza degli importi**: catena proposta = importo → regola (versione, riferimento normativo) → parametri vigenti (riferimento) → fatti (atto di origine, autore, date). **prassi-interpretazione**.
- **Doppia data obbligatoria su ogni importo**: competenza e pagamento, più la causa del ritardo, per art. 51 e art. 17 TUIR. **norma certa** per i requisiti fiscali; **prassi-interpretazione** per la soluzione.
- **Flusso proposta-conferma**: mandato emesso e reversale sono naturalmente eventi di ritorno nel registro. **prassi-interpretazione**.
- **AI nelle verifiche**: interviene sull'ingresso dei fatti e sul confronto tra proiezioni, mai come fonte di un importo (gli importi restano da regole deterministiche). **prassi-interpretazione**.
- **Tool esistenti**: le loro regole deterministiche si migrano come definizioni pure con parametri datati; gli output obbligatori si generano come proiezioni. **prassi-interpretazione**.

## Domande aperte

1. Versionamento delle regole: come si conserva e si richiama la versione del codice-regola usata per ogni istantanea (hash del repository regole? rilascio datato?) e chi la approva.
2. Rinnovi CCNL retroattivi: il ricalcolo degli arretrati genera fatti di rettifica per periodo o una sola differenza? Effetti su ListaPosPA per periodi pregressi e su tassazione separata. **da verificare** con istruzioni INPS e AdE.
3. Testo vigente del conguaglio nell'art. 23 DPR 600/1973 e regole operative per conguaglio a cessazione: da leggere su Normattiva.
4. Esiste un formato standard per esprimere riferimenti normativi italiani in modo stabile (es. URN NIR / ELI) da usare nel campo `reference`? **da verificare**.
5. Arrotondamenti: quali regole di arrotondamento sono imposte da norma (contributi, IRPEF, addizionali) e quali sono prassi; condizionano la riproducibilità.
6. Bitemporalità e correzioni di dati dichiarati: come si rappresenta che un fatto è stato già "usato" in un output inviato (UniEmens, F24EP) e quindi la sua correzione richiede una rettifica dell'output.
7. Fonti non raggiunte in sessione da rileggere: pagina Fowler "Retroactive Event", paper Catala ICFP 2021, specifica OMG DMN, guida SBR STP, Manual de Orientação eSocial S-1.3, pagina HMRC RTI.
