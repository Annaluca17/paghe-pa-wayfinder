# Versamenti F24EP sulla fonte primaria: scadenze, compensazioni, IRAP

Ticket: #51 · Branch: `research/versamenti-f24ep` · Data: 2026-11-06 · Serve a: ADR 0023 (sezione «Da verificare»)

## Domanda

Quali regole fissano, sul testo vigente, il versamento F24EP di un Ente Locale? L'ADR 0023 ha deciso la struttura della delega e lascia senza fonte scadenze, compensazioni e IRAP. Il ticket chiede sei temi: scadenza e proroga di Ferragosto, termini di trasmissione e annullamento, compensazione dei crediti del sostituto, IRAP, codici e causali, effetto dei nuovi testi unici dal 01/01/2027.

## Legenda e limiti del metodo

- **norma certa**: testo di legge, provvedimento o specifica tecnica dell'amministrazione titolare, letto in questa sessione.
- **prassi-interpretazione**: risoluzione, circolare, comunicato, oppure lettura ricavata da fonti secondarie concordi.
- **da verificare**: non confermato su fonte primaria in questa sessione.

Come sono state lette le fonti (importa per fidarsi dei riferimenti):

- **Letti per intero** (PDF scaricati ed estratti): Allegato 2 delle specifiche F24EP (versione dicembre 2016), tabella codici F24EP aggiornata al 18/09/2025 e al 01/10/2026, risoluzione AdE 9/E del 31/01/2025, circolare AdE 29/E del 14/12/2020, D.Lgs. 33/2025 (testo unico versamenti e riscossione) e D.Lgs. 141/2026 (testo unico adempimenti e accertamento) nella Gazzetta Ufficiale.
- **Letti solo come sintesi**: gli articoli 10-bis, 16 e 30 del D.Lgs. 446/1997 e l'articolo 18 del D.Lgs. 241/1997 su Normattiva. Lo strumento ha restituito un riassunto, non il testo letterale, e in alcuni punti il testo è omesso. Quindi le lettere e i commi di questi articoli vanno riaperti prima di citarli in una regola.
- **Non recuperati**: il testo letterale dell'art. 32-ter DL 185/2008, dell'art. 15 D.Lgs. 175/2014 e dell'art. 17 D.Lgs. 241/1997 nella versione vigente nel 2026. Nei testi unici nuovi si leggono le norme che li riprendono (art. 4, art. 73, art. 3), che dichiarano la fonte di origine.
- **Il vault-pa** è stato consultato solo come pista (istruzioni 770/2026 e note interne). Nessuna affermazione di questo documento si regge solo sul vault.
- Nessun importo o aliquota è dato come certo senza una seconda fonte indipendente (ADR 0003). Dove la seconda fonte manca, lo dice la riga.
- Nessun dato reale né nome di ente.

## Sintesi

1. **Scadenza.** Il versamento F24EP scade il **16 del mese successivo**; se cade di **sabato o di giorno festivo** si versa il primo giorno lavorativo dopo. La regola è scritta per l'F24EP in modo esplicito (art. 4 c. 2 del D.Lgs. 33/2025, che riprende l'art. 32-ter DL 185/2008). Attenzione: parla di «giorno festivo», non solo di domenica; l'estrattore oggi ignora le festività infrasettimanali.
2. **Proroga di Ferragosto.** Il testo dell'art. 11 del D.Lgs. 33/2025 (ex art. 37 c. 11-bis DL 223/2006) sposta al **20 agosto** le scadenze dal 1° al 20 agosto, ma richiama gli articoli 3 e 10 c. 4, **non l'art. 4 dell'F24EP**. Per l'F24EP esiste solo una conferma di prassi: il comunicato AdE del 06/08/2008, riportato da Fisco Oggi. La conclusione più solida è: **la proroga vale**, ma con fonte di prassi. Dei due tool ha ragione l'estrattore (sempre accesa); F24EP-editor, che la spegne, va corretto. Resta da leggere il comunicato originale.
3. **Trasmissione.** Le regole sono nell'Allegato 2 (versione dicembre 2016, ancora quella linkata dall'AdE): saldo a debito entro le 20:00 del secondo giorno lavorativo prima della data di versamento; annullamento entro le 22:00 dello stesso giorno; con saldo zero fino alle 24:00 del giorno di versamento.
4. **Compensazione.** I crediti entrano nella stessa delega come righe a credito, con il vincolo tecnico che il **saldo di ogni modello (record V) non sia negativo**. Per ordine fra i crediti e riporto non c'è una norma che li fissi: sono scelte del modello. La prassi «trattamento integrativo compensato con la CPDEL» **non è né prescritta né vietata** dalla norma letta: la compensazione è orizzontale e generale.
5. **IRAP.** Aliquota **8,5%** (art. 16 c. 2 D.Lgs. 446/1997, confermata dalla risoluzione DF 1/2021), acconto mensile sugli emolumenti del mese precedente (art. 30 c. 5), codice **380E** nella sezione Regioni. La scadenza del 16 è di prassi: il decreto ministeriale richiamato dall'art. 30 c. 5 non è stato individuato.
6. **Codici.** Confermati sulla tabella AdE: 384E (addizionale comunale saldo), 385E (acconto), 380E, 150E/153E/154E/170E/175E (tutti usabili a debito e a credito), P608 e P632 (esistono e sono a debito). **Non** c'è una causale dedicata all'1% aggiuntivo. La scelta fra C10 e CXX dipende dall'aliquota (ridotta o piena) ma la fonte letta è del 2023 e riguarda un'altra categoria: resta da verificare.
7. **Testi unici dal 01/01/2027.** Cambia il **numero dell'articolo**, non il contenuto. Attenzione al ticket: il «TU D.Lgs. 117/2026» è il **nuovo TUIR**; le regole di versamento stanno nel **D.Lgs. 33/2025**, mentre i rimborsi da assistenza fiscale passano al **D.Lgs. 141/2026**.
8. **Novità non prevista nell'ADR:** il codice **179E** (e i suoi gemelli) per l'imposta sostitutiva sul trattamento accessorio del personale non dirigenziale delle amministrazioni pubbliche (L. 199/2025, art. 1 c. 237; risoluzione AdE 4/E del 29/01/2026). È un nuovo debito del ciclo stipendiale da mappare. Vedi il tema 5.

