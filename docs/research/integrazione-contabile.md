# Integrazione nativa con la contabilità armonizzata

Ticket: #8 (mappa #1). Ramo: `research/integrazione-contabile`. Data: 2026-10-21.

## Domanda

Come la spesa di personale di un Ente Locale può diventare movimenti di contabilità armonizzata (impegni, liquidazioni, mandati, reversali per ritenute e oneri riflessi; IRAP; F24EP e regolarizzazioni) senza export/reimport? Quali regole del principio contabile applicato riguardano la spesa di personale, quali standard di scambio esistono, quali fornitori espongono API documentate pubblicamente, cosa deve contenere un contratto neutro rispetto al fornitore per proposte di movimento da confermare in Ragioneria.

## Legenda e limiti del metodo

- **norma certa**: contenuto di una norma o di uno standard ufficiale, con riferimento indicato e riscontrato in almeno una riproduzione del testo.
- **prassi-interpretazione**: lettura di dottrina, magistratura contabile, enti o pratica diffusa.
- **da verificare**: plausibile ma non riscontrato sul testo ufficiale vigente in questa sessione.

Limite dichiarato: in questa sessione i siti istituzionali (rgs.mef.gov.it, agid.gov.it, normattiva.it, bancaditalia.it) non erano raggiungibili in lettura diretta (proxy/DNS). I riscontri sono stati fatti tramite motore di ricerca sugli estratti dei documenti primari (URL citati) e su riproduzioni del testo di norma (Brocardi, estratti di allegati pubblicati da consigli regionali e Governo). Anche dove la marcatura è **norma certa**, il testo vigente va riletto sulla fonte ufficiale prima di entrare nella specifica.

## Sintesi

