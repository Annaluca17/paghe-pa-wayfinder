# Modelli temporali per retroattività, arretrati e conguagli

Ticket: #3 (mappa #1). Data ricerca: 2026-10-21.

Legenda: **norma certa** = riferimento normativo o documento ufficiale riscontrato; **prassi-interpretazione** = prassi amministrativa, dottrina, letteratura tecnica o scelta progettuale argomentata; **da verificare** = non riscontrato su fonte primaria o riscontrato solo in parte.

Nota di metodo: in questa sessione l'accesso diretto alle pagine web (fetch) era bloccato dal proxy; le fonti sono state lette tramite gli estratti restituiti dal motore di ricerca. Dove l'estratto riporta testualmente un documento ufficiale (PDF INPS, Agenzia Entrate, allegato 4/2 pubblicato su governo.it, documentazione di prodotto) la marcatura è **norma certa** o documentazione di prodotto; il testo consolidato su Normattiva non è stato aperto, quindi le citazioni letterali di TUIR e DPR 600/1973 vanno ricontrollate prima dell'uso in specifica. I gestionali paghe esistenti non sono stati usati come riferimento.

## Domanda

Come rappresentare il tempo in un sistema paghe per Enti Locali in cui norme, contratti e atti hanno effetti retroattivi (rinnovi CCNL con arretrati, progressioni, atti tardivi, conguagli fiscali e previdenziali, UniEmens/ListaPosPA di periodi pregressi)? Valutare modelli bitemporali (valid time vs transaction time), ricalcolo per differenza, versioning delle regole, snapshot; esempi reali anche fuori dal payroll; limiti; implicazioni sulla tracciabilità.

## Sintesi

1. Il dominio non ha due assi temporali ma almeno quattro, e la normativa ne usa ciascuno per scopi diversi: **periodo di competenza** (a cui il diritto si riferisce), **data dell'atto/fonte** (firma CCNL o CCI, determina), **data di pagamento** (cassa, rilevante per il fisco), **data di conoscenza/registrazione** nel sistema. A questi si aggiunge la **versione dichiarata** verso terzi (ListaPosPA, CU, F24EP), che è immutabile una volta inviata.
2. Il modello bitemporale classico (valid time + transaction time, Snodgrass; SQL:2011; XTDB) copre bene competenza e conoscenza, ma da solo non basta: data dell'atto e data di pagamento sono attributi di dominio (non assi del database) che la norma usa come discriminanti.
3. Le correzioni retroattive vanno espresse come **differenza** (dovuto ricalcolato oggi per il periodo P meno quanto già pagato/dichiarato per P), registrata come nuovo fatto nel periodo di pagamento con riferimento al periodo di competenza. È il pattern "Difference Adjustment" calcolato con un "Parallel Model" (Fowler). Le stesse differenze però vanno **dichiarate** a INPS in forma di **sostituzione** del periodo (V1 causale 5): il modello deve saper produrre entrambe le viste.
4. Le **regole** (formule, aliquote, tabelle contrattuali) devono essere versionate per periodo di vigenza e ogni risultato deve registrare quale versione di regole e quali versioni dei fatti di input lo hanno prodotto. La bitemporalità dei dati non copre i cambi di codice/regole.
5. Gli **snapshot immutabili** sono necessari solo per ciò che è stato pagato o dichiarato a terzi (esiti di fatto); tutto il resto deve essere ricalcolabile.

## Findings

### A. Assi temporali richiesti dalle norme