## Tema 1. Scadenza del versamento e proroga di Ferragosto

| Punto | Esito | Marcatura e fonte |
|---|---|---|
| Gli enti delle tabelle A e B della L. 720/1984 e le amministrazioni centrali usano l'F24EP per ritenute, addizionali, IRAP e contributi | Sì | **norma certa**: art. 4 c. 1 D.Lgs. 33/2025 (origine: art. 32-ter DL 185/2008) |
| Versamento entro il 16 del mese di scadenza; se cade di sabato o di giorno festivo, il primo giorno lavorativo successivo | Sì, scritto per l'F24EP | **norma certa**: art. 4 c. 2 D.Lgs. 33/2025. Nel 2026 vale ancora la fonte originaria (art. 32-ter DL 185/2008, non letto) e per i versamenti unitari l'art. 18 c. 1 D.Lgs. 241/1997 (letto in sintesi su Normattiva, vigente fino al 31/12/2026) |
| Il testo dice «giorno festivo», non «domenica» | Le festività infrasettimanali spostano la scadenza | **norma certa**, stessa fonte. Incoerenza con l'estrattore, che le ignora (`f24ep-core.js:2491-2515`, riga della conoscenza-tool) |
| Proroga: scadenze dal 1° al 20 agosto possono essere versate entro il 20 agosto, senza maggiorazione | Vale in generale per i versamenti unitari | **norma certa**: art. 11 D.Lgs. 33/2025 (origine: art. 37 c. 11-bis DL 223/2006) |
| La proroga vale per l'F24EP | Sì, ma l'art. 11 richiama gli articoli 3 e 10 c. 4 e non l'art. 4 | **prassi-interpretazione**: comunicato AdE del 06/08/2008, riferito da [Fisco Oggi](https://www.fiscooggi.it/portale/-/con-la-proroga-di-ferragosto-in-ferie-anche-f24-e-f24-ep), che dice «anche F24 e F24 EP». L'articolo cita un DPCM del 29 luglio 2008 senza numero né estremi di pubblicazione. Il comunicato originale (sito del Dipartimento Finanze) **non è stato letto**: **da verificare** |
| Come si è arrivati alla proroga stabile (art. 3-quater DL 16/2012) | Ricostruzione di fonti secondarie | **da verificare**: non letto sul testo |
| Se il 20 agosto cade di sabato o domenica | Slitta al primo giorno lavorativo? | **da verificare**: nessun testo letto lo dice per questo caso. Si può ipotizzare l'applicazione della regola generale sul giorno festivo |
| Tutte le altre scadenze del mese restano al 16 | Sì: la proroga tocca solo scadenze dal 1° al 20 agosto, cioè i versamenti di luglio | Deriva dal testo dell'art. 11 |

**Contraddizione fra i tool.** F24EP-editor spegne la proroga di default (conferma trovata solo nel comunicato del 2008); l'estrattore la applica sempre ai versamenti di luglio. Sulla fonte letta ha ragione l'estrattore. Il modello dovrebbe avere una **regola datata con fonte** (art. 11 D.Lgs. 33/2025 più comunicato 2008), non una opzione da accendere.