1. La spesa di personale ha regole proprie di impegno: il tabellare e gli oneri riflessi sono impegnati automaticamente con l'approvazione del bilancio; il salario accessorio segue la sottoscrizione dell'integrativo e passa per il fondo pluriennale vincolato se esigibile nell'esercizio successivo. Quindi la paga **non crea** la maggior parte degli impegni: li **consuma** (liquidazione) e propone variazioni/sub-impegni solo per eccezioni.
2. Lo standard di scambio che esiste e che è nazionale è solo quello **tra ente e tesoriere**: OPI su SIOPE+ (XML, regole tecniche AgID, infrastruttura Banca d'Italia). Il mandato OPI ha una struttura `ritenute` che collega le reversali al mandato: è il modello ufficiale del rapporto netto/ritenute.
3. **Non esiste** uno standard nazionale per lo scambio paghe → contabilità dentro l'ente (proposta di impegno/liquidazione). Non ho trovato documentazione pubblica di API dei principali fornitori di contabilità per enti locali.
4. Un contratto neutro deve quindi essere definito dal progetto, ancorato a vocabolari ufficiali (piano dei conti integrato, missione/programma, codici SIOPE, tipi di pagamento OPI, codici tributo F24EP) e agli elementi obbligatori del mandato (art. 185 TUEL), lasciando all'ente-adattatore la mappatura su capitoli/articoli e la numerazione.

## Findings

### A. Ciclo della spesa e spesa di personale

- **norma certa** Impegno automatico del tabellare e degli oneri riflessi: art. 183, comma 2, lett. a), TUEL (D.Lgs. 267/2000): con l'approvazione del bilancio e successive variazioni, senza ulteriori atti, è costituito impegno per il "trattamento economico tabellare già attribuito al personale dipendente e per i relativi oneri riflessi". https://brocardi.it/testo-unico-enti-locali/parte-ii/titolo-iii/capo-ii/art183.html
- **norma certa** Allegato 4/2 al D.Lgs. 118/2011 (principio contabile applicato della contabilità finanziaria), punto 5.2: impegno a inizio esercizio per l'intero importo dei trattamenti fissi e continuativi con dinamica salariale predefinita da legge o contrattazione collettiva nazionale, anche per gli esercizi successivi del bilancio di previsione; vi rientra il personale comandato/utilizzato, con rimborso rilevato in entrata. Estratti dell'allegato: https://www.governo.it/sites/governo.it/files/76572-9653.pdf ; https://www.consiglioregionale.calabria.it/upload/istruttoria/2%20Allegato%20n%204.2%20e%204.4%20D.%20Lgs.%20n.%20118-2011.pdf
- **norma certa** (con riserva di rilettura del testo vigente) Punto 5.2 dell'allegato 4/2: le spese per trattamento accessorio e premiante liquidate nell'esercizio successivo sono stanziate e impegnate nell'esercizio cui si riferiscono; l'obbligazione nasce con la sottoscrizione dell'integrativo ed è imputata agli esercizi di esigibilità; a fine esercizio, se l'integrativo non è sottoscritto, le risorse del fondo regolarmente costituito confluiscono nel risultato di amministrazione vincolato. Riportato da: https://www.filodiritto.com/la-corretta-contabilizzazione-del-salario-accessorio-spettante-al-personale-dipendente-dagli-enti-locali ; https://fondazioneifel.it/documenti-e-pubblicazioni/faq-strumenti/item/download/1131_7968a6ebaa303b18cc2d00240434e49d
- **prassi-interpretazione** Fondo pluriennale vincolato per l'accessorio: con integrativo sottoscritto entro l'anno, la quota esigibile nell'anno successivo (tipicamente performance) è impegnata con imputazione all'anno successivo e coperta da FPV di spesa corrente; la sola parte stabile del fondo non costituito confluisce in avanzo vincolato, la variabile diventa economia. Orientamento della magistratura contabile riportato in https://www.segretaricomunalivighenzi.it/?p=15154 e https://www.segretaricomunalivighenzi.it/?p=41074. Il numero esatto della deliberazione Corte dei conti Lombardia citata dalle rassegne (368 o 386/2019) è **da verificare**.
- **prassi-interpretazione** La certificazione del fondo da parte dell'organo di revisione è letta come elemento costitutivo ai fini del vincolo a fine esercizio. https://www.segretaricomunalivighenzi.it/06-10-2023-certificazione-del-fondo-per-il-salario-accessorio-da-parte-dellorgano-di-revisione/06/10/2023
- **da verificare** Trattamento puntuale di IRAP e oneri sull'accessorio imputato all'anno successivo (seguono l'imputazione della retribuzione cui accedono?) e degli arretrati da rinnovo contrattuale: non riscontrato sul testo del punto 5.2 in questa sessione.
- **norma certa** Esercizio provvisorio: le spese di personale sono tra quelle sottratte al limite dei dodicesimi (allegato 4/2, gestione provvisoria/esercizio provvisorio), estratti citati sopra; l'art. 185, comma 2, TUEL prevede nel mandato l'identificazione delle spese non soggette al regime dei dodicesimi. https://miolegale.it/testi-unici/enti-locali/art-185/

### B. Elementi del mandato e controllo della Ragioneria

- **norma certa** Art. 185, comma 2, TUEL: il mandato contiene almeno numero progressivo per esercizio, data, missione/programma/titolo (distinti per residui o competenza e cassa), codifica di bilancio, creditore (e chi può quietanzare, con codice fiscale/partita IVA), importo in cifre e lettere, causale, scadenza se prevista, modalità di estinzione, codifica SIOPE e codici della transazione elementare, indicazione delle spese non soggette ai dodicesimi in esercizio provvisorio. https://miolegale.it/testi-unici/enti-locali/art-185/ ; https://www.brocardi.it/testo-unico-enti-locali/parte-ii/titolo-iii/capo-ii/art185.html
- **norma certa** Art. 185, comma 3: controllo di impegno, liquidazione e autorizzazione di cassa spetta al servizio finanziario, che contabilizza e trasmette al tesoriere. Conseguenza per il modello: il numero di mandato/reversale è assegnato dalla Ragioneria, mai dalla proposta.
- **norma certa** Art. 185, comma 4: il tesoriere paga anche senza mandato obblighi tributari, somme iscritte a ruolo e delegazioni; l'ente emette il mandato di regolarizzazione entro trenta giorni (termine **da verificare** sul testo vigente). È la base delle regolarizzazioni dei provvisori F24EP. Fonti come sopra.
- **norma certa** Art. 216, comma 2, TUEL: il tesoriere non estingue mandati privi della codifica prevista (inclusa SIOPE). https://www.brocardi.it/testo-unico-enti-locali/parte-ii/titolo-v/capo-iii/art216.html
- **norma certa** Art. 184 TUEL (liquidazione) è la fase intermedia tra impegno e mandato; contenuti dell'atto di liquidazione non approfonditi in questa sessione (**da verificare**).

### C. Piano dei conti integrato e codifiche

- **norma certa** Art. 8 D.Lgs. 118/2011 e DM MEF 9 giugno 2016 (S.O. GU n. 154 del 4/7/2016): dal 2017 le codifiche SIOPE degli enti territoriali sono sostituite da quelle del piano dei conti integrato. https://finanze.regione.emilia-romagna.it/documenti-di-finanza/decreto-siope ; https://www.agid.gov.it/sites/default/files/repository_files/documenti_indirizzo/st_n.17_-_22-07-2016_-_siope_oil.pdf
- **prassi-interpretazione** (codici riscontrati in documenti di bilancio pubblicati da enti, non sull'allegato ufficiale):
  - `U.1.01.01.01.002` Voci stipendiali corrisposte al personale a tempo indeterminato. https://amministrazionetrasparente.iss.it/wp-content/uploads/2019/12/4.2_BilancioGestionaleSpese-2.pdf
  - `U.1.01.02.01.001` Contributi obbligatori per il personale. https://santannapisa.it/sites/default/files/inline-files/2023_prospetto%20missioni%20e%20programmi.pdf
  - `U.7.01.02.01.000` Versamenti di ritenute erariali su redditi da lavoro dipendente riscosse per conto terzi; `U.7.01.02.02.000` ritenute previdenziali e assistenziali; `U.7.01.02.99.000` altre ritenute. https://www.arpab.it/arpab/wp-content/uploads/2025/07/Dati-in-formato-tabellare-II-Trim-2025.pdf
- **da verificare** Codice di V livello dell'IRAP (atteso nel macroaggregato U.1.02 "Imposte e tasse a carico dell'ente") e i codici di entrata del Titolo 9 speculari alle ritenute (attesi in E.9.01.02): non riscontrati in questa sessione. Non sono riportati codici non verificati.
- **da verificare** Elenco completo degli elementi della transazione elementare (allegato 7 al D.Lgs. 118/2011: attesi missione, programma, piano dei conti, COFOG, codice UE, SIOPE, CUP, ricorrente/non ricorrente, perimetro sanitario): da rileggere sull'allegato.

### D. SIOPE+ e OPI

- **norma certa** SIOPE+ nasce dall'art. 1, comma 533, L. 232/2016, che integra l'art. 14 L. 196/2009; gli ordinativi sono emessi secondo lo standard OPI e transitano sull'infrastruttura SIOPE gestita dalla Banca d'Italia; AgID emana regole tecniche e schemi XSD. https://www.agid.gov.it/index.php/it/piattaforme/siope ; https://www.rgs.mef.gov.it/_Documenti/VERSIONE-I/e-GOVERNME1/SIOPE/SIOPE/documenti/opi-regole_tecniche_v_1_3_1.pdf
- **norma certa** Documento di supporto più recente individuato: "Vademecum di supporto per l'emissione degli OPI" v1.8.1 (marzo 2026), che ha sostituito la denominazione "Linee guida". https://www.agid.gov.it/sites/agid/files/2026-03/OPI-Vademecum%20OPI_V_1_8_1.pdf ; v1.8: https://www.agid.gov.it/sites/default/files/repository_files/documentazione/OPI-Vademecum%20OPI_V_1_8.pdf. La versione corrente delle Regole tecniche OPI è **da verificare**.
- **norma certa** (standard tecnico) Il flusso OPI è un XML; nel mandato, per beneficiario, la struttura `ritenute` (ripetibile, fino a 30 occorrenze secondo le linee guida) riporta `importo_ritenute`, `numero_reversale`, `progressivo_versante` della reversale collegata. Le reversali collegate a mandati per ritenute e quelle di regolarizzazione sono "ESENTE BOLLO". https://www.agid.gov.it/sites/default/files/repository_files/opi-linee_guida_v1_6_1.pdf ; https://www.agid.gov.it/sites/default/files/repository_files/documentazione/OPI-Vademecum%20OPI_V_1_8.pdf
- **norma certa** (standard tecnico) Tra i valori di `tipo_pagamento` figurano `F24EP` (riservato agli enti in Tesoreria Unica), `COMPENSAZIONE` (mandati compensati con reversali tramite struttura `ritenute`) e, dall'esercizio 2024, una voce unificata `REGOLARIZZAZIONE` per i provvisori. https://www.agid.gov.it/sites/default/files/repository_files/schedetecnichemodificheopi_v06_03042024.pdf ; https://www.agid.gov.it/sites/default/files/repository_files/schedetecnichemodificheopi_se08_v04_09.03.2023.pdf
- **da verificare** Se tutti i Comuni del target siano oggi in Tesoreria Unica (condizione per `F24EP` come tipo pagamento) e l'effetto del progetto Re.Tes. di Banca d'Italia dal 1/1/2025 (IBAN del conto di tesoreria). Fonte di segnalazione: https://www.segretaricomunalivighenzi.it/?p=60446
- **norma certa** F24 EP approvato con provvedimento Agenzia delle Entrate 8/11/2007, versamenti dal 1/1/2008. https://www.agenziaentrate.gov.it/portale/documents/20143/306263/Risoluzione+n+367+del+12+dicembre+2007_risoluzione_367_12_dic_2007.pdf
- **prassi-interpretazione** Nella pratica i versamenti F24EP sono spesso addebitati dal tesoriere come provvisori di uscita e regolarizzati con mandati "a copertura"; nelle verifiche di cassa compaiono sospesi "versamento tributi F24-EP" e "stipendi". https://www.invalsi.it/amm%5Ftrasp/documenti/controlli_rilievi_amm/2023/V12_2023_Allegato%201%20Verifica%20di%20cassa.pdf

### E. Fornitori e API

- **da verificare / non trovato** Nessuna documentazione pubblica di API (REST/SOAP, OpenAPI) per impegni, liquidazioni o ordinativi è emersa per i principali software di contabilità per enti locali (ricerche su Maggioli, Halley, Dedagroup/Civilia, PA Digitale/URBI). L'unico riscontro pubblico Maggioli riguarda l'integrazione di contabilità terze con la piattaforma pagoPA (JPPA), non le spese di personale. https://assistenza.maggioli.it/wp-content/uploads/2019/06/Domande_Risposte_PagoPA_19062019.pdf
- **prassi-interpretazione** Le integrazioni paghe-contabilità esistenti avvengono tipicamente con tracciati proprietari concordati con il fornitore o per moduli dello stesso fornitore; le specifiche, se esistono, non sono pubbliche. Non citabile come fatto finché non si ha la documentazione.
- **da verificare** Catalogo PDND: non sono emersi e-service di contabilità finanziaria degli enti. https://www.cittametropolitana.fi.it/wp-content/uploads/D.D.-1485-del-27-06-2025.pdf

## Dati minimi di una proposta di movimento

Derivati dagli elementi obbligatori (art. 185 TUEL, OPI) e dalle esigenze di tracciabilità della mappa. Gli elementi marcati (E) sono assegnati o confermati dalla Ragioneria, non dalla proposta.

Comuni a ogni proposta:

- identificativo stabile della proposta e versione; ente; esercizio; periodo di competenza retributiva;
- tipo: `impegno` | `sub-impegno/variazione` | `liquidazione` | `mandato` | `reversale` | `regolarizzazione`;
- importo (centesimi, segno esplicito); causale testuale;
- classificazione ufficiale: missione, programma, titolo, macroaggregato, codice piano dei conti V livello (= codice SIOPE); altri elementi della transazione elementare (**da verificare** elenco);
- riferimento contabile dell'ente (capitolo/articolo) solo come esito della mappatura, (E);
- imputazione: esercizio di esigibilità; flag competenza/residuo; flag "coperto da FPV"; flag "non soggetto a dodicesimi";
- provenienza: elenco di righe sorgente (persona, istituto retributivo, norma/atto, input) che sommano all'importo;
- stato: proposta → confermata | respinta (con motivo) | modificata da Ragioneria.

Specifici:

- **Impegno / variazione**: atto presupposto (bilancio per il tabellare ex art. 183 c.2 lett. a; integrativo sottoscritto con data per l'accessorio; delibera costituzione fondo e certificazione revisori); esercizi di imputazione con ripartizione; creditore anche generico (personale) per oneri e IRAP.
- **Liquidazione**: impegno di riferimento (E), periodo, creditore o categoria (personale, INPS gestione dipendenti pubblici, Erario, Regione per IRAP), importo lordo; ragione del credito.
- **Mandato** (netto al personale o versamento a terzi): liquidazioni di riferimento; beneficiari (codice fiscale, IBAN, importo netto) o rinvio a un beneficiario cumulativo secondo prassi dell'ente (**da verificare** quale variante OPI usare); `tipo_pagamento` OPI (es. `F24EP`, `REGOLARIZZAZIONE`, `COMPENSAZIONE`); elenco ritenute collegate con importo e riferimento alla proposta di reversale (il numero reversale è (E)).
- **Reversale per ritenute** (partite di giro): mandato e beneficiario di origine; tipo ritenuta (erariale, previdenziale/assistenziale, altra); codice di entrata Titolo 9 (**da verificare**); importo; flag esente bollo; legame con il successivo mandato di versamento U.7.01.02.
- **Regolarizzazione F24EP**: estremi del provvisorio (numero e data comunicati dal tesoriere, (E)); delega F24EP di origine con righe per codice tributo/causale e importi; ripartizione per impegno/liquidazione (ritenute in partita di giro, oneri e IRAP su spesa corrente).

Eventi di ritorno attesi dalla contabilità: proposta confermata/respinta, numero impegno/liquidazione assegnato, mandato/reversale emesso, esito SIOPE+ (accettazione, quietanza), provvisorio regolarizzato.

## Standard disponibili

| Ambito | Standard | Stato |
|---|---|---|
| Ente → tesoriere | OPI su SIOPE+ (XML, XSD AgID) | **norma certa**, nazionale e obbligatorio |
| Classificazioni | Piano dei conti integrato, missioni/programmi, SIOPE (D.Lgs. 118/2011, DM 9/6/2016) | **norma certa** come vocabolario |
| Versamenti | F24 EP (Agenzia Entrate) | **norma certa** |
| Paghe → contabilità dentro l'ente | nessuno standard pubblico trovato | lacuna |
| API fornitori contabilità | nessuna documentazione pubblica trovata | **da verificare** con i fornitori |

## Trade-off

- **Generare OPI direttamente** vs **proporre movimenti alla contabilità**: OPI è l'unico standard certo, ma il mandato è atto della Ragioneria e presuppone impegno e liquidazione registrati in contabilità; generarlo fuori contabilità duplica il registro. Usare il vocabolario e la struttura `ritenute` di OPI dentro le proposte è a basso rischio; emettere OPI no.
- **Contratto ricco (fino al capitolo)** vs **contratto classificato (fino al piano dei conti)**: il capitolo è dell'ente; il contratto neutro dovrebbe fermarsi alle classificazioni ufficiali e lasciare la mappatura a un adattatore configurato dalla Ragioneria.
- **Granularità**: per persona (massima tracciabilità, volumi alti) vs aggregata per classificazione con dettaglio di provenienza consultabile. La seconda rispetta il "senza export/reimport" se il dettaglio resta interrogabile.
- **Integrazione**: API del fornitore (non documentate pubblicamente, vincolo commerciale) vs file firmato conforme al contratto (funziona con tutti, ma è un import) vs coda/eventi. Senza API pubbliche, un prototipo neutro può solo definire il contratto e un adattatore di riferimento.
- **Accessorio e FPV**: il modello deve sapere data di sottoscrizione dell'integrativo e stato del fondo per proporre l'imputazione corretta; altrimenti la proposta è sbagliata per costruzione.

## Implicazioni per la mappa

- Il "flusso proposta → conferma" non è un export: è un registro di proposte con stati ed eventi di ritorno; il modello deve memorizzare gli identificativi assegnati dalla Ragioneria.
- La catena di provenienza (norma → atto → input → importo) deve arrivare fino alla riga di proposta e alla ritenuta collegata.
- Il fondo risorse decentrate (ticket dedicato) va modellato con data di sottoscrizione, certificazione dei revisori ed esigibilità per anno, perché determina impegno e FPV.
- IRAP e oneri: le proposte vanno separate per creditore (Erario/Regione, INPS gestioni ex INPDAP) e per natura (spesa corrente vs partita di giro).

## Domande aperte

1. Testo vigente del punto 5.2 dell'allegato 4/2 (ultima versione Arconet) su accessorio, oneri, IRAP e arretrati da rinnovo.
2. Codici V livello per IRAP e codici di entrata del Titolo 9 per le ritenute: da prendere dall'allegato 6 vigente.
3. Elementi della transazione elementare (allegato 7) e quali sono obbligatori per le spese di personale.
4. Versione corrente delle Regole tecniche OPI e XSD; modalità ammesse per mandati con molti beneficiari (stipendi).
5. Tesoreria Unica e Re.Tes.: condizioni per `tipo_pagamento = F24EP` per gli enti del target.
6. Esistenza di specifiche di integrazione dei fornitori ottenibili su richiesta (non pubbliche) e loro licenza.
7. Contenuto minimo dell'atto di liquidazione (art. 184 TUEL e regolamento di contabilità dell'ente).