A1. **Tassazione separata degli arretrati: conta il rapporto tra anno di competenza e anno di percezione, e la causa giuridica del ritardo.** L'art. 17, c. 1, lett. b) TUIR assoggetta a tassazione separata gli "emolumenti arretrati per prestazioni di lavoro dipendente riferibili ad anni precedenti, percepiti per effetto di leggi, di contratti collettivi, di sentenze o di atti amministrativi sopravvenuti o per altre cause non dipendenti dalla volontà delle parti". La Risoluzione AdE 151/E del 13/12/2017 precisa che in presenza di una delle cause giuridiche previste non va indagata la fisiologicità del ritardo; negli altri casi, se il ritardo è fisiologico, la tassazione separata non si applica.
- Marcatura: **norma certa** per l'esistenza e l'ambito della norma e per la risoluzione 151/E; testo letterale del TUIR **da verificare** su Normattiva.
- Fonti: https://www.agenziaentrate.gov.it/portale/documents/20143/302523/Risoluzione+n+151+del+13+dicembre+2017_RISOLUZIONE+N_151+DEL+13-12-2017.pdf/3fad92a8-5d48-a8cf-e2d7-2c94fed502c1 ; https://www.wikilabour.it/wp-content/uploads/2022/09/AdE_Interpello468-2022.pdf ; https://www.informazionefiscale.it/emolumenti-arretrati-tassazione-separata-istruzioni-risoluzione-agenzia-entrate
- Conseguenza: il modello deve conservare per ogni importo il periodo di competenza, la data di pagamento e **il titolo giuridico** (legge, CCNL, sentenza, atto) che ne ha causato la corresponsione tardiva. Il titolo è un dato, non un'etichetta descrittiva.

A2. **Principio di cassa allargata.** L'art. 51, c. 1 TUIR considera percepiti nel periodo d'imposta anche le somme "corrisposte dai datori di lavoro entro il giorno 12 del mese di gennaio del periodo d'imposta successivo a quello cui si riferiscono".
- Marcatura: **norma certa** (contenuto concorde in più fonti); testo letterale **da verificare** su Normattiva.
- Fonti: https://www.fiscal-focus.it/quotidiano/altre-tematiche/infoprofessioni/compenso-amministratori-il-principio-di-cassa-allargata,3,44882 ; https://fiscomania.com/principio-di-cassa-allargato/
- Conseguenza: l'imputazione fiscale è funzione di (data pagamento, periodo di riferimento), non della sola data di pagamento. Ulteriore conferma che competenza e cassa sono entrambi necessari.

