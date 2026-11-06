# Fabbisogno dati degli adempimenti non stipendiali

Ticket: #10 (mappa #1). Data ricerca: 21/10/2026.

## Domanda

Quali dati richiedono Conto Annuale (SICO), PIAO e gli altri adempimenti sul personale di un Ente Locale non strettamente stipendiali (trasparenza, GEDAP, Perla PA, anagrafe delle prestazioni, monitoraggio della spesa di personale e dei limiti, relazioni sul fondo risorse decentrate)? Per ciascun dato: fonte originaria (giuridico, presenze, paghe, contabilità), granularità, periodicità. Obiettivo: requisiti del modello dati affinché tutto si estragga senza reinserimenti.

## Avvertenza sul metodo

- Legenda: **norma certa** = obbligo con riferimento normativo riportato in modo concorde da fonti istituzionali; **prassi-interpretazione** = modalità operative, circolari, orientamenti della Corte dei conti o prassi degli enti; **da verificare** = non confermato su fonte primaria.
- In questa sessione l'accesso diretto a normattiva.it, rgs.mef.gov.it, funzionepubblica.gov.it e perlapa.gov.it era bloccato dal proxy di rete (HTTP 403 / DNS). Le verifiche sono state fatte tramite motore di ricerca, su documenti istituzionali (circolari RGS, note DFP, pagine "Amministrazione trasparente" di enti) che riportano il testo o l'URL della fonte primaria. Per questo **nessun tracciato tecnico** (campi, codici voce SICO, formati Perla PA) è riportato come certo: va riletto sulle fonti primarie indicate.
- Le colonne "fonte originaria" e "granularità" sono un'analisi del ricercatore (dove nasce il dato nel ciclo dell'ente), non un contenuto delle norme: vanno lette come **prassi-interpretazione**.

## Sintesi