**Per l'ADR 0023.** La regola di scadenza ha fonte; la data di versamento scelta dopo la scadenza calcolata resta un avviso, come deciso.

**Tesoreria unica.** L'ADR chiede se tutti gli enti del target sono in tesoreria unica. La norma dice che l'F24EP è dovuto dagli enti delle tabelle A e B della L. 720/1984; l'elenco delle tabelle **non è stato letto**. **da verificare**: gli enti locali fuori dalle tabelle usano l'F24 ordinario e la regola di scadenza è la stessa (art. 8 D.Lgs. 33/2025), ma serve la delega diversa.

## Tema 2. Trasmissione e annullamento (Allegato 2)

Fonte: **norma certa**, specifiche tecniche F24EP «Allegato 2» (versione dicembre 2016) al provvedimento AdE prot. 154279 del 01/12/2015. La [scheda AdE dell'F24 enti pubblici](https://www.agenziaentrate.gov.it/portale/schede/pagamenti/f24-enti-pubblici-f24_enti_pub/f24_ep_enti-pubblici) linka ancora questa versione alla data del 06/11/2026. Resta **da verificare** che non esista una versione più recente non linkata.

| Regola | Testo (par. 3) |
|---|---|
| Esecuzione del pagamento | Alla data indicata nel record M, per i modelli con saldo maggiore di zero arrivati **entro le 20:00 del secondo giorno lavorativo precedente**. Se arrivano dopo, sono eseguiti e addebitati il secondo giorno lavorativo successivo alla ricezione |
| Saldo uguale a zero | Possono essere inviati **fino alle 24:00 del giorno** indicato nel record M. Se arrivano dopo, i versamenti valgono dal giorno di invio |
| Annullamento | Si chiede sui canali Entratel o Fisconline **entro le 22:00 del secondo giorno lavorativo precedente** (saldo maggiore di zero), oppure **entro le 24:00 del giorno di versamento** (saldo zero). Si raccomanda di inviare in anticipo |
| Fasi dopo l'invio | Ricevuta dei controlli formali (se negativa i pagamenti sono scartati); ricevuta del controllo preventivo dei crediti in compensazione, se ce ne sono; ricevuta dell'addebito sul conto dell'ente. I pagamenti sono eseguiti solo se **tutte le fasi** sono positive |
| Chi può trasmettere | L'ente direttamente o il tesoriere autorizzato; stesso modello non può mescolare pagamenti propri e per conto di un terzo |

Coerenza con ADR 0023: la ricevuta dell'AdE come esito dichiarato e l'annullamento come fatto a sé stanno nel testo. Un esito dichiarato è «trasmesso» ma **non è ancora «eseguito»**: le tre ricevute sono tre eventi distinti. Da tenere presente nel modello (l'ADR parla di una sola ricevuta).

## Tema 3. Compensazione dei crediti del sostituto

### Cosa dicono i testi

| Punto | Esito | Marcatura e fonte |
|---|---|---|
| I codici 150E, 153E, 154E, 170E, 175E si usano **sia a debito sia a credito** | Sì: modalità d'uso «E» | **norma certa**: tabella codici F24EP (18/09/2025 e 01/10/2026), legenda nota (9). I codici 155E/160E/161E (eccedenze di versamento) sono pure «E» |
| 150E, 151E, 152E (erario), 153E (regione, codice regione), 154E (comune, codice catastale) | Rimborsi da assistenza fiscale: estremi non compilati per 150E, riferimento B = anno d'imposta | **norma certa**: tabella AdE, risoluzione 103/E del 09/12/2015 |
| 170E, trattamento integrativo (DL 3/2020, art. 1 c. 4) | Rif. A mese di erogazione (00MM), rif. B anno (AAAA) | **norma certa**: tabella AdE, risoluzione 35/E del 26/06/2020 |
| 175E, somma della L. 207/2024 (art. 1 c. 4) | Stesso formato di 170E; il codice si usa anche a debito per riversare quanto già erogato e poi recuperato | **norma certa**: [risoluzione AdE 9/E del 31/01/2025](https://www.agenziaentrate.gov.it/portale/documents/20143/8410894/RIS_n_9_del_31_01_2025/d093ae0e-6f92-4637-0f29-fc60c0330bf8) |
| Recupero del credito 170E/175E | Avviene «in compensazione ai sensi dell'art. 17 D.Lgs. 241/1997» (ora art. 3 D.Lgs. 33/2025) | **norma certa**: ris. 9/E 2025 per 175E; **prassi-interpretazione**: circ. 29/E del 14/12/2020 par. 7 per 170E |
| Limite di 2 milioni l'anno (art. 3 c. 10 D.Lgs. 33/2025) | Non si applica al 170E | **prassi-interpretazione**: circ. 29/E 2020 par. 7 (cita l'art. 34 L. 388/2000, riprodotto nell'art. 3). Per **175E la risoluzione 9/E tace**: **da verificare** nel testo della L. 207/2024 |
| Rimborsi 730 | Compensati «esclusivamente» con le modalità del versamento unitario, **nel mese successivo** a quello del rimborso, **senza concorrere al limite di 2 milioni**, «nei limiti» dell'art. 83 c. 5 | **norma certa** per il 2027: art. 73 D.Lgs. 141/2026 (origine: art. 15 D.Lgs. 175/2014). Per il 2026 vale la norma originaria (art. 15 c. 1 lett. a D.Lgs. 175/2014), **non letta direttamente**: **da verificare** che il testo 2026 coincida |
| Il credito dei prospetti 730 si somma o si toglie dalle **ritenute d'acconto** del periodo d'imposta in corso | Il testo lega il credito al monte ritenute | **norma certa**: art. 83 c. 5 D.Lgs. 141/2026 (origine: art. 37 D.Lgs. 241/1997) |
| Il saldo del modello non può essere negativo | Un credito non può superare i debiti dello stesso modello | **norma certa** (specifica tecnica): Allegato 2, record V, campo «Saldo debito - credito»: «maggiore di zero o uguale a zero». Un record V corrisponde a una pagina del modello |
| Controlli sui crediti | L'AdE può sospendere fino a 30 giorni la delega con compensazioni a rischio; se il credito non è utilizzabile, la delega **non è eseguita** | **norma certa**: art. 5 c. 5-6 D.Lgs. 33/2025 e Allegato 2 par. 1 b |
| Recupero di un 170E usato in modo indebito | Si versa con 700E (credito e interessi) e 701E (sanzione), con codice ufficio e codice atto | **norma certa**: tabella AdE 01/10/2026 (codici «(***)»). L'estremo della risoluzione istitutiva (indicata da fonti secondarie come la n. 51 del 06/10/2025) **non è stato verificato** |

### La prassi «trattamento integrativo compensato con la CPDEL»

- Nessuna norma o circolare letta vincola il 170E a un debito preciso. La compensazione è **orizzontale**: l'art. 3 c. 1 e c. 5 D.Lgs. 33/2025 (art. 17 D.Lgs. 241/1997) ammette il versamento unitario di imposte, ritenute, addizionali, IRAP e contributi degli enti previdenziali. La circolare 29/E 2020 dice solo che il sostituto recupera «nell'ambito del modello F24»; i suoi esempi usano la sola sezione Erario.
- L'Allegato 2 ammette righe di sezioni diverse nello stesso record V, con saldo non negativo.
- Quindi: la prassi è **compatibile con la norma generale** ma **non è prescritta né citata da una fonte**. Resta una scelta dell'ente. Nessuna norma letta la vieta per i codici INPDAP: **da verificare** con una prassi AdE esplicita sull'uso dei crediti 170E contro causali di sezione INPDAP.
- Per il modello: la scelta del debito contro cui compensare è una **regola configurabile dell'ente**, con un default da decidere. La lettura più vicina alla circolare è compensare contro le ritenute (100E).
- Un'esclusione che non c'entra: l'art. 3 c. 2 lett. c D.Lgs. 33/2025 esclude le aziende committenti dalla compensazione dei **crediti contributivi** verso la Gestione separata. Non riguarda i crediti d'imposta del sostituto.

### Ordine, riporto, esposizione nel 770

- **Ordine.** Nessun testo letto fissa un ordine fra i crediti (150E, 153E, 154E, 170E, 175E) o fra i debiti su cui si compensa. L'unico vincolo è il saldo non negativo del modello. **da verificare** se esistano istruzioni AdE sull'ordine; finora è una scelta del modello.
- **Riporto del credito non assorbito.** Per 170E è esplicito nel quadro SX49 del 770: la colonna 1 riporta il residuo della colonna 7 del 770 precedente. Per i rimborsi 730 (SX2) e per 175E (SX50) il riporto non è descritto nelle sintesi lette. Fonte: sintesi del [quadro SX del 770/2026](https://www.informazionefiscale.it/Quadro-SX-modello-770-istruzioni-compilazione), **prassi-interpretazione**; le istruzioni ufficiali AdE non sono state lette. **da verificare**.
- **Righe del quadro SX** (sempre secondo la sintesi): SX2 col. 1 credito da assistenza fiscale e col. 2 la parte compensata con 150E–154E; SX49 per 170E (col. 3 e 5 riversato, col. 6 utilizzato fino al 16 marzo, col. 7 residuo); SX50 per 175E (col. 3 riversato, col. 6 utilizzato fino al 16 marzo 2026, col. 7 residuo). Le date citate dalla fonte mescolano il 2025 e il 2026 (per esempio, il 16 marzo): **da verificare** sulle istruzioni ufficiali prima di fissare la regola.
- **Esito per l'ADR 0023**: il fermo «se il credito incontra un limite o una regola non ancora modellata» è ben dimensionato. I limiti noti sono tre: saldo non negativo nel record V; limite di 2 milioni (non si applica a 170E né ai rimborsi 730; per 175E da verificare); controllo preventivo dell'AdE con possibile sospensione fino a 30 giorni.

## Tema 4. IRAP degli enti locali (metodo retributivo)

| Punto | Esito | Marcatura e fonte |
|---|---|---|
| Metodo retributivo: base imponibile degli enti non commerciali del metodo di cui all'art. 3 c. 1 lett. e-bis | Retribuzioni al personale dipendente, redditi assimilati a lavoro dipendente, compensi di co.co.co. e di lavoro autonomo occasionale | **norma certa** (letta in sintesi): art. 10-bis c. 1 D.Lgs. 446/1997 su Normattiva. Il testo letterale e le lettere vanno riaperti |
| Esclusioni espresse | Borse di studio e interventi per il diritto allo studio universitario (L. 390/1991); somme esenti che l'articolo richiama (riferimento da riaprire) | **norma certa** (sintesi, da riaprire) |
| Criterio | Di **cassa**: concorrono nell'anno di erogazione | **prassi-interpretazione**: interpello AdE 509/2022, riportato da fonte secondaria |
| Aliquota | **8,5%** | **norma certa**: art. 16 c. 2 D.Lgs. 446/1997 (sintesi Normattiva); l'art. 30 c. 5 la richiama. Seconda fonte: **risoluzione DF 1/2021** del 17/02/2021 (non modificabile dalle Regioni; riportata da [Enti Locali Online](https://www.entilocali-online.it/irap-le-regioni-non-possono-modificare-laliquota-dell85-prevista-per-il-metodo-retributivo-adottato-dalle-amministrazioni-pubbliche/)). Due fonti indipendenti concordi: aliquota confermata |
| Versamento | **Acconto mensile**, pari all'aliquota applicata agli emolumenti corrisposti nel mese precedente, «con le modalità e nei termini stabiliti con decreto del Ministro» | **norma certa** (sintesi): art. 30 c. 5 D.Lgs. 446/1997 |
| Scadenza del 16 e arrotondamento all'euro | 16 del mese successivo, con la regola del giorno festivo | **prassi-interpretazione**: [Il Sole 24 Ore](https://www.ilsole24ore.com/art/fisco-aziende-ssn-tutto-dichiarazione-irap-AF8jbeYB) e [Studio Sigaudo](https://www.studiosigaudo.com/articoli/irap-commerciale-e-irap-istituzionale). Il decreto ministeriale citato dall'art. 30 c. 5 **non è stato individuato**: **da verificare**. L'art. 4 c. 2 D.Lgs. 33/2025 dice solo che l'IRAP degli enti dell'F24EP va con il modello F24EP entro il 16 |
| Codice 380E | Sezione **Regioni (R)**, estremi non compilati, rif. A = mese (00MM), rif. B = anno (AAAA); solo a debito (D); codice regione dalla tabella T0 | **norma certa**: tabella AdE, risoluzione 367/E del 12/12/2007 |
| Amministratori locali | Le indennità di sindaci e assessori concorrono alla base IRAP. L'indennità di fine mandato concorre al netto di 309,87 euro per anno di mandato | **prassi-interpretazione**: risoluzione AdE 29/E del 15/04/2010, riportata da fonte secondaria. Il testo originale **non è stato letto**: **da verificare** |
| Co.co.co. | Concorrono alla base | **norma certa** (sintesi): art. 10-bis c. 1. Nessuna fonte distingue per il netto dei contributi: **da verificare** (una fonte secondaria parla di compenso al netto dei contributi a carico del collaboratore) |
| LSU (lavori socialmente utili) | Nessuna fonte trovata | **da verificare** |
| Ripartizione fra più regioni se i dipendenti prestano servizio in regioni diverse | Il codice regione è un campo del rigo | **da verificare**: la regola di riparto non è stata cercata |

**Per l'ADR 0023.** L'aliquota e il codice hanno fonte; la scadenza e le esclusioni di soggetti restano in parte da verificare. Il «fermo dichiarato» dell'IRAP si può ridurre a due fermi più piccoli: **scadenza** (finché non è individuato il decreto ministeriale) e **riparto per regione**. La base (retribuzioni, assimilati, co.co.co., occasionali) ha una fonte e non richiede fermo.

## Tema 5. Codici tributo e causali del ciclo stipendiale

Fonte unica per la colonna «Esito»: tabella AdE dei codici F24EP aggiornata al [01/10/2026](https://www.agenziaentrate.gov.it/portale/documents/d/guest/tabella-codici-tributo-f24ep-aggiornata-al-1-ottobre-2026) (confrontata con la versione del 18/09/2025 per i codici sotto). **norma certa** salvo diversa indicazione. Nella tabella ci sono anche codici sospesi: la riga indica la modalità (D = debito, E = debito e credito).

**Correzione (ticket #54, 07/11/2026).** Dove questa tabella dice «estremi = codice catastale» (384E, 385E) o «estremi = sigla provincia» (P201 e le altre causali INPDAP), il valore va nel campo **«Codice»** del rigo, non negli estremi: così l'Allegato 2 e la tabella AdE, rilette nel ticket #54. Per 384E gli estremi sono «non compilare», per P201 sono facoltativi.

| Codice | Denominazione e uso | Esito |
|---|---|---|
| **384E** | Addizionale comunale IRPEF trattenuta dai sostituti, **saldo**. Sezione Enti locali (S), estremi = codice catastale, rif. A = mese (00MM), rif. B = anno. D | Confermato |
| **385E** | Stessa addizionale, **acconto**. D | Confermato |
| 127E, 128E | Addizionale comunale su 730, acconto e saldo. D | Confermato |
| 381E | Addizionale regionale IRPEF trattenuta dai sostituti (sezione Regioni, codice regione). D | Confermato |
| 100E, 102E, 104E | Ritenute su redditi da lavoro dipendente e assimilati, arretrati, lavoro autonomo. D | Confermato |
| **380E** | IRAP. Vedi il tema 4 | Confermato |
| **P201** | Cassa CPDEL, «contributi obbligatori». Sezione INPDAP (Q), estremi = sigla provincia (tabella T2), periodo di riferimento A e B in formato MMAAAA. D | Confermato come causale generica |
| **1% aggiuntivo** | **Nessuna causale dedicata** nella tabella: la denominazione di P201 è «contributi obbligatori»; P206 è un'altra cosa («contribuzione 10% L. 166/91») | Resta **da verificare**: che il 1% vada dentro P201 (come fa F24EP-editor) non è né confermato né smentito da una fonte |
| **P608** | Cassa INADEL, «contributo TFR su elementi accordo quadro 29/7/99». D | Esiste e ha questo significato (risoluzione 96/E del 07/10/2010) |
| **P632** | Cassa INADEL, «contributo su ulteriori elementi imponibili TFR». D | Esiste e ha questo significato. Che il «TFR 6,91» di F24EP-editor e dell'estrattore sia proprio P632 è una lettura **prassi-interpretazione** (la denominazione è compatibile, nessuna norma citata) |
| P607, P909 | INADEL TFS; Cassa unica del credito. D | Esistono |
| **C10** e **CXX** | Gestione committenti (INPS), D. Estremi = codice sede INPS, rif. A = mese e anno di pagamento del compenso (MM/AAAA) | Esistono. La regola di scelta: vedi sotto |
| **179E** (e gemelli 180E ss.) | Imposta sostitutiva su IRPEF e addizionali sul **trattamento accessorio** del personale non dirigenziale delle amministrazioni pubbliche (L. 199/2025, art. 1 c. 237). D; rif. A = mese della trattenuta, rif. B = anno | **Nuovo**, dal 29/01/2026 (ris. 4/E 2026). Non è nel perimetro dell'ADR 0023: **da portare nella mappatura** (ADR 0022) |
| 700E, 701E | Recupero del 170E indebito (credito e interessi, sanzione) | Vedi il tema 3 |

**Gestione separata: C10 o CXX.** L'unica fonte INPS letta, la circolare 88/2023 (par. su un'altra categoria di collaboratori), dice di usare **CXX** per «l'aliquota complessiva al 27,03%» e **C10** per «l'aliquota del 24%». L'aliquota è del 2023 e **non va usata per il 2026**. La circolare INPS 8 del 03/02/2026 con le aliquote aggiornate **non è stata letta**. Una guida secondaria collega la distinzione alla copertura previdenziale (C10 per chi ha altra tutela o è pensionato, CXX per chi è privo di altra copertura). Le due letture sono coerenti, ma servono per i co.co.co. ordinari: **da verificare** sulla circolare 8/2026. La lista collaboratori (ADR 0015) deve portare l'aliquota come fatto dell'incarico, non come costante del codice.

**Addizionale comunale a saldo.** 384E per il saldo e 385E per l'acconto, ambedue sezione Enti locali con codice catastale: **la domanda dell'ADR è chiusa**. Per il rimborso al dipendente dell'addizionale comunale da assistenza fiscale il codice è 154E (a credito); gli interessi della dilazione sono in 125E.

## Tema 6. Effetto dei testi unici dal 01/01/2027

Cosa leggere con cura: il ticket parlava del «TU D.Lgs. 117/2026».

- **D.Lgs. 117/2026** (19 giugno 2026) è il **nuovo TUIR**. Si applica dal 01/01/2027 e riscrive la numerazione delle norme sui redditi. Per esempio, il D.Lgs. 141/2026 cita i redditi di lavoro dipendente e assimilati come «articoli 51 e 52» del nuovo TUIR, dove oggi sono gli artt. 49 e 50. Le regole datate del modello che citano il TUIR vanno rinumerate. Fonte: GU del D.Lgs. 141/2026; **norma certa** per questa osservazione, **prassi-interpretazione** per la data di applicazione del 117 (riportata da fonti secondarie).
- **D.Lgs. 33/2025** (testo unico versamenti e riscossione): le regole di versamento. Si applica dal **01/01/2027**; il rinvio dal 2026 è dell'art. 4 DL 200/2025 (fonti secondarie e nota di Normattiva). L'art. 240 abroga, alla data di entrata in vigore, gli artt. da 17 a 28 e 30 del D.Lgs. 241/1997, l'art. 32-ter DL 185/2008 e l'art. 37 c. 11-bis DL 223/2006. **norma certa** (testo letto).
- **D.Lgs. 141/2026** (testo unico adempimenti e accertamento, 05/08/2026, GU del 06/08/2026): contiene la compensazione dei rimborsi da assistenza fiscale (art. 73, ex art. 15 D.Lgs. 175/2014) e l'assistenza fiscale dei sostituti (art. 83). Si applica dal 01/01/2027. **norma certa** (testo letto).

Tabella di corrispondenza per le regole datate:

| Regola | Fonte fino al 31/12/2026 | Fonte dal 01/01/2027 |
|---|---|---|
| Versamento unitario e compensazione | art. 17 D.Lgs. 241/1997 | art. 3 D.Lgs. 33/2025 |
| Scadenza del 16 (generale) | art. 18 D.Lgs. 241/1997 | art. 8 D.Lgs. 33/2025 |
| F24EP e scadenza del 16 | art. 32-ter DL 185/2008 | art. 4 D.Lgs. 33/2025 |
| Proroga al 20 agosto | art. 37 c. 11-bis DL 223/2006 | art. 11 D.Lgs. 33/2025 |
| Rimborsi da assistenza fiscale in compensazione | art. 15 D.Lgs. 175/2014 | art. 73 D.Lgs. 141/2026 |
| Limite di 2 milioni | art. 1 c. 72 L. 234/2021 | art. 3 c. 10 D.Lgs. 33/2025 |

Effetto per il modello: **il contenuto non cambia**, cambia il riferimento. Basta una regola datata con due fonti e due intervalli di validità, che è già il meccanismo dell'ADR 0022. Dall'1/1/2027 i riferimenti degli ADR 0023 e 0024 alle vecchie norme vanno aggiornati. **da verificare**: se esista un testo unico dell'IRAP che sostituisca il D.Lgs. 446/1997 (non cercato), perché è la norma su cui poggia il tema 4.

## Esito per ADR 0023: le voci «Da verificare»

| Voce dell'ADR | Esito della ricerca |
|---|---|
| Scadenza del 16 e slittamento | **Chiusa**: art. 4 c. 2 D.Lgs. 33/2025; vale anche per le festività infrasettimanali |
| Proroga di Ferragosto per l'F24EP | **Chiusa per la prassi**: vale (comunicato AdE 2008). Estrattore giusto, F24EP-editor da correggere. Resta da leggere il comunicato originale |
| Ordine, limiti e riporto delle compensazioni (150E, 153E, 154E, 170E, 175E) | **Parziale**: limiti e vincolo del saldo chiusi. Ordine e riporto sono scelte del modello, da riscontrare sulle istruzioni 770. Limite per 175E da verificare |
| Prassi «integrativo compensato con la CPDEL» | **Né confermata né scartata**: compatibile con la norma generale, nessuna fonte specifica |
| IRAP: aliquota, base, soggetti esclusi | **Aliquota e base chiuse**; scadenza e esclusioni (LSU, riparto regioni) da verificare |
| Codice dell'addizionale comunale a saldo | **Chiusa**: 384E (saldo), 385E (acconto) |
| Causali C10 o CXX | **Aperta**: dipende dall'aliquota; da verificare sulla circolare INPS 8/2026 |
| P608, P632, 1% in P201 | **P608 e P632 confermate**; 1% senza causale dedicata, da verificare |
| Enti del target in tesoreria unica | **Aperta**: elenco delle tabelle L. 720/1984 non letto |

## Nuovi punti emersi (non nel ticket)

1. **Tre ricevute, non una.** L'esito «eseguito» richiede controlli formali, controllo dei crediti ed esito dell'addebito (Allegato 2, par. 1). Da riflettere nell'esito dichiarato dell'ADR 0023.
2. **Codice 179E** e gemelli: nuovo debito del ciclo stipendiale per il personale non dirigenziale (L. 199/2025). Da mappare.
3. **Codici 700E e 701E** per recuperare un 170E indebito: l'ADR non li cita.
4. **Controllo preventivo dei crediti:** una delega con compensazione può restare sospesa fino a 30 giorni (art. 5 c. 5 D.Lgs. 33/2025). Il modello non può considerare pagata una delega solo perché inviata.
5. **Festivi infrasettimanali** nella scadenza: oggi ignorati dall'estrattore.

## Fonti

Primarie, lette per intero:

- AdE, specifiche tecniche F24EP, **Allegato 2** (dicembre 2016), provv. prot. 154279 del 01/12/2015 ([PDF](https://www.agenziaentrate.gov.it/portale/documents/20143/344093/Provvedimento+del+1122015+F24+EP_allegato+2+-+specifiche+tecniche+F24+EP+dicembre+2016+(2).pdf/92a0df69-e9f4-adb5-5339-415ada83da88)).
- AdE, tabella dei codici F24EP, aggiornata al [01/10/2026](https://www.agenziaentrate.gov.it/portale/documents/d/guest/tabella-codici-tributo-f24ep-aggiornata-al-1-ottobre-2026) e al [18/09/2025](https://www.agenziaentrate.gov.it/portale/documents/d/guest/tabella-codici-tributo-f24ep-aggiornata-al-18-settembre-2025).
- AdE, risoluzione 9/E del 31/01/2025 (codice 175E).
- AdE, circolare 29/E del 14/12/2020 (recupero del trattamento integrativo, 170E).
- D.Lgs. 24 marzo 2025, n. 33, [testo unico versamenti e riscossione](https://www.agenziaentrateriscossione.gov.it/export/.files/it/gruppo/GU-DLGS_33_2025-TU-VERSAMENTI-E-RISCOSSIONE.pdf) (GU n. 71 del 26/03/2025), artt. 3, 4, 5, 8, 10, 11, 240 e 243.
- D.Lgs. 5 agosto 2026, n. 141, testo unico adempimenti e accertamento (GU n. 181 del 06/08/2026), artt. 73 e 83.
- INPS, circolare 88 del 31/10/2023 (solo per la regola C10/CXX, in un contesto diverso).

Primarie, lette in sintesi (Normattiva): D.Lgs. 446/1997 artt. 10-bis, 16, 30; D.Lgs. 241/1997 art. 18.

Prassi e secondarie (da riaprire prima di usarle in una regola):

- [Fisco Oggi, «Con la proroga di Ferragosto, in ferie anche F24 e F24 EP»](https://www.fiscooggi.it/portale/-/con-la-proroga-di-ferragosto-in-ferie-anche-f24-e-f24-ep), 06/08/2008 (comunicato AdE).
- [Enti Locali Online](https://www.entilocali-online.it/irap-le-regioni-non-possono-modificare-laliquota-dell85-prevista-per-il-metodo-retributivo-adottato-dalle-amministrazioni-pubbliche/) sulla risoluzione DF 1/2021.
- [Il Sole 24 Ore](https://www.ilsole24ore.com/art/fisco-aziende-ssn-tutto-dichiarazione-irap-AF8jbeYB) e [Studio Sigaudo](https://www.studiosigaudo.com/articoli/irap-commerciale-e-irap-istituzionale) sull'IRAP degli enti.
- [Informazione Fiscale, quadro SX del 770/2026](https://www.informazionefiscale.it/Quadro-SX-modello-770-istruzioni-compilazione).
- Risoluzione AdE 29/E del 15/04/2010 e interpello 509/2022, riportati da fonti secondarie.

Pista interna (non citabile): vault-pa, note sul quadro SX del 770/2026 e sulle quadrature F24EP.