A3. **Conguaglio fiscale di fine anno o cessazione.** L'art. 23 DPR 600/1973 disciplina il conguaglio tra ritenute operate e imposta dovuta, con termine riportato dalle fonti al 28 febbraio dell'anno successivo o alla cessazione se anteriore.
- Marcatura: **norma certa** per l'esistenza dell'istituto; termine e formulazione **da verificare** su testo vigente (letti solo in sintesi secondarie).
- Fonti: https://www.quotidianopiu.it/dettaglio/10788206/conguaglio-annuale-2023-novita-per-fringe-benefit-e-buoni-benzina
- Conseguenza: esiste un "periodo fiscale aperto" (anno d'imposta fino a chiusura conguaglio) e un "periodo chiuso" dopo il quale le correzioni cambiano natura. Lo stato aperto/chiuso di un periodo è un dato temporale da modellare.

A4. **CU: arretrati di anni precedenti per anno di competenza.** La CU ha una sezione dedicata agli emolumenti arretrati di anni precedenti soggetti a tassazione separata (punti 511 e seguenti secondo una fonte di software house, con suddivisione per anno di competenza).
- Marcatura: **da verificare** (numerazione dei punti letta solo in fonte secondaria; consultare le istruzioni ufficiali CU dell'anno).
- Fonte: https://passepartout.net/Resources/aggiornamenti-paghe/acred912.pdf ; https://www.mysolution.it/fisco/guide/guide-dichiarazioni/2025/certificazione-unica-2025---guida-alla-compilazione/oneri-deducibili-altri-dati-ritenute-a-titolo-dimposta-e-compensi-anni-precedenti

A5. **ListaPosPA: le correzioni di periodi pregressi sono sostituzioni integrali del periodo.** Il quadro V1 causale 5 serve a rettificare o sostituire periodi già denunciati: annulla i quadri E0/V1 dello stesso lavoratore per lo stesso periodo presso lo stesso datore. Il Messaggio INPS 749 del 20/02/2024 precisa la compilazione della sezione "Ente Versante" (importo e periodo di pagamento) nei V1 causale 5 per emolumenti corrisposti dopo la cessazione o durante la sospensione, e la circolare INPS 156 del 30/12/2025 considera, per il conguaglio 2025, gli elementi E0 e V1 causali 1, 5 e 7. Il periodo di un V1 causale 5 non può spezzare periodi già dichiarati in quadri V1 cumulativi.
- Marcatura: **norma certa** (prassi amministrativa vincolante INPS) per l'esistenza di V1 causale 5 e del messaggio 749/2024; le regole di dettaglio sul frazionamento dei periodi e il richiamo al messaggio 2791/2017 sono **da verificare** sul testo (letti in sintesi).
- Fonti: https://www.inps.it/content/dam/inps-site/it/scorporati/circolari-e-messaggi/2024/02/Circolare_14482/Allegati/14759_Messaggio-numero-749-del-20-02-2024.pdf ; https://www.inps.it/content/dam/inps-site/pdf/prestazioni-e-servizi/uniemens-enti-amministrazioni/937KEY-manuale_lista_pospa_v1-13_02_2018.pdf ; https://www.pensionifacili.it/circolare-numero-156-del-30-12-2025/
- Conseguenza chiave: verso INPS la correzione non è una differenza ma una **ridichiarazione completa** del periodo di competenza. Il modello deve quindi poter ricostruire "lo stato corretto completo del periodo P alla data di oggi", non solo il delta.

A6. **Contabilità armonizzata: l'impegno segue la data dell'atto, non la competenza economica del lavoratore.** Il principio contabile applicato 4/2 al D.Lgs. 118/2011, punto 5.2, prevede che per i rinnovi contrattuali l'impegno si registri "nell'esercizio in cui è firmato il contratto collettivo nazionale", anche per effetti retroattivi e oneri riflessi, salvo differimento degli effetti economici; per il trattamento accessorio e premiante, le somme liquidate nell'esercizio successivo sono stanziate e impegnate nell'esercizio di riferimento, e l'impegno nasce alla sottoscrizione della contrattazione integrativa.
- Marcatura: **norma certa** (estratto dell'allegato 4/2 pubblicato su governo.it); formulazione puntuale da ricontrollare sulla versione vigente dell'allegato (aggiornato più volte).
- Fonti: https://www.governo.it/sites/governo.it/files/76572-9653.pdf ; https://www.entionline.it/ita/RAGCC/2011_DLgs118_All4-2_Agg_settembre2021.pdf ; https://www.neopa.it/corretta-contabilizzazione-delle-spese-relative-al-trattamento-accessorio-e-premiante/
- Conseguenza: per la proposta di movimento contabile l'asse rilevante è la **data dell'atto fonte** (firma CCNL/CCI), distinta sia dalla competenza del lavoratore sia dalla data di pagamento. Un arretrato 2022-2024 di un CCNL firmato nel 2025 ha tre date diverse e ciascuna serve a un adempimento diverso.

A7. **Progressioni economiche: decorrenza fissata dall'atto, retroattiva rispetto alla graduatoria.** Secondo fonti di prassi, con il CCNL Funzioni Locali 16/11/2022 (art. 14) la decorrenza del differenziale stipendiale è il 1° gennaio dell'anno di sottoscrizione definitiva del CCI, con copertura sulle risorse stabili del fondo di quell'anno; per ARAN il requisito triennale si verifica alla data di decorrenza.
- Marcatura: **prassi-interpretazione** (fonti secondarie e atti di singoli enti; testo dell'art. 14 non riscontrato) - **da verificare** sul testo del CCNL e sugli orientamenti ARAN.
- Fonti: https://lentepubblica.it/personale-e-previdenza/progressioni-economiche-enti-locali-laran-chiarisce-i-differenziali-stipendiali/ ; https://comune.ballao.su.it/wp-content/uploads/2024/03/approvazione-graduatoria-progressione-economica.pdf
- Conseguenza: un fatto (progressione) noto a ottobre ha validità dal 1° gennaio: è il caso tipico bitemporale (valid time anteriore al transaction time). Inoltre i requisiti di ammissione si valutano "as of" una data passata: serve interrogare lo stato del personale com'era valido a quella data.

A8. **Prescrizione contributiva: il passato non è correggibile all'infinito.** L'art. 3, cc. 9-10, L. 335/1995 ha ridotto a cinque anni la prescrizione contributiva, applicabile anche alle gestioni pubbliche (circ. INPS 122/2019); il c. 10-bis (introdotto dal DL 4/2019) e successive proroghe hanno sospeso i termini per periodi pregressi delle gestioni esclusive; la circ. INPS 25/2020 indica che per periodi prescritti l'ente datore deve farsi carico dell'onere del trattamento di quiescenza. Il termine di sospensione vigente oggi non è stato accertato (ultima fonte trovata: circ. 58/2024).
- Marcatura: **norma certa** per art. 3 L. 335/1995 e circolari INPS 122/2019 e 25/2020; **da verificare** l'eventuale proroga oltre il 31/12/2024.
- Fonti: https://servizi2.inps.it/CircolariZIP/Circolare%20numero%20122%20del%2006-09-2019.pdf ; https://servizi2.inps.it/CircolariZIP/Circolare%20numero%2025%20del%2013-02-2020.pdf ; https://www.studiocerbone.com/?p=486176 ; https://senato.it/service/PDF/PDFServer/DF/441015.pdf
- Conseguenza: ogni periodo ha uno stato giuridico che cambia nel tempo (aperto, chiuso fiscalmente, prescritto); il ricalcolo deve sapere se una differenza è ancora dichiarabile/versabile o diventa un onere diverso.

### B. Modelli temporali: esempi reali e caratteristiche

B1. **Bitemporalità (valid time / transaction time).** Snodgrass formalizza tabelle a tempo di validità, a tempo di transazione e bitemporali in SQL standard, con vincoli di integrità e modifiche temporali dedicate.
- Marcatura: **prassi-interpretazione** (letteratura tecnica di riferimento).
- Fonte: https://smsf.cs.arizona.edu/~rts/tdbbook.pdf (copia dell'autore; disponibilità non verificata) ; https://shop.elsevier.com/books/developing-time-oriented-database-applications-in-sql/snodgrass/978-0-08-050422-3

B2. **Fowler, "Bitemporal History", usa proprio un esempio paghe**: aumento di stipendio con effetto 15 febbraio comunicato il 15 marzo, poi corretto il 5 aprile. "Actual history" registra come la storia avrebbe dovuto essere con informazione perfetta; "record history" registra come cambia la nostra conoscenza; il tempo effettivo è sempre minore o uguale al tempo di registrazione.
- Marcatura: **prassi-interpretazione**.
- Fonte: https://www.martinfowler.com/articles/bitemporal-history.html

B3. **SQL:2011** introduce tabelle temporali tramite definizioni di periodo (coppia di colonne inizio/fine): periodi di **system time** (tabelle system-versioned, cioè transaction time gestito dal DBMS) e di **application time** (valid time gestito dall'applicazione), combinabili in tabelle bitemporali.
- Marcatura: **prassi-interpretazione** (lo standard ISO/IEC 9075-2:2011 è a pagamento e non è stato consultato; si cita l'articolo degli autori IBM che hanno partecipato alla stesura).
- Fonte: Kulkarni, Michels, "Temporal features in SQL:2011", SIGMOD Record 41(3), 2012, DOI 10.1145/2380776.2380786 - https://sigmodrecord.org/2012/09/30/temporal-features-in-sql2011/

B4. **Supporto nei prodotti (stato da documentazione):**
- SQL Server: temporal tables = tabelle system-versioned (solo transaction time); il valid time va modellato con colonne applicative. **Prassi-interpretazione** (assenza di application-time dedotta, non dichiarata esplicitamente). https://learn.microsoft.com/en-us/sql/relational-databases/tables/temporal-tables
- MariaDB: system versioning + application-time periods (`FOR PORTION OF`, `WITHOUT OVERLAPS` dalla 10.5.3) combinabili in tabelle bitemporali. **Prassi-interpretazione** (documentazione di prodotto). https://mariadb.com/kb/en/application-time-periods ; https://mariadb.com/resources/blog/rewinding-time-in-mariadb-databases-system-versioning-and-application-time/
- PostgreSQL 18: chiavi primarie/uniche `WITHOUT OVERLAPS` e foreign key con `PERIOD` (vincoli su application time); nessun system versioning nativo. **Da verificare** sulle release notes ufficiali (letti solo in fonti secondarie). https://neon.com/postgresql/postgresql-18/temporal-constraints ; https://www.npgsql.org/efcore/release-notes/11.0.html
- XTDB: ogni tabella è bitemporale; valid time correggibile, system time immutabile; query `FOR VALID_TIME` e `FOR SYSTEM_TIME AS OF` per ricostruire cosa si sapeva a una data (uso di audit). **Prassi-interpretazione** (documentazione di prodotto). https://docs.xtdb.com/about/time-in-xtdb.html ; https://v1-docs.xtdb.com/concepts/bitemporality/

B5. **Contabilità: tre modi di correggere il passato (Fowler, Accounting Patterns).**
- *Replacement Adjustment*: cancella e riscrive; semplice ma distrugge la storia (inadatto se dall'importo è già derivato un pagamento).
- *Reversal Adjustment*: storno con segno opposto + nuova scrittura; adatto a registrazioni immutabili; triplica le scritture.
- *Difference Adjustment*: una sola scrittura con la differenza; leggibile, ma calcolarla senza duplicare la logica di calcolo è difficile; la soluzione suggerita è calcolare un *Parallel Model* corretto e confrontarlo con l'originale.
- Marcatura: **prassi-interpretazione** (materiale bozza dell'autore, non aggiornato).
- Fonti: https://martinfowler.com/eaaDev/ReplacementAdjustment.html ; https://martinfowler.com/eaaDev/ReversalAdjustment.html ; https://www.martinfowler.com/eaaDev/DifferenceAdjustment.html ; https://www.martinfowler.com/eaaDev/AccountingNarrative.html

B6. **Event sourcing e Retroactive Event.** Distingue eventi fuori ordine, eventi da respingere ed eventi errati; la correzione si ottiene ricostruendo lo stato da uno snapshot anteriore al punto di diramazione e rieseguendo gli eventi, oppure riavvolgendo; i Parallel Model calcolano stati alternativi da liste di eventi alternative. Fowler osserva che questi pattern sono molto difficili da aggiungere a posteriori a un sistema non nato event-sourced.
- Marcatura: **prassi-interpretazione**.
- Fonti: https://martinfowler.com/eaaDev/RetroactiveEvent.html ; https://martinfowler.com/eaaDev/EventSourcing.html

B7. **Bilancio (IFRS, IAS 8): correzione retroattiva vs prospettica.** Gli errori di periodi precedenti si correggono retroattivamente (restatement dei comparativi o dei saldi d'apertura), con limite di impraticabilità; i bilanci già approvati non si riscrivono, si ripresentano i comparativi. È l'analogo contabile di "correggo il valid time, ma il documento emesso resta".
- Marcatura: **prassi-interpretazione** per l'analogia; il contenuto di IAS 8 è **norma certa** in ambito IFRS (non applicabile agli enti locali), letto via Basis for Conclusions.
- Fonte: https://www.aasb.gov.au/admin/file/content105/c9/IAS8_BC_1-22.pdf

B8. **Assicurazioni (endorsement retroattivi).** Non è stata trovata una fonte primaria (standard di settore pubblico) che descriva il modello temporale delle polizze; si omette.
- Marcatura: **da verificare**.

## Trade-off

| Opzione | Cosa risolve | Limiti nel dominio |
|---|---|---|
| Solo storia di validità (valid time) | "Quanto spettava per marzo 2023" | Perde "cosa sapevamo quando abbiamo pagato marzo 2023": impossibile giustificare il pagato e calcolare la differenza in modo verificabile |
| Solo versioning di sistema (transaction time, es. temporal tables SQL Server) | Audit di ogni modifica | Non esprime retroattività: un aumento con effetto passato è indistinguibile da una correzione di errore |
| Bitemporale (SQL:2011 / XTDB / colonne applicative) | Competenza + conoscenza; "as-of" per ricostruire il pagato | Non copre data atto, data pagamento, stato del periodo (aperto/chiuso/prescritto), né i cambi di regole/codice. Query e vincoli più complessi; operazioni `FOR PORTION OF` spezzano righe |
| Ricalcolo per differenza (Parallel Model + Difference Adjustment) | Arretrati e conguagli come delta pagabili; una scrittura per periodo | Richiede di ricalcolare il periodo con conoscenza attuale e di disporre del "pagato" esatto; non basta per ListaPosPA che vuole la sostituzione integrale del periodo |
| Storno + riemissione (Reversal) | Immutabilità, leggibilità per periodo | Moltiplica i movimenti; in contabilità finanziaria uno storno di mandato emesso non è un'operazione neutra |
| Snapshot immutabili | Prova di cosa è stato pagato/dichiarato | Se usati per tutto, duplicano lo stato e diventano la fonte di verità al posto delle regole; vanno limitati agli esiti verso terzi |
| Event sourcing puro | Ricostruzione e "what-if" naturali | Costo di adozione elevato; il replay con regole cambiate produce risultati diversi da quelli pagati, quindi servono comunque snapshot degli esiti |

## Implicazioni per la mappa

1. **Concetti del dominio** (Not yet specified): oltre a fatti con validità, servono come concetti di primo livello almeno: *periodo di competenza*, *atto fonte con data di efficacia*, *pagamento* (data cassa), *dichiarazione inviata* (versione immutabile verso INPS/AdE/MEF), *stato del periodo* (aperto, chiuso fiscalmente, prescritto). **Prassi-interpretazione** derivata da A1-A8.
2. **Provenienza degli importi**: ogni importo dovrebbe registrare (periodo di competenza, data di conoscenza, versione delle regole, versioni dei fatti di input, atto fonte). Con questo la catena norma -> atto -> input -> importo è interrogabile "as of" qualsiasi data. **Prassi-interpretazione**.
3. **Calcolo**: proposta di funzione pura `dovuto(periodo, conoscenza_al, regole_vigenti_per_periodo)`; l'arretrato è `dovuto(P, oggi) - pagato(P)` dove `pagato` viene dagli esiti registrati e non da un ricalcolo. **Prassi-interpretazione** (Difference Adjustment + Parallel Model).
4. **Output obbligatori**: lo stesso ricalcolo deve produrre due viste: delta (per pagamento, ritenute, F24EP, contabilità) e stato completo del periodo (per V1 causale 5). **Norma certa** per il vincolo INPS (A5); la doppia vista è **prassi-interpretazione**.
5. **Proposte di movimento contabile**: l'esercizio di imputazione dipende dalla data dell'atto (A6), non dalla competenza del lavoratore: l'asse "data atto" non può essere ricavato dagli altri. **Norma certa** per il principio 4/2.
6. **Versioning delle regole**: le regole hanno una vigenza per periodo di competenza (tabelle contrattuali, aliquote) e alcune per periodo di pagamento (regime fiscale dell'anno di erogazione). Va specificato per ogni regola quale asse ne seleziona la versione. **Da verificare** caso per caso (es. aliquote contributive applicabili agli arretrati).
7. **Tracciabilità/AI**: l'interrogazione "cosa sapeva il sistema quando ha pagato" è la base per spiegare qualsiasi differenza a un revisore o per una verifica automatica. **Prassi-interpretazione**.

## Domande aperte

1. Per gli arretrati della gestione pubblica, i contributi si calcolano con aliquote e massimali del periodo di competenza o del periodo di pagamento, e con quale termine di versamento? Non trovata fonte primaria - **da verificare** su circolari INPS gestione dipendenti pubblici.
2. Testo vigente dell'art. 14 CCNL FL 16/11/2022 sulla decorrenza dei differenziali stipendiali e orientamenti ARAN - **da verificare**.
3. Stato attuale della sospensione della prescrizione contributiva per le gestioni esclusive dopo il 31/12/2024 - **da verificare**.
4. Regole per CU e 770 di correzione dopo l'invio (sostitutiva/annullamento) e loro impatto sul concetto di "dichiarazione inviata" - **da verificare**.
5. Il tempo di conoscenza deve coincidere con il tempo di registrazione nel database o con la data di protocollo/acquisizione dell'atto da parte dell'ente? Scelta di progetto da portare al grilling.
6. Fino a che punto il prototipo deve gestire il replay con regole cambiate (correzione di un errore di regola su periodi già pagati) rispetto al solo cambio dei fatti?