1. Gli adempimenti non stipendiali chiedono quasi sempre **aggregati** (conteggi, giorni, importi) ma con **chiavi di disaggregazione diverse** tra loro: qualifica/categoria contrattuale, genere, tempo pieno/parziale, ufficio dirigenziale, tipologia di rapporto, causale di assenza, fascia d'età, anzianità, titolo di studio, voce di costo, fonte di finanziamento del fondo. Il modello deve quindi conservare il dato elementare (evento datato, per persona) e le dimensioni, non report precotti.
2. Il Conto Annuale (art. 60 d.lgs. 165/2001; rilevazione 2025 con circolare RGS n. 12 del 26/06/2026, termine 25/07/2026) è l'adempimento più esigente: consistenze al 31/12, flussi (assunzioni/cessazioni), lavoro flessibile in unità-anno, giorni di assenza per causale, spesa per retribuzioni e accessori per qualifica, altri oneri, fondo e SICI, riconciliazione con la contabilità. Molti altri adempimenti (trasparenza art. 16 e 21, PIAO 3.3) **riusano** le sue tabelle.
3. Dal 2025 (rilevazione 2025) la Scheda informativa 1 chiede per le Funzioni Locali le **FTE che hanno percepito accessorio** (Tabella 13) e c'è una nuova **Scheda A33** per le facoltà assunzionali: due dati che obbligano a legare importo accessorio, persona e frazione di tempo lavorato.
4. Le presenze sono la fonte più trasversale: tassi di assenza trimestrali per ufficio (trasparenza), giorni di assenza annui per causale (Conto Annuale), permessi L. 104 annui per beneficiario (Perla PA), permessi sindacali (GEDAP, entro 2 giorni lavorativi dall'autorizzazione), adesioni agli scioperi (GEPAS, il giorno stesso).
5. Il giuridico alimenta consistenze, inquadramenti, ufficio di assegnazione, incarichi extra-istituzionali (anagrafe delle prestazioni, entro 15 giorni) e deleghe sindacali (rilevazione ARAN).
6. Contabilità e paghe alimentano i limiti di spesa (rapporto spesa di personale/entrate correnti ex art. 33 c. 2 d.l. 34/2019; tetto accessorio art. 23 c. 2 d.lgs. 75/2017; limiti storici c. 557/562 L. 296/2006, che secondo stampa specializzata sarebbero stati superati dal d.l. 144/2026: **da verificare** la conversione). Questi limiti si calcolano su **impegni di competenza** e su aggregati di bilancio, non sul pagato in busta: serve un ponte persona/voce -> impegno/capitolo.
7. Le relazioni illustrativa e tecnico-finanziaria del contratto integrativo (art. 40 c. 3-sexies d.lgs. 165/2001; schemi circolare RGS n. 25/2012) richiedono la costituzione del fondo per sezione (risorse stabili, variabili, decurtazioni) e la destinazione per istituto: il fondo è un oggetto del modello, non una somma di voci.

## Elenco adempimenti e dati richiesti

### A. Conto Annuale (SICO) - RGS

- **norma certa**: rilevazione prevista dal Titolo V e dall'art. 60 d.lgs. 165/2001; il richiamo all'art. 60 c. 2 è anche nell'art. 16 d.lgs. 33/2013. Fonte: https://documenti.camera.it/_dati/leg17/lavori/documentiparlamentari/indiceetesti/047/001_RS/00000022.pdf
- **norma certa / prassi**: rilevazione 2024 con circolare RGS n. 18 del 19/06/2025, termine 15/07/2025 https://www.rgs.mef.gov.it/_Documenti/VERSIONE-I/CIRCOLARI/2025/18/Circolare-del-19-giugno-2025-n-18.pdf ; rilevazione 2025 con circolare RGS n. 12 del 26/06/2026, termine 25/07/2026, invio in SICO via web o kit Excel https://www.rgs.mef.gov.it/_Documenti/VERSIONE-I/CIRCOLARI/2026/12/Allegato-alla-Circolare-del-26-giugno-2026-n-12.pdf (sintesi: https://www.neopa.it/conto-annuale-2025-pubblicata-la-circolare-della-rgs/ , https://www.ilpersonale.it/la-circolare-n-12-del-26-giugno-2026-sul-conto-annuale-2025/ )
- **prassi-interpretazione**: novità 2024: in Tabella 11 la causale "malattia retribuita" è divisa tra assenze soggette e non soggette a trattenuta (ricovero, terapie, infortunio); Tabella 15 e SICI allineate ai nuovi CCNL https://www.neopa.it/conto-annuale-2024-pubblicata-la-circolare-della-rgs/
- **prassi-interpretazione**: novità 2025: in Scheda informativa 1 le Funzioni Locali indicano le unità in FTE che hanno percepito il salario accessorio di Tabella 13; nuova Scheda A33 (comuni, province, città metropolitane, regioni) per le facoltà assunzionali; istruzioni sull'incremento del fondo ex art. 14 c. 1-bis d.l. 25/2025 https://www.neopa.it/conto-annuale-2025-pubblicata-la-circolare-della-rgs/ , https://www.lagazzettadeglientilocali.it/fondo-risorse-decentrate-la-circolare-della-ragioneria-generale-dello-stato-con-le-istruzioni/
- **da verificare**: numerazione e contenuto esatto delle tabelle 3-10 (comandi/distacchi, assunzioni, cessazioni, passaggi, classi di età, anzianità, titolo di studio). Da fonti secondarie risulta: Tab. 1 personale a tempo indeterminato al 31/12; Tab. 2 e 2A personale flessibile; Tab. 3 usata per le correzioni per comandi e distacchi nel calcolo dei presenti; Tab. 12 retribuzioni, Tab. 13 accessori, Tab. 14 altri oneri (costo del lavoro = 12+13+14); Tab. 15 fondo per la contrattazione integrativa; scheda di riconciliazione. https://service.agcm.it/dotcmsdoc/trasparenza/CONTO_ANNUALE_AGCM_2022_(dati_31-12-2021).pdf , https://www.unito.it/sites/default/files/conto_annuale_2023.pdf , https://portale.fnomceo.it/wp-content/uploads/2024/07/COM-N-84.pdf

| Dato | Fonte originaria | Granularità richiesta | Periodicità | Riferimento |
|---|---|---|---|---|
| Personale in servizio al 31/12 (tempo indeterminato, dirigenti, segretario) | Giuridico | Conteggio per qualifica/posizione economica, genere, tempo pieno/part-time | Annuale (anno precedente) | Tab. 1; art. 60 d.lgs. 165/2001 (**norma certa** l'obbligo; dettaglio colonne **da verificare**) |
| Personale flessibile (tempo determinato, formazione lavoro, somministrazione, LSU, co.co.co.) | Giuridico + presenze (periodi di servizio) | Unità-anno o mesi per tipologia, qualifica, genere | Annuale | Tab. 2/2A (**da verificare** unità di misura e tipologie) |
| Comandi, distacchi, convenzioni in entrata/uscita | Giuridico | Conteggio per qualifica, ente di provenienza/destinazione | Annuale | Tab. 3 (**da verificare**) |
| Assunzioni e cessazioni per causa | Giuridico | Conteggio per qualifica, genere, causa (concorso, mobilità, pensione, dimissioni...) | Annuale | Tabelle di flusso (**da verificare** numerazione) |
| Passaggi di qualifica / progressioni | Giuridico | Conteggio per qualifica di partenza e di arrivo | Annuale | **da verificare** |
| Classi di età, anzianità di servizio, titolo di studio | Giuridico (anagrafe, carriera, titoli) | Conteggio per classe, qualifica, genere | Annuale | Tab. 7-9 (**da verificare**) |
| Giorni di assenza per causale (ferie, malattia soggetta/non soggetta a trattenuta, L. 104, maternità, sindacali, sciopero, formazione, lavoro agile...) | Presenze | Giorni per causale, qualifica, genere | Annuale | Tab. 11 (**prassi-interpretazione** novità 2024; elenco causali **da verificare**) |
| Retribuzioni fisse (stipendio, RIA, tredicesima, arretrati) | Paghe | Importi annui e mensilità per qualifica | Annuale | Tab. 12 (**prassi-interpretazione**) |
| Indennità e compensi accessori per voce | Paghe (+ fondo) | Importi per voce SICO e qualifica; FTE percettori (dal 2025) | Annuale | Tab. 13 + SI1 (**prassi-interpretazione**) |
| Altri oneri (contributi a carico ente, IRAP, buoni pasto, formazione, welfare, somme a personale esterno) | Paghe + contabilità | Importi per voce | Annuale | Tab. 14 (**prassi-interpretazione**; elenco voci **da verificare**) |
| Costituzione e destinazione del fondo risorse decentrate (comparto, dirigenza, segretari) | Fondo (atti) + contabilità | Importi per voce di costituzione e destinazione | Annuale | Tab. 15 + SICI (**prassi-interpretazione**) |
| Riconciliazione spesa rilevata / dati contabili | Contabilità | Importi per aggregato contabile | Annuale | Scheda di riconciliazione (**da verificare** se con SIOPE o con rendiconto) |
| Dati per facoltà assunzionali (Scheda A33) | Contabilità + giuridico | Importi e consistenze ente | Annuale (dal 2025) | **prassi-interpretazione**; contenuto **da verificare** |

### B. PIAO - sezione 3 Organizzazione e capitale umano

- **norma certa**: art. 6 d.l. 80/2021; DPR 81/2022; DM 30/06/2022 n. 132 (schema tipo). Art. 6 DM: modalità semplificate per enti con meno di 50 dipendenti (sezione 1, sottosezione 2.3, sezione 3 con 3.1 struttura organizzativa, 3.2 lavoro agile, 3.3 fabbisogni). Art. 7 DM: approvazione entro il 31 gennaio, durata triennale. https://irpet.it/wp-content/uploads/2023/06/direttore_12_31-03-2023_all-a-piao_2023.pdf , https://www.comunemalcesine.it/media/978/piao-2022-2024.pdf
- **prassi-interpretazione**: la sottosezione 3.3 contiene la consistenza di personale al 31/12 dell'anno precedente per inquadramento professionale, capacità assunzionale, cessazioni previste, modalità di copertura, formazione, eventuali eccedenze (art. 4 c. 1 lett. c DM 132/2022 come letto da commentatori). https://www.segretaricomunalivighenzi.it/01-03-2023-il-piao-visto-dallanci-scadenza-al-30-maggio-per-tutti-obiettivi-provvisori-e-conferma-della-duplicazione-col-dup-per-i-fabbisogni-di-personale/ ; testo dell'art. 4 **da verificare** su GU.
- **da verificare**: eventuali nuove linee guida DFP sul PIAO successive al 2023 e la persistenza delle linee guida fabbisogni DM 8/5/2018.

| Dato | Fonte originaria | Granularità | Periodicità | Riferimento |
|---|---|---|---|---|
| Consistenza al 31/12 per inquadramento (area/profilo) | Giuridico | Conteggio (e FTE: **da verificare** se richiesto) per area/profilo, ufficio | Annuale (adozione entro 31/1) | Sottosez. 3.3 (**prassi-interpretazione**) |
| Cessazioni previste nel triennio (pensionamenti, scadenze contratti) | Giuridico (date di nascita, anzianità contributiva, scadenze) | Persona, data prevista | Annuale, rolling triennale | **prassi-interpretazione** |
| Capacità assunzionale (rapporto spesa/entrate, valori soglia) | Contabilità + paghe | Importi ente | Annuale | art. 33 c. 2 d.l. 34/2019 e DM 17/3/2020 (**norma certa**) |
| Struttura organizzativa (organigramma, uffici, posizioni di EQ) | Giuridico/organizzazione | Ufficio, responsabile | Annuale / a variazione | Sottosez. 3.1 (**norma certa** l'esistenza) |
| Lavoro agile: dipendenti, giorni, attività | Presenze + giuridico (accordi individuali) | Persona, accordo, giorni | Annuale | Sottosez. 3.2 (**norma certa** l'esistenza; indicatori **da verificare**) |
| Formazione (ore/partecipanti) | Gestione formazione / presenze | Persona, corso, ore | Annuale | **da verificare** |

### C. Trasparenza (d.lgs. 33/2013, sezione "Personale" e collegate)

- **norma certa**: art. 16 c. 1 pubblicazione del conto annuale con dotazione organica, personale in servizio e costo per qualifiche e aree; c. 2 costo complessivo del personale a tempo indeterminato per aree professionali; c. 3 tassi di assenza trimestrali distinti per uffici di livello dirigenziale. https://colosseo.it/trasparenza/dotazione-organica/ , https://amministrazionetrasparente.iss.it/index.html%3Ftipologie=tassi-di-assenza.html
- **prassi-interpretazione**: tasso di assenza = giorni di assenza complessivi / giorni lavorativi del periodo, conteggiando tutte le cause di mancata presenza (circolari DFP n. 3/2009 e n. 5/2009 richiamate dagli enti). https://autorita-trasporti.it/trasparenza/tassi-di-assenza/tassi-di-assenza-2023
- **norma certa**: art. 17 c. 1 elenco annuale del personale non a tempo indeterminato; c. 2 costo complessivo trimestrale, articolato per aree professionali. https://www.ce.camcom.it/printpdf/4029 , https://www.uniba.it/it/amministrazione-trasparente/personale/personale-non-indeterminato/costo-tempo-determinato/costo-2023 (testo **da verificare** su Normattiva)
- **norma certa**: art. 20 ammontare dei premi collegati alla performance stanziati ed effettivamente distribuiti; dati sulla distribuzione e sul grado di differenziazione. https://www.regione.lombardia.it/amministrazione-trasparente/performance
- **norma certa**: art. 21 c. 2 contratti integrativi con relazioni, e informazioni sui costi della contrattazione integrativa certificate e trasmesse al MEF (le tabelle del conto annuale). https://www.anticorruzione.it/amministrazione-trasparente/personale/contrattazione-integrativa ; **da verificare**: dal 2026 sostituzione con link alla banca dati ARAN-CNEL https://www.aifa.gov.it/contrattazione-integrativa
- **da verificare** (non coperti dalla ricerca): art. 14 (titolari di incarichi dirigenziali: compensi), art. 18 (incarichi conferiti o autorizzati ai dipendenti), art. 15 (consulenti e collaboratori).
- **prassi-interpretazione**: ANAC delibera n. 495 del 25/09/2024 (schemi standard per artt. 4-bis, 13, 31; obbligatori dal 22/01/2026), aggiornata con delibera n. 481 del 3/12/2025; non introduce nuovi obblighi ma formati uniformi. https://www.segretaricomunalivighenzi.it/pubblicato-nella-g-u-del-21-1-2025-n-16-il-comunicato-anac-relativo-a-delibera-del-25-9-2024-n-495-con-cui-sono-stati-approvati-3-schemi-di-pubblicazione-ai-sensi-dellart-48-del-d-lg/24/01/2025/

| Dato | Fonte originaria | Granularità | Periodicità | Riferimento |
|---|---|---|---|---|
| Dotazione, personale in servizio, costo per qualifica/area | Giuridico + paghe | Aggregato per qualifica/area | Annuale | art. 16 c. 1-2 (**norma certa**) |
| Tasso di assenza | Presenze + giuridico (ufficio di assegnazione, calendario) | Per ufficio di livello dirigenziale, per mese/trimestre | Trimestrale | art. 16 c. 3 (**norma certa**); metodo **prassi-interpretazione** |
| Elenco personale non a tempo indeterminato | Giuridico | Persona/rapporto | Annuale | art. 17 c. 1 (**norma certa**) |
| Costo personale non a tempo indeterminato | Paghe (competenza o cassa: **da verificare**) | Aggregato per area professionale | Trimestrale | art. 17 c. 2 (**norma certa**) |
| Premi performance stanziati e distribuiti, differenziazione | Fondo + paghe + valutazione | Aggregato; distribuzione per fasce | Annuale/tempestivo | art. 20 (**norma certa**) |
| Costi contrattazione integrativa | Fondo + contabilità | Come Tab. 15/SICI | Annuale | art. 21 c. 2 (**norma certa**) |
| Compensi dirigenti / incarichi a dipendenti | Giuridico + paghe | Persona | Tempestiva/annuale | artt. 14, 18 (**da verificare**) |

### D. Perla PA e altri canali del Dipartimento della Funzione Pubblica

- **GEDAP - permessi, distacchi, aspettative sindacali**: **norma certa** art. 50 c. 3-4 d.lgs. 165/2001; **prassi-interpretazione** comunicazione entro 2 giornate lavorative dall'autorizzazione (art. 22 c. 1 CCNQ 4/12/2017), dichiarazione annuale anche negativa (storicamente entro 31 marzo, più volte prorogata), mancata trasmissione = infrazione disciplinare; permessi non fruiti non riportabili. https://lentepubblica.it/?p=336947 , https://www.perlapa.gov.it/fileadmin/user_upload/PerlaPA/DFP_9090_-_Nota_chiarimenti_gedap_con_Aran-signed.pdf
- **Permessi L. 104/1992**: **norma certa** art. 24 L. 183/2010 (permessi art. 33 c. 2-3 L. 104/1992); **prassi-interpretazione** giorni/ore fruiti per beneficiario, anche beneficiari senza fruizione, esclusi congedi straordinari; termine 31 marzo dell'anno successivo (rilevazione 2026). https://www.orizzontescuola.it/permessi-ex-legge-104-perlapa-ricorda-la-scadenza-del-31-marzo-2026/ , https://www.informazionefiscale.it/legge-104-permessi-statali-comunicazione-perlapa
- **Anagrafe delle prestazioni**: **norma certa** art. 53 c. 12-14 d.lgs. 165/2001: comunicazione entro 15 giorni degli incarichi conferiti o autorizzati ai dipendenti, anche gratuiti, con oggetto e compenso lordo; **prassi-interpretazione** dopo il d.lgs. 75/2017 la comunicazione avviene su Perla PA; per gli incarichi del c. 13 i compensi vanno comunicati dal dipendente entro 10 giorni dal pagamento. https://www.consiglio.regione.lazio.it/binary/consiglio_regionale/tbl_trasparenzaContenuti/Anagrafe_delle_Prestazioni_anno_2021.pdf , https://www.regione.piemonte.it/web/sites/default/files/media/documenti/2022-07/modulo_anagrafe_prestazioni_bi.pdf ; **da verificare**: obbligo dell'ente di comunicare anche gli incarichi conferiti a consulenti esterni (c. 14) e scadenze vigenti.
- **GEPAS - scioperi**: **norma certa** art. 5 L. 146/1990 (pubblicità di numero di aderenti, durata, trattenute); **prassi-interpretazione** dati aggregati in GEPAS entro le 14 del giorno dello sciopero (provvisori) e appena possibile (consolidati). https://www.cnr.it/en/trasparenza/circolari/allegato/60091/direttiva-ugru-nuova-piattaforma-perlapa-gepas-signed.pdf , https://www.funzionepubblica.gov.it/sites/funzionepubblica.gov.it/files/documenti/scioperi_pdf/154-20042021-1656513.pdf

| Dato | Fonte originaria | Granularità | Periodicità | Riferimento |
|---|---|---|---|---|
| Permessi/distacchi/aspettative sindacali autorizzati e fruiti | Giuridico (autorizzazione) + presenze (fruizione) | Persona, sigla sindacale, tipo prerogativa, ore/giorni, date | Evento (entro 2 gg lav.) + annuale | GEDAP (**prassi-interpretazione**) |
| Permessi L. 104 fruiti | Presenze + giuridico (titolo del beneficio, assistito) | Persona beneficiaria, giorni/ore per mese o anno (**da verificare**) | Annuale | art. 24 L. 183/2010 (**norma certa**) |
| Incarichi extra-istituzionali dei dipendenti | Giuridico (autorizzazione) + paghe/terzi (compenso) | Persona, incarico, soggetto conferente, oggetto, compenso, date | Evento (15 gg) + compensi | art. 53 c. 12-14 (**norma certa**) |
| Adesioni a sciopero | Presenze + paghe (trattenute) | Aggregato per sciopero: aderenti, in servizio, trattenute | Evento (giorno stesso) | art. 5 L. 146/1990 (**norma certa**) |

### E. Rilevazione deleghe sindacali (ARAN)

- **norma certa**: art. 43 d.lgs. 165/2001 (rappresentatività: dato associativo). **prassi-interpretazione**: deleghe attive al 31/12 con trattenuta nel cedolino di gennaio, inserite nell'applicativo "Deleghe Sindacali" ARAN (ciclo 2025-2027: dati al 31/12/2024, finestra 1/2-31/3/2025); GEDAP è sistema distinto. https://www.orizzontescuola.it/accertamento-rappresentativita-sindacati-rilevazione-deleghe-al-31-dicembre-circolare-aran/ , https://compartounico.regione.fvg.it/export/sites/comparto-unico/contrattazione/contrattazione-collettiva-di-comparto/prerogative-rsu-rappresentativita-distacchi/documentazione/2025_Prot.-114579_deleghe_al_31122024.PDF

| Dato | Fonte originaria | Granularità | Periodicità | Riferimento |
|---|---|---|---|---|
| Deleghe sindacali con trattenuta | Giuridico (delega, revoca) + paghe (trattenuta) | Persona, sigla, data, comparto/area | Triennale (per ciclo contrattuale), riferita al 31/12 | art. 43 d.lgs. 165/2001 (**norma certa**); modalità **prassi** |

### F. Limiti e monitoraggio della spesa di personale

- **norma certa**: art. 33 c. 2 d.l. 34/2019 e DM 17/03/2020 (GU 27/04/2020, decorrenza 20/04/2020): valori soglia per fascia demografica del rapporto spesa di personale / entrate correnti al netto del FCDE; percorso di rientro. https://lentepubblica.it/personale-e-previdenza/facolta-assunzionali/ ; **da verificare** su GU: definizioni dell'art. 2 DM (aggregati di rendiconto, media triennale delle entrate).
- **prassi-interpretazione**: nella spesa di personale rientrano gli impegni di competenza per tempo indeterminato e determinato, co.co.co., somministrazione, art. 110 TUEL (Corte dei conti Lombardia 96/2022). https://www.segretaricomunalivighenzi.it/?p=39602
- **norma certa**: art. 23 c. 2 d.lgs. 75/2017: tetto del trattamento accessorio pari all'importo 2016; per i comuni adeguabile in base all'art. 33 d.l. 34/2019 rispetto al personale al 31/12/2018. https://www.segretaricomunalivighenzi.it/?p=21797 . Resta vigente anche dopo il d.l. 144/2026 secondo la stampa specializzata (**prassi-interpretazione**).
- **norma certa (storica) / da verificare (vigenza)**: art. 1 c. 557, 557-quater (media 2011-2013) e 562 (spesa 2008) L. 296/2006. Secondo ItaliaOggi e Le Autonomie il d.l. 144/2026 ("decreto PA 2026") ne disapplica i limiti per gli enti soggetti all'art. 33 d.l. 34/2019 (non per le unioni di comuni); conversione in legge non verificata. https://www.italiaoggi.it/enti-locali-e-pa/enti-locali-addio-ai-tetti-di-spesa-sul-personale-v1kil8sl , https://leautonomie.it/limiti-alla-spesa-di-personale-cancellati-ma-solo-a-meta/?pdf=28693 , https://lentepubblica.it/personale-e-previdenza/personale-degli-enti-locali-dopo-il-dl-pa-2026-superati-i-tetti-storici-resta-il-nodo-del-salario-accessorio/
- **da verificare**: limite al lavoro flessibile (art. 9 c. 28 d.l. 78/2010) non coperto dalla ricerca.

| Dato | Fonte originaria | Granularità | Periodicità | Riferimento |
|---|---|---|---|---|
| Spesa di personale (impegni di competenza) per tipologia di rapporto | Contabilità (impegni) alimentata da paghe | Importi per rapporto, capitolo/macroaggregato, anno | Annuale (rendiconto) + previsione | art. 33 c. 2 d.l. 34/2019 (**norma certa**) |
| Entrate correnti e FCDE | Contabilità | Importi ente, ultimi rendiconti | Annuale | DM 17/3/2020 (**norma certa**; definizioni **da verificare**) |
| Personale al 31/12/2018 e anno corrente | Giuridico | Conteggio (FTE: **da verificare**) | Annuale | art. 33 d.l. 34/2019 (**prassi-interpretazione**) |
| Risorse accessorio 2016 e anno corrente, con esclusioni | Fondo + contabilità | Importi per componente | Annuale | art. 23 c. 2 d.lgs. 75/2017 (**norma certa**) |
| Spesa media 2011-2013 / spesa 2008 | Contabilità storica | Importo ente | Annuale (se ancora vigente) | c. 557-quater/562 (**da verificare** vigenza) |

### G. Contratto integrativo e fondo risorse decentrate

- **norma certa**: art. 40 c. 3-sexies d.lgs. 165/2001 (relazione illustrativa e tecnico-finanziaria su schemi MEF-DFP, certificate dall'organo di controllo ex art. 40-bis c. 1); art. 40-bis c. 5 trasmissione telematica ad ARAN e CNEL entro 5 giorni dalla sottoscrizione. https://www.bollettinoadapt.it/wp-content/uploads/2015/09/manuale_-trasmissione_contratti_integrativi_luglio_2015.pdf
- **prassi-interpretazione**: schemi della circolare RGS n. 25 del 19/07/2012; relazione tecnico-finanziaria: Modulo 1 costituzione del fondo (sez. I risorse fisse aventi carattere di certezza e stabilità, risorse variabili, decurtazioni), moduli successivi su destinazione, copertura e compatibilità. https://trasparenza.comune.livorno.it/sites/trasparenza/files/index/amm_trasparente/relazione_tecnico_finanziaria_ccdi_2022_2024.pdf ; articolazione completa dei moduli **da verificare** sulla circolare.

| Dato | Fonte originaria | Granularità | Periodicità | Riferimento |
|---|---|---|---|---|
| Costituzione del fondo per voce (stabili, variabili, decurtazioni, incrementi di legge) | Atti (determinazione di costituzione) + contabilità | Voce di costituzione, base normativa/contrattuale, importo | Annuale | art. 40 c. 3-sexies; circ. RGS 25/2012 (**prassi**) |
| Destinazione per istituto (progressioni, performance, indennità, EQ...) | Contratto integrativo + paghe (utilizzo effettivo) | Istituto, importo previsto vs erogato | Annuale | idem |
| Copertura in bilancio | Contabilità | Capitolo/impegno | Annuale | idem |
| Verifica tetto 2016 | Fondo | Componenti incluse/escluse | Annuale | art. 23 c. 2 d.lgs. 75/2017 (**norma certa**) |

### H. Altri adempimenti sul personale individuati

- **Prospetto informativo disabili** (L. 68/1999 art. 9 c. 6): **norma certa** obbligo per datori con almeno 15 dipendenti, telematico, entro il 31 gennaio, situazione al 31/12 precedente, solo se ci sono variazioni rilevanti per l'obbligo. **da verificare**: regole di computo specifiche per le PA. https://www.regione.fvg.it/rafvg/cms/RAFVG/formazione-lavoro/servizi-lavoratori/FOGLIA26/ , https://www.dottrinalavoro.it/notizie-c/dottrina-per-il-lavoro-entro-il-31-gennaio-invio-del-prospetto-informativo-disabili
  - Dati: base di computo, lavoratori appartenenti alle categorie protette, esclusioni; fonte giuridico; granularità persona; annuale.
- **Non coperti dalla ricerca (da verificare)**: comunicazioni obbligatorie UniLav (eventi di rapporto), relazione al conto annuale / monitoraggio (per gli EL non risulta applicabile: **da verificare**), rilevazioni su lavoro agile, Comitato unico di garanzia (relazione annuale), dati per BDAP/rendiconto (allegati sul personale), certificazioni per la Corte dei conti (questionari sul rendiconto).

## Requisiti per il modello dati

Requisiti derivati (analisi del ricercatore, **prassi-interpretazione**):

1. **Rapporto di lavoro come entità datata**: tipologia (indeterminato, determinato, dirigente, segretario, co.co.co., LSU/LPU, somministrato, comandato in entrata), inquadramento, profilo, tempo pieno/parziale con percentuale, ufficio di assegnazione, tutti con validità da/a. Serve a ricostruire consistenze a qualunque data (31/12, 31/12/2018, fine trimestre) e unità-anno/FTE.
2. **Eventi di carriera tipizzati con causa**: assunzione (modalità), cessazione (causa), comando/distacco (ente controparte), progressione, cambio ufficio. Alimentano le tabelle di flusso SICO e la 3.3 PIAO.
3. **Anagrafe estesa**: data di nascita, genere, titolo di studio, data di inizio anzianità, appartenenza a categorie protette, deleghe sindacali con date di rilascio/revoca.
4. **Assenze come eventi giornalieri/orari con causale normalizzata** e mapping verso: causali SICO Tab. 11 (inclusa la distinzione malattia con/senza trattenuta), tasso di assenza (art. 16 c. 3), L. 104 (beneficiario e assistito), GEDAP (sigla, tipo prerogativa, atto di autorizzazione), sciopero (data dello sciopero proclamato). Una sola registrazione, più mapping.
5. **Calendario lavorativo per persona/ufficio**: necessario per il denominatore del tasso di assenza e per le unità-anno.
6. **Struttura organizzativa versionata**: uffici di livello dirigenziale, responsabili, EQ; legame persona-ufficio datato.
7. **Ogni importo erogato classificato su più assi**: voce SICO (Tab. 12/13/14), istituto del fondo (destinazione), capitolo/impegno di bilancio, competenza (anno di riferimento) e cassa (data pagamento), area professionale. Da qui: Tab. 12-14, art. 17 c. 2 trimestrale, art. 20, limiti di spesa, FTE percettori dell'accessorio.
8. **Fondo risorse decentrate come oggetto proprio**: voci di costituzione con base normativa, importo, natura (stabile/variabile), inclusione/esclusione dal tetto 2016; destinazioni per istituto; utilizzo effettivo collegato ai pagamenti. Alimenta Tab. 15, SICI, relazione tecnico-finanziaria, art. 21, art. 23 c. 2.
9. **Ponte con la contabilità**: impegni di competenza sulla spesa di personale, entrate correnti, FCDE e dati di rendiconto letti (non reinseriti) dalla contabilità armonizzata, per rapporto art. 33 e riconciliazione SICO.
10. **Incarichi extra-istituzionali** come entità: dipendente, soggetto conferente, oggetto, autorizzazione (data), compenso previsto e pagamenti con date. Alimenta anagrafe delle prestazioni e trasparenza (art. 18, **da verificare**).
11. **Fotografie annuali congelate**: snapshot al 31/12 con versione e data di invio, perché le rilevazioni chiedono confronti con anni fissi (2016, 2018) e non devono cambiare se si corregge lo storico.
12. **Tabelle di mapping versionate per anno di rilevazione** (causali, voci SICO, tipologie) perché le circolari RGS cambiano ogni anno (es. 2024: split malattia; 2025: FTE e Scheda A33).

## Implicazioni

- Le presenze non possono restare un input riassuntivo mensile per la busta: servono eventi con causale fine e collegamento ad atti (autorizzazioni GEDAP, titoli L. 104).
- Il collegamento importo -> impegno/capitolo, già richiesto dalle proposte di movimento contabile, è anche il requisito dei limiti di spesa: conviene progettarlo una sola volta.
- Il fondo deve esistere prima e indipendentemente dai pagamenti accessori (vincolo di capienza), tema del ticket sul fondo.
- Gli adempimenti non stipendiali sono in gran parte "viste" sullo stesso insieme di fatti: un livello di estrazione parametrico per anno di rilevazione è preferibile a moduli separati.

## Domande aperte

1. Struttura ufficiale delle tabelle SICO 3-10 e delle voci di Tab. 12-14 per il comparto Funzioni Locali (capitolo 6 della circolare n. 12/2026): da leggere sulla fonte primaria.
2. Contenuto della nuova Scheda A33 e definizione di FTE usata da RGS (giorni, ore, percentuale part-time?).
3. Testo vigente del d.l. 144/2026 dopo conversione: quali limiti di spesa restano per comuni e unioni.
4. Costo art. 17 c. 2: competenza o cassa? Inclusi oneri riflessi?
5. Tracciato Perla PA per L. 104 e GEDAP: dettaglio mensile o annuo, dati dell'assistito.
6. Definizioni del DM 17/3/2020 (art. 2) e circolare interministeriale attuativa per il calcolo del rapporto.
7. PIAO: è richiesta la consistenza in FTE o in teste? Esistono linee guida DFP aggiornate dopo il 2023?
8. Trasparenza art. 21 dal 2026: pubblicazione sostituita da link alla banca dati ARAN-CNEL?
9. Amministratori, co.co.co., LSU/LPU: in quali tabelle SICO e in quali limiti di spesa rientrano?

## Fonti principali

- RGS circolare n. 12 del 26/06/2026 (Conto Annuale 2025): https://www.rgs.mef.gov.it/_Documenti/VERSIONE-I/CIRCOLARI/2026/12/Allegato-alla-Circolare-del-26-giugno-2026-n-12.pdf
- RGS circolare n. 18 del 19/06/2025 (Conto Annuale 2024): https://www.rgs.mef.gov.it/_Documenti/VERSIONE-I/CIRCOLARI/2025/18/Circolare-del-19-giugno-2025-n-18.pdf
- RGS capitolo 1 informazioni operative SICO: https://www.rgs.mef.gov.it/_Documenti/VERSIONE-I/e-GOVERNME1/SICO/Conto-annu/2025/documenti/CAPITOLO-1-informazioni-operative.pdf
- DFP nota GEDAP con ARAN: https://www.perlapa.gov.it/fileadmin/user_upload/PerlaPA/DFP_9090_-_Nota_chiarimenti_gedap_con_Aran-signed.pdf
- ARAN manuale trasmissione contratti integrativi (2015): https://www.bollettinoadapt.it/wp-content/uploads/2015/09/manuale_-trasmissione_contratti_integrativi_luglio_2015.pdf
- Altre fonti citate nelle singole sezioni.
