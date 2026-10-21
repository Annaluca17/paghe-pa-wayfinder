# Fonti di norme e CCNL leggibili da software

Ticket: #4 (mappa #1). Ricerca del 21/10/2026.

## Legenda

- **norma certa**: affermazione verificata su fonte primaria (testo di legge o documento ufficiale dell'ente titolare della fonte).
- **prassi-interpretazione**: indicazione dell'ente titolare (pagine web, circolari, guide) o lettura consolidata, non norma di legge.
- **da verificare**: rilevata da estratti di pagine ufficiali o da fonti secondarie, non confermata con lettura integrale della fonte primaria.

### Limite di metodo dichiarato

Dall'ambiente di ricerca i domini istituzionali italiani (normattiva.it, dati.normattiva.it, inps.it, aranagenzia.it, finanze.gov.it, ipzs.it) **non erano raggiungibili** in lettura diretta (errore DNS/proxy). Le informazioni sono state ricavate dagli estratti indicizzati delle pagine ufficiali tramite motore di ricerca e, dove indicato, da fonti secondarie. Per questo motivo gran parte dei punti tecnici (endpoint, licenze, formati) resta marcata **da verificare**: vanno confermati aprendo i documenti ufficiali linkati prima di progettarci sopra. Nessun endpoint, tracciato o riferimento normativo e' stato ricostruito a memoria.

## Domanda

Esistono fonti machine-readable per norme e contratti rilevanti per le paghe degli Enti Locali (Normattiva, Gazzetta Ufficiale, ARAN, INPS, Agenzia delle Entrate, MEF/RGS)? Con quale formato, licenza, frequenza di aggiornamento e stabilita'? Quali parametri (aliquote, soglie, scaglioni, massimali, tabelle stipendiali CCNL) sono pubblicati in forma strutturata e quali solo testuale? Che cosa implica per un modello con regole normative espresse come codice e tracciabilita' verso la fonte?

## Sintesi

1. Il **testo** delle norme statali e' disponibile in forma strutturata: Normattiva ha un portale open data (dati.normattiva.it) con API e download in Akoma Ntoso, XML NIR, JSON, HTML, URI ELI; licenza CC BY 4.0 dichiarata su tutti gli atti dal 1/1/2026. Questo da' **identificatori stabili e versioni alla data** (multivigenza), non parametri.
2. I **parametri numerici** (aliquote, scaglioni, soglie, massimali, minimali) restano quasi sempre **dentro il testo**: articoli di legge, circolari INPS, provvedimenti AdE, tabelle allegate ai CCNL in PDF. Non e' stata trovata alcuna fonte ufficiale che pubblichi aliquote contributive, scaglioni IRPEF o tabelle stipendiali CCNL Funzioni Locali come dataset.
3. Eccezione rilevante: le **addizionali comunali IRPEF** sono pubblicate dal MEF - Dipartimento Finanze in un elenco generale aggiornato quotidianamente, indicato come scaricabile in CSV.
4. I **formati degli adempimenti** (UniEmens/ListaPosPA, CU, 770) sono strutturati (XSD, tracciati record), ma descrivono l'output, non le regole di calcolo.
5. Implicazione: il modello deve mantenere un proprio **registro dei parametri normativi**, trascritti da fonte testuale, ciascuno ancorato a un identificatore di fonte (URN NIR/ELI + articolo + data di vigenza, oppure numero/data di circolare o provvedimento), con controllo a quattro occhi sulla trascrizione.

## Findings per fonte

### 1. Normattiva (IPZS / Presidenza del Consiglio)

- Esiste un portale open data dedicato, composto da un portale web e da un insieme di API, che rende disponibili gli atti in versione originaria, vigente a una data e multivigente. **da verificare** (estratti di https://dati.normattiva.it/Il-progetto e https://dati.normattiva.it/ ; comunicato IPZS https://www.ipzs.it/news/comunicati-stampa/normattiva-al-via-il-portale-open-data).
- Formati di download: AKN (Akoma Ntoso / OASIS LegalDocML), XML NIR (Normeinrete, standard AgID), JSON, HTML, URI ELI; PDF ed EPUB solo per le collezioni preconfezionate (RTF citato per la consultazione). Due modalita': collezioni preconfezionate e collezioni calcolate "su richiesta" da parametri di ricerca. **da verificare** (https://dati.normattiva.it/Come-scaricare-i-dati).
- Specifica API ufficiale in PDF "Normattiva Specifiche API Open Data" (MDL-ITSMS-00-GEN): ricerca semplice, ricerca avanzata, dettaglio per URN, ricerca con FacetMap, ricerca asincrona, richiesta delle tipologie di formati di esportazione; changelog con revisioni successive (aggiunta parametri anno/mese/giorno/numero nella ricerca avanzata). Base URL indicati negli estratti: produzione `https://api.normattiva.it/t/normattiva.api`, collaudo `https://pre.api.normattiva.it/t/normattiva.api`. Il portale dichiara specifica in formato OpenAPI e file Postman. **da verificare** (https://dati.normattiva.it/assets/come_fare_per/API_Normattiva_OpenData.pdf ; https://dati.normattiva.it/assets/come_fare_per/Normattiva%20OpenData.html).
- Licenza: fase sperimentale iniziale CC BY 4.0 NC; dal 1/7/2025 al 31/12/2025 CC BY 4.0 con funzionalita' limitate; dal 1/1/2026 CC BY 4.0 per tutti gli atti in versione originaria, vigente e multivigente. **da verificare** (https://dati.normattiva.it/Dati-disponibili ; thread https://forum.italia.it/t/normattiva-open-data/536).
- Documentazione sulla strutturazione degli atti in Akoma Ntoso e sull'implementazione ELI in Italia. **da verificare** (https://dati.normattiva.it/assets/come_fare_per/Portale_Normattiva_2.0-Strutturazione_degli_atti_in_Akoma_Ntoso_26-07-2021.pdf ; https://dati.normattiva.it/assets/come_fare_per/ELI_implementation_in_Italy.pdf).
- Frequenza di aggiornamento: l'aggiornamento del testo vigente e' garantito "di norma, entro tre giorni dalla data di pubblicazione dell'atto aggiornante"; una notizia 2023 del portale indica fino a 15 giorni in caso di numero rilevante di modifiche e caricamento dell'atto entro un'ora dalla pubblicazione in GU. **prassi-interpretazione** (impegno editoriale del gestore, non norma) (https://www.normattiva.it/staticPage/guidaAllUso_RegoleAggiornamento ; https://www.normattiva.it/showArchivioNews?anno=2023).
- Valore giuridico: il testo Normattiva non sostituisce la Gazzetta Ufficiale, che prevale in caso di discordanza. **da verificare** nella formulazione esatta delle note legali del portale (avviso riportato in https://github.com/ondata/normattiva_2_md ; definizione di "testo vigente" in https://www.normattiva.it/staticPage/guidaAllUso_RegoleAggiornamento).
- Indirizzamento stabile per URN NIR, anche a livello di articolo, es. TUIR art. 11 (scaglioni IRPEF): `https://www.normattiva.it/uri-res/N2Ls?urn:nir:presidente.repubblica:decreto:1986-12-22;917~art11`. Il pattern `uri-res/N2Ls?urn:nir:...~artN` e' **prassi-interpretazione** (usato dal portale e documentato da strumenti di terzi: https://github.com/ondata/normattiva_2_md). Che gli scaglioni IRPEF siano nell'art. 11 TUIR (DPR 917/1986) e' **norma certa**.
- Esiste anche un export AKN per singolo atto con parametri `dataGU`, `codiceRedaz`, `dataVigenza` (es. `https://www.normattiva.it/do/atto/caricaAKN?dataGU=20050307&codiceRedaz=005G0104&dataVigenza=20251101`). **da verificare**: e' documentato solo da uno strumento di terzi, non e' un'API dichiarata stabile (https://github.com/ondata/normattiva_2_md).
- Stabilita': il PDF di specifica ha revisioni successive e un ambiente di collaudo; endpoint e parametri sono cambiati tra versioni. **da verificare**; implicazione: non accoppiare il modello a un endpoint, ma a identificatori (URN/ELI) e a snapshot scaricati.

### 2. Gazzetta Ufficiale (IPZS)

- La GU usa ELI dal 2015 (es. `https://www.gazzettaufficiale.it/eli/gu/2025/12/27/299/sg/pdf`); edizione PDF certificata dal 2009; archivio PDF dal 1861. **da verificare** (Publications Office UE: https://op.europa.eu/en/web/forum/italy-oj2).
- Non e' stata trovata un'API o un servizio open data di dati strutturati della GU distinto da Normattiva. **da verificare** (assenza di evidenza, non evidenza di assenza).

### 3. ARAN e CNEL (CCNL e contratti integrativi)

- I CCNL del comparto Funzioni Locali sono pubblicati sul sito ARAN nella sezione contratti del comparto; le fonti trovate rimandano a documenti PDF. **da verificare** il formato degli allegati tabellari (https://www.aranagenzia.it/contrattazione/comparti/comparto-delle-funzioni-locali/contratti.html).
- **Non e' stata trovata** alcuna pubblicazione ufficiale delle tabelle stipendiali (tabellare, posizioni economiche, indennita') del CCNL Funzioni Locali in formato strutturato (CSV/XLSX/JSON/API). Le tabelle vivono negli allegati del contratto. **da verificare** con ARAN.
- Banca dati dei contratti integrativi (ARAN-CNEL) su https://www.contrattintegrativipa.it/ci/ , alimentata dalle amministrazioni (procedura congiunta attiva dal 1/10/2015); ARAN la presenta come consultabile in logica open data, con estrazione per amministrazione, territorio, anno; la pagina di ricerca mostra una scheda "OPEN DATA". Formato e licenza dell'export **non trovati**; i documenti per singolo contratto sono PDF. **da verificare** (https://www.aranagenzia.it/comunicati/8426-banca-dati-contratti-integrativi-comunicazione-a-tutte-le-pubbliche-amministrazioni.html ; https://www.cnel.it/archivio-contratti/entra-nell-archivio/contratti-collettivi-del-settore-pubblico/banca-dati-aran-cnel---contratti-integrativi).
- La pubblicazione dei contratti integrativi da parte delle PA e' richiamata in relazione all'art. 9-bis d.lgs. 33/2013. **da verificare** il nesso esatto (pagina ARAN https://www.aranagenzia.it/amministrazione-trasparente/personale/contrattazione-integrativa/contratti-integrativi.html).
- L'Archivio nazionale dei contratti del CNEL offrirebbe cartelle in formato elaborabile (Excel) con metadati dei CCNL (codici, settori), non i contenuti economici. **da verificare** (fonte secondaria: https://www.testo-unico-sicurezza.com/archivio-nazionale-dei-contratti-collettivi-di-lavoro.html).

### 4. INPS

- Portale Open Data con catalogo conforme DCAT-AP_IT, esposizione LOD/RDF e SDMX per gli osservatori statistici; licenza indicata nella scheda di ciascun dataset (non unica). **da verificare** (https://www.inps.it/dati-ricerche-e-bilanci/open-data ; https://www.inps.it/dati-ricerche-e-bilanci/open-data/informazioni/come-si-usano). Storicamente (2013) formati Excel/CSV/XML e licenza IODL 2.0 (fonte secondaria datata: https://www.corrierecomunicazioni.it/pa-digitale/l-inps-spinge-sugli-open-data/).
- Gli open data INPS sono statistici (osservatori), **non** parametri di calcolo: non e' stato trovato un dataset di aliquote contributive, massimali o minimali. **da verificare**.
- I parametri annui (minimale giornaliero, massimale ex art. 2 c. 18 L. 335/1995, soglie di accredito) sono pubblicati con circolare annuale; per il 2026 la circolare n. 6 del 30/01/2026, valida per dipendenti pubblici e privati. Pubblicazione in HTML/PDF con allegati tabellari in PDF. **prassi-interpretazione** (circolare = atto di prassi) / formato **da verificare** (notizia INPS: https://www.inps.it/it/it/inps-comunica/notizie/dettaglio-news-page.news.2026.02.lavoratori-dipendenti-limite-minimo-di-retribuzione-giornaliera-2026.html ; allegato riprodotto da terzi: https://ascom.bo.it/wp-content/uploads/2026/02/Allegato-1-CIRCO-23-26_Circolare-INPS-n.-6-del-30-01-2026.pdf).
- Circolari e messaggi INPS: non e' stata trovata API o feed strutturato ufficiale; consultazione via sito. **da verificare**.
- UniEmens / ListaPosPA: documento tecnico (Allegato tecnico) versionato e schemi XSD; versione 4.32.2 riportata come pubblicata a giugno 2026; manuale operativo ListaPosPA v1.0 del 13/02/2018. Strutturato per il **tracciato**, con tabelle codici in appendice. **da verificare** (https://www.quotidianopiu.it/dettaglio/15890154/uniemens-nuovo-aggiornamento-dellallegato-tecnico ; https://www.inps.it/content/dam/inps-site/pdf/prestazioni-e-servizi/uniemens-enti-amministrazioni/937KEY-manuale_lista_pospa_v1-13_02_2018.pdf).

### 5. Agenzia delle Entrate

- Modelli CU e relative specifiche tecniche di trasmissione approvati annualmente con provvedimento del Direttore (CU 2026: provv. n. 15707/2026 del 15/01/2026, secondo fonti secondarie), pubblicati in PDF con tracciati record a lunghezza fissa. **da verificare** il numero sul sito AdE (fonte secondaria: https://www.fiscoetasse.com/files/21140/provvedimento-cu-2026.pdf).
- Tabelle di codici (codici tributo F24) consultabili tramite motore di ricerca sul sito AdE; **non trovato** un dataset scaricabile ufficiale. **da verificare** (fonti secondarie: https://www.informazionefiscale.it/Codici-tributo-modello-F24-piu-comuni).
- Aliquote, scaglioni e detrazioni IRPEF non sono pubblicati da AdE come dataset: stanno nel TUIR (artt. 11, 13) e nelle istruzioni ai modelli in PDF. **norma certa** per la collocazione nel TUIR; **da verificare** l'assenza di dataset.

### 6. MEF - Dipartimento Finanze, RGS, NoiPA

- Addizionale comunale IRPEF: "Elenchi generali aggiornati quotidianamente", per anno d'imposta, con codice catastale, comune, aliquota (unica o per scaglioni), esenzione, estremi della delibera e data di pubblicazione; formato indicato come CSV; il valore `0*` segnala delibera non ancora adottata. Esistono anche elenchi annuali in PDF. **da verificare** il formato attuale (https://www.finanze.gov.it/it/fiscalita/fiscalita-regionale-e-locale/Addizionale-comunale-allIRPEF/aliquote-applicabili/Elenchi-generali-aggiornati-quotidianamente/ ; https://www1.finanze.gov.it/finanze2/dipartimentopolitichefiscali/fiscalitalocale/nuova_addcomirpef/download/tabella.htm ; PDF: https://www.finanze.gov.it/export/sites/finanze/.galleries/Documenti/Fiscalita-locale/Elenco-annuale-addizionale-comunale-IRPEF-2025-26-gennaio-2026-1.pdf).
- La fonte giuridica dell'aliquota comunale resta la **delibera** del comune; l'elenco MEF ne e' la pubblicazione. Limite dello 0,8% salvo deroghe: **norma certa** nel d.lgs. 360/1998 art. 1 (https://www.normattiva.it/uri-res/N2Ls?urn:nir:stato:decreto.legislativo:1998-09-28;360~art1), da rileggere per le deroghe vigenti.
- Addizionale regionale: pagine per regione su finanze.gov.it (es. `addregirpef.php?reg=06`), HTML; formato scaricabile **non trovato**. **da verificare** (https://www1.finanze.gov.it/finanze2/dipartimentopolitichefiscali/fiscalitalocale/addregirpef/addregirpef.php?reg=06).
- Conto Annuale RGS: dataset nazionale open data **non verificato**; diversi comuni ripubblicano le proprie tabelle in CSV con licenza CC BY 4.0 (es. https://dati.comune.genova.it/en/dataset/conto-annuale-del-personale-2015-2016-2017-2018). Sono dati di output, non parametri. **da verificare**.
- NoiPA Open Data (MEF): dati aggregati sul personale gestito da NoiPA, modello LOD, presente su dati.gov.it; non contiene parametri normativi. Licenza/formati **da verificare** (https://www.pmi.it/?p=280177).

## Classificazione dei parametri

| Parametro | Fonte giuridica | Pubblicazione strutturata trovata | Stato |
|---|---|---|---|
| Testo norme statali, versioni alla data | Leggi/decreti in GU | Si: Normattiva AKN/NIR/JSON + API | da verificare (endpoint/licenza) |
| Scaglioni e aliquote IRPEF | TUIR art. 11 | Solo come testo strutturato per articolo/comma (AKN), non come numeri | norma certa (collocazione) |
| Detrazioni lavoro dipendente | TUIR art. 13 | Idem | norma certa (collocazione) |
| Addizionale comunale IRPEF | Delibere comunali, d.lgs. 360/1998 | Si: elenco MEF (CSV indicato), aggiornamento quotidiano | da verificare (formato) |
| Addizionale regionale IRPEF | Leggi regionali | Pagine HTML MEF per regione | da verificare |
| Aliquote contributive ex INPDAP (CPDEL, TFS/TFR, ecc.) | Leggi e circolari INPS | Non trovata | da verificare |
| Massimale/minimale contributivo annuo | L. 335/1995 + circolare annua INPS | Solo circolare (HTML/PDF) | prassi-interpretazione |
| Tabellare e progressioni CCNL Funzioni Locali | CCNL ARAN | Solo allegati PDF | da verificare |
| Fondo risorse decentrate, contratti integrativi | CCNL + CCI | PDF in banca dati ARAN-CNEL; export open data di formato ignoto | da verificare |
| Codici tributo F24 | Risoluzioni AdE | Ricerca online, nessun dataset trovato | da verificare |
| Tracciati UniEmens/ListaPosPA | Documento tecnico INPS | Si: XSD + allegato tecnico versionato | da verificare |
| Tracciati CU/770 | Provvedimenti AdE | Tracciati record in PDF | da verificare |

## Trade-off

- **Usare Normattiva come ancora di tracciabilita'** (URN/ELI + data di vigenza) e' praticabile e a licenza aperta; ma il testo Normattiva non e' ufficiale (prevale la GU) e l'aggiornamento puo' tardare di giorni rispetto alla pubblicazione. Per un parametro che entra in vigore il giorno dopo la GU serve poter citare direttamente l'URL ELI della GU.
- **Accoppiarsi alle API** consente automazione (rilevare modifiche a un articolo citato), ma la specifica e' giovane e ha gia' cambiato parametri; meglio snapshot periodici versionati.
- **Trascrivere i parametri a mano** dalle fonti testuali e' inevitabile per la maggior parte dei valori, con rischio di errore: richiede doppio controllo e test sui valori.
- **Dati MEF sulle addizionali** sono automatizzabili, ma riflettono le delibere con ritardo e con convenzioni proprie (`0*`): il dato giuridico resta la delibera.
- **Rules as Code** (es. OpenFisca, Catala) mostra che codificare norme e' fattibile, ma l'esperienza canadese rileva che e' difficile catturare tutto il significato di una norma in un linguaggio imperativo. **prassi-interpretazione** (https://www.microsoft.com/en-us/research/publication/catala-a-programming-language-for-the-law/ ; https://oecd-opsi.org/wp-content/uploads/2024/04/Rules-as-Code-in-Canada.pdf).

## Implicazioni per il modello

1. Separare **regole** (logica di calcolo, codice versionato) da **parametri** (valori con periodo di validita'), entrambi con riferimento di fonte obbligatorio.
2. Ogni parametro porta: valore, unita', validita' dal/al, tipo fonte (legge, circolare, provvedimento, CCNL, delibera), identificatore (URN NIR o ELI + articolo/comma; numero e data di circolare/messaggio; estremi CCNL e articolo/tabella; delibera comunale), URL, data di acquisizione, chi ha trascritto, chi ha validato, marcatura (norma certa / prassi / da verificare).
3. Le fonti di prassi (circolari INPS, risoluzioni AdE) vanno modellate come livello distinto dalla norma: spesso sono loro a fissare il numero (massimale annuo), ma la base resta la legge.
4. Le tabelle CCNL vanno digitalizzate dal progetto stesso (non esiste fonte strutturata trovata): e' un costo fisso a ogni rinnovo, da prevedere come attivita' con verifica.
5. Unico parametro con alimentazione automatica realistica: addizionale comunale (MEF). Per il resto: sorveglianza (Normattiva multivigente, news INPS/AdE) e trascrizione assistita, ruolo possibile per l'AI con conferma umana.
6. Snapshot dei testi Normattiva (AKN) alla data di vigenza usata, conservati con hash, per rendere riproducibile la catena norma -> importo anche se il portale cambia.
7. I formati degli adempimenti (XSD UniEmens, tracciati CU/770) sono contratti di output: vanno versionati come le regole.

## Domande aperte

- Contenuto esatto, stabilita' e limiti d'uso (quote, autenticazione) dell'API Normattiva: serve lettura diretta del PDF/OpenAPI.
- La licenza CC BY 4.0 dal 1/1/2026 e' effettivamente in vigore e copre anche l'uso via API? Conferma sulla pagina "Dati disponibili".
- ARAN pubblica (o intende pubblicare) le tabelle stipendiali CCNL in formato strutturato? Che cosa contiene l'export "OPEN DATA" di contrattintegrativipa.it?
- Esiste un dataset ufficiale INPS (o un'appendice strutturata del documento tecnico UniEmens) con aliquote della gestione dipendenti pubblici?
- Formato attuale (CSV) e tracciato dell'elenco MEF addizionale comunale, e disponibilita' analoga per le addizionali regionali.
- Le leggi regionali (addizionale regionale) sono coperte da Normattiva open data o vanno prese dai BUR regionali?
