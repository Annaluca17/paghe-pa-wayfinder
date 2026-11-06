# Regimi per titolo di compenso: amministratori, co.co.co., LSU/LPU, segretario

Ticket: #19 (mappa #1). Data ricerca: 06/11/2026.

## Domanda

Per ciascun titolo di compenso diverso dal lavoro dipendente del comparto (amministratori locali, co.co.co., LSU/LPU, segretario in titolarità, in convenzione e a scavalco): quale regime previdenziale, assicurativo, fiscale e contabile si applica, con quali flussi e adempimenti, e che cosa cambia dal 01/01/2027? Questo documento riporta fatti riscontrati. Le decisioni spettano all'intervista e alle ADR.

## Avvertenza sul metodo

**Legenda**

- **norma certa**: letta sul testo della norma, del CCNL, della circolare o dell'istruzione ufficiale.
- **prassi-interpretazione**: magistratura contabile, rassegne, prassi o lettura del ricercatore. Vale anche quando la conclusione è una deduzione da testi certi.
- **da verificare**: non riscontrato o riscontrato in modo incompleto. È indicato che cosa è stato provato.

**Regola sugli importi.** Per importi e percentuali sono richieste due fonti indipendenti. Dove è stato letto solo il testo primario la marcatura è «**norma certa** il testo; seconda fonte **da verificare**».

**Come sono state lette le fonti.** Ogni riferimento tra parentesi quadre rinvia alla sezione Fonti, che distingue i testi letti direttamente (D) da quelli visti solo da estratti di ricerca o riproduzioni (E).

**Accessi, 06/11/2026**

- Normattiva raggiungibile: portale con `!vig=2026-11-06` e API open data. Gli articoli lunghi sono paginati a 100 commi. Tramite `atto/caricaArticolo` sono stati letti i commi 1-1000 di L. 234/2021, i commi 501-600 di L. 296/2006 e i commi 401-500 di L. 160/2019.
- Raggiungibili e scaricati: RGS, INPS (PDF), Agenzia delle Entrate.
- `aranagenzia.it`: pagine con HTTP 403, PDF raggiungibile. Il CCNL 16/07/2024 è letto dalla copia pubblicata da una Prefettura.
- Gazzetta Ufficiale: pagina dell'atto caricata lato client, testo non estratto. **Il D.M. 17/03/2020 non è stato letto sul testo.**
- INPS: la nota operativa INPDAP n. 6/2008 non è stata trovata. Il messaggio 3268/2019 è letto da una riproduzione.
- Allegato tecnico UniEmens (Appendice B, codici): non scaricato. I codici di tipo rapporto vengono da circolare INPS e istruzioni CU.

**Vault.** `vault-pa` è stato usato solo come pista. Nessuna affermazione poggia sul vault: Conto Annuale, CU e 770 sono stati riscontrati sui PDF ufficiali.

**Limiti della circolare RGS.** Il testo dei PDF è estratto con `pdftotext`. Nelle tabelle a più colonne l'associazione tra voce e codice può essere disallineata. Dove conta è segnalato.

## Sintesi

Tabella per titolo. Le marcature sono nei findings. Per il segretario titolare e in convenzione le righe fiscale, CU, previdenza e flusso sono **prassi-interpretazione**: seguono dalla natura di rapporto di lavoro dipendente, senza un testo letto dedicato.

| | Amministratore | Co.co.co. | LSU/LPU | Segretario titolare | Segretario in convenzione | Segretario a scavalco |
|---|---|---|---|---|---|---|
| Natura | Mandato, non lavoro | Lavoro autonomo coordinato | Nessun rapporto di lavoro | Dipendente: rapporto di lavoro con il Ministero, rapporto di servizio con l'ente | Come titolare, una sola titolarità su più enti | Titolare altrove, incarico temporaneo |
| Chi paga | Ente | Ente | **INPS l'assegno** (o ente se autofinanziato); ente l'integrazione | Ente | Di norma il capo convenzione, poi recupera | Ente dello scavalco, per la sola indennità |
| Fiscale oggi | Art. 50 c. 1 lett. g) (gettoni: anche lett. f) | Art. 50 c. 1 lett. c-bis) | Art. 50 c. 1 lett. l) | Art. 49 | Art. 49 | Art. 49 |
| CU | **Punto 4**, art. 13 c. 5 | Punti 1-2, art. 13 c. 1 | Punti 1-2; regime agevolato punti 496-499 | Punti 1-2 | Punti 1-2 | **da verificare** |
| Previdenza | Solo art. 86: **non sull'indennità** | Gestione separata 35,03% (2/3-1/3) | Nessuna ordinaria individuata: **da verificare** | Gestione pubblica, ListaPosPA | Come titolare | **da verificare** |
| Flusso | ListaPosPA (c. 1) o ListaCollaboratori tipo 04/19 (c. 2) o cassa o bollettino | ListaCollaboratori tipo 11 | **da verificare** | ListaPosPA | ListaPosPA | **da verificare** |
| Conto Annuale | Fuori (solo oneri, se dipendente dell'ente) | Scheda 1 + Tab. 14 L111 | Tab. 2 + Tab. 14 P065 | Tab. 1, 12, 13, 14, 15 | Capofila: Tab. 1 e Tab. 3 out; altri: Tab. 3 in | Tab. 13 S740 senza organico |
| Piano dei conti | U.1.03.02.01.001 | U.1.03.02.12.003 | U.1.03.02.12.002 | Macroaggregato 1.01, nessuna voce dedicata | Rimborsi U.1.09.01.01.001 / E.3.05.02.01.001 | **da verificare** |
| Numeratore RGS A33 | No | Sì | Sì | Sì | Rimborsi non estratti: vedi 12 | **da verificare** |

**Punti che possono cambiare il modello**

1. **L'imponibile previdenziale dell'amministratore non è l'indennità.** Art. 86 c. 1: oneri su aspettativa. Art. 86 c. 2: quota forfettaria sul minimale, verso la forma pensionistica della persona, che può essere una cassa privata. Le condizioni dipendono da carica, popolazione e situazione della persona. Non risulta una ritenuta previdenziale in busta (**prassi-interpretazione**). Da tutto questo restano fuori, per esempio, gli assessori dei comuni fino a 10.000 abitanti (**norma certa**, art. 86 c. 1).
2. **L'assegno LSU non è pagato dall'ente.** L'ente paga solo l'eventuale integrazione e l'INAIL, e può avere LSU con spesa zero che comunque rileva in Tab. 2.
3. **Tre rimandi della domanda sono superati.** Art. 45 CCNL 16/05/2001 sostituito da art. 63 CCNL 16/07/2024, che fissa la retribuzione aggiuntiva al 25%. Art. 41 e 42 sostituiti da artt. 38 e 39 CCNL 23/02/2026. D.Lgs. 468/1997 è abrogato salvo gli artt. 7-8 per i progetti pregressi.
4. **Il segretario non ha un fondo.** Il risultato è a carico del bilancio, **ma nel limite dell'art. 23 c. 2**. La retribuzione aggiuntiva per la convenzione sta fuori da Tab. 15.
5. **Le lettere del nuovo testo unico cambiano:** c-bis) → d), f) → g), g) → i), l) → o), art. 17 → art. 19. La norma riporta il proprio raccordo in testa a ogni articolo.
6. **Le co.co.co. sono uscite dalla Tab. 2A** del Conto Annuale. Il documento #10 va aggiornato.
7. **Nessuno di questi titoli sta nel macroaggregato 1.01**, tranne il segretario. Il numeratore RGS della Scheda A33 prende però LSU e co.co.co., non gli amministratori né i rimborsi 1.09.

## Findings

### A. Amministratori locali

#### 1. Indennità, gettoni e fondo statale

Vigenza: art. 82 TUEL testo dal 01/01/2020 [N1]; L. 234/2021 art. 1, pagina letta al 06/11/2026 [N2]; D.M. 119/2000 testo dal 28/05/2000 [N3]. Non risulta fine vigenza.

- Indennità di funzione per sindaco, presidenti, componenti degli organi esecutivi. **Dimezzata per i lavoratori dipendenti che non abbiano richiesto l'aspettativa** (art. 82 c. 1). **norma certa**
- Gettone di presenza per i consiglieri, per consigli e commissioni. Tetto mensile: un quarto dell'indennità **massima** prevista per il rispettivo sindaco o presidente (art. 82 c. 2). **norma certa**
- Le indennità di funzione del Capo IV non sono cumulabili tra loro: opzione per una delle due, o per il 50% di ciascuna (c. 5). Con indennità di funzione nessun gettone per organi collegiali dello stesso ente (c. 7). Gettone subordinato alla partecipazione effettiva (c. 11). **norma certa**
- Fine mandato: integrazione per sindaci e presidenti di provincia pari a un'indennità mensile per ogni anno di mandato (art. 82 c. 8 lett. f; D.M. 119/2000 art. 10, proporzionale per periodi inferiori). **norma certa**
- L. 234/2021 art. 1:
  - c. 583: dal 2024, indennità dei sindaci di regioni a statuto ordinario parametrata al trattamento dei presidenti di regione. Metropolitani 100%; capoluoghi di regione e di provincia oltre 100.000 abitanti 80%; capoluoghi fino a 100.000 70%; oltre 50.000 45%; 30.001-50.000 35%; 10.001-30.000 30%; 5.001-10.000 29%; 3.001-5.000 22%; fino a 3.000 16%. **norma certa** il testo; seconda fonte **da verificare**.
  - c. 584: 45% nel 2022 e 68% nel 2023 delle misure del c. 583. **norma certa**
  - c. 585: vicesindaci, assessori e presidenti di consiglio seguono con le percentuali del D.M. 119/2000. **norma certa**
- D.M. 119/2000: art. 2 maggiorazioni 5%, 3% e 2%, cumulabili; art. 4 vicesindaci e assessori; art. 5 presidenti di consiglio; art. 11 aumenti e diminuzioni. **norma certa**. La tabella A non è stata letta.
- **Fondo statale.** L. 234/2021 c. 586: il fondo dell'art. 57-quater c. 2 d.l. 124/2019 è incrementato di 100 milioni nel 2022, 150 nel 2023 e 220 dal 2024, a titolo di concorso. C. 587: ripartizione con decreto; il comune **riversa allo Stato l'importo non utilizzato**. **norma certa**
  - Rilevanza: è un'entrata di bilancio con destinazione e obbligo di rendicontazione di fatto, non un dato di paghe. Serve per il capitolo e per la verifica del riversamento. **prassi-interpretazione**
  - Voce di entrata, decreti di riparto e incidenza sulle entrate correnti del rapporto art. 33: **da verificare**. Non cercati.
- Riduzione ex art. 5 c. 7 d.l. 78/2010 e altre misure citate nelle note all'art. 82: non esaminate. **da verificare**

#### 2. Oneri art. 86, permessi, rimborsi

Vigenza: art. 79 testo dal 06/12/2017, art. 80 dal 02/03/2001, art. 81 dal 01/01/2008, art. 84 dal 31/07/2010, art. 86 dal 15/08/2015 [N1]. **norma certa**

**Art. 86 c. 1: dipendenti in aspettativa non retribuita**

- L'ente versa a proprio carico gli oneri assistenziali, previdenziali e assicurativi «ai rispettivi istituti», comunicandolo ai datori di lavoro. Cariche: sindaci, presidenti di provincia, comunità montane, unioni e consorzi; assessori provinciali; **assessori di comuni oltre 10.000 abitanti**; **presidenti di consiglio di comuni oltre 50.000**; presidenti di consiglio provinciale; alcune figure circoscrizionali e di aziende. **norma certa**
- I consiglieri dell'art. 77 c. 2 che chiedono l'aspettativa pagano **per intero a proprio carico** (art. 81). **norma certa**. Modalità: circolare INPS 133/2012, causale F24 indicata in estratto. **da verificare** [I5]
- Flusso.
  - Il Ministero dell'interno indica come destinatario l'istituto cui l'amministratore è iscritto: ex INPDAP per i pubblici, INPS per i privati [M1, estratto]. **prassi-interpretazione**
  - Le istruzioni CU indicano che compila la certificazione previdenziale l'amministrazione del mandato, se ha denunciato o versato, con il rinvio alla nota operativa INPDAP n. 6/2008, e nel quadro gestione pubblica elencano la contribuzione art. 86 tra i casi particolari [A1]. **norma certa**
  - Quindi per il dipendente pubblico in aspettativa il versamento è dell'ente del mandato e non è un rimborso al datore. La sede tecnica coerente è ListaPosPA. **prassi-interpretazione**
  - Codice e modalità esatte in ListaPosPA, e se ente del mandato e datore coincidono: **da verificare**. Provato: documento tecnico UniEmens 4.33 (nessuna indicazione nel ramo letto), ricerca del testo della nota 6/2008. Per i privati il documento indica `TipoLavStat` E000 per chi è in aspettativa per funzioni elettive [I3]. **norma certa**

**Art. 86 c. 2: non dipendenti**

- Cifra forfettaria annuale per quote mensili, stesse cariche del c. 1, verso la forma pensionistica di iscrizione. Criteri nel D.M. 25/05/2001 [N4]. **norma certa** l'art. 86; D.M. letto da riproduzione (**prassi-interpretazione** la fedeltà).
- Il D.M. elenca INPS artigiani, commercianti e coltivatori diretti, e le casse private. **Il versamento può quindi andare a una cassa privata.** Riproduzione.
- Circolare INPS 205/2001: base è il minimale di artigiani e commercianti, anche per la Gestione separata; quote mensili entro il 16; per gestione separata F24 e denuncia, per artigiani e commercianti bollettino postale. Le modalità sono quelle del 2001: F24 EP e UniEmens per la Gestione separata risultano da fonti successive; bollettino oggi **da verificare** [I2]. **norma certa** al 2001.
- Contrasto interpretativo: la Corte dei conti (Liguria 21/2019) richiede l'astensione dal lavoro, la Cassazione (ord. 24615/2023) no. L'Osservatorio finanza e contabilità, giugno 2024, indica di seguire la Cassazione e parla di quota spettante ai liberi professionisti «su loro richiesta» [M2]. **prassi-interpretazione**
- Il Ministero esclude i rapporti parasubordinati dal c. 2 [M1, estratto]. **da verificare**

**Altri rimborsi e oneri**

- **Rimborso al datore per i permessi.** Le assenze dei commi 1, 3 e 4 dell'art. 79 sono retribuite dal datore. Gli oneri sono a carico dell'ente solo per dipendenti **da privati o da enti pubblici economici**; rimborso su richiesta documentata, entro 30 giorni, esente IVA (art. 80). Permessi: tempo della seduta; 24 o 48 ore mensili; ulteriori 24 ore non retribuite (art. 79). **norma certa**
- **Quota TFR.** L'ente rimborsa al datore la quota annuale entro un dodicesimo dell'indennità annua; il resto è dell'amministratore (art. 86 c. 3). **norma certa**
- **Rimborsi di viaggio.** Art. 84 c. 1: missioni fuori dal capoluogo, spese di viaggio effettivamente sostenute, autorizzazione, misura da decreto. C. 2: liquidazione del dirigente su richiesta documentata. C. 3: residenti fuori capoluogo. **norma certa**. Decreto di misura e sua vigenza: **da verificare**.
- **Assicurazione e spese legali.** Facoltative e condizionate (art. 86 c. 5). **norma certa**

#### 3. Gestione separata e INAIL

- **Riferimento dell'obbligo.** Per gli amministratori la fonte è l'art. 86 c. 2 TUEL con il D.M. 25/05/2001, non una lettura diretta dell'art. 2 c. 26 L. 335/1995 sull'indennità. La tabella INPS porta la dicitura «Amministratore di enti locali (D.M. 25.5.2001)». **norma certa** il testo; **prassi-interpretazione** la conclusione.
- **Chi vi rientra.** Non dipendente, nelle cariche del c. 1, iscritto alla Gestione separata alla data dell'incarico. Per gli altri la gestione o cassa propria. **prassi-interpretazione** su [I2, N4].
- L'art. 50 c. 1 lett. c-bis) non comprende le cariche elettive, che stanno in lett. g). Una sintesi di ricerca riportava, in forma generica e senza testo INPS, che indennità e gettoni possono generare contributi in Gestione separata: non è stato possibile risalire alla fonte. Testo INPS che escluda espressamente l'indennità dalla Gestione separata: non trovato. **da verificare**
- **Aliquote 2026** (circolare INPS n. 8 del 03/02/2026 [I1]; valori dal 01/01/2026 al 31/12/2026):

| Tipo rapporto | Descrizione | IVS | Aggiuntive | Totale |
|---|---|---|---|---|
| 04 | Amministratore di enti locali (D.M. 25.5.2001) | 33,00 | 0,50 + 0,22 | **33,72%** |
| 19 | Amministratore di enti locali iscritto come libero professionista | 25,00 | 0,50 + 0,22 + 0,35 | **26,07%** |

  **norma certa**; confermata da un riepilogo di terzi [T1]. Tipo 19: messaggio INPS 3268/2019 [I4, riproduzione].
- **Massimale 2026:** 122.295,00 euro. **Minimale 2026:** 18.808,00 euro. Contributo annuo sul minimale: 6.342,06 per il 33,72%; 4.903,25 per il 26,07% (circolare par. 6). **norma certa**; riepilogo di terzi concorde.
- **Ripartizione.** La regola 1/3-2/3 riguarda i committenti in generale. Per l'art. 86 c. 2 la norma pone il pagamento a carico dell'ente. **norma certa** l'art. 86; assenza di quota a carico dell'amministratore **prassi-interpretazione**.
- **INAIL.** La Cassazione, sez. lav., n. 22036/2025 afferma che il sindaco non rientra tra i tutelati del D.P.R. 1124/1965, ma che il dipendente in aspettativa per l'intero mandato ha diritto alla tutela assicurativa obbligatoria ex art. 86 c. 1 e 2 [G1, riproduzione]. Il c. 5 riguarda la copertura facoltativa. **prassi-interpretazione**. Modalità di premio e posizione INAIL per l'ente: **da verificare**.

#### 4. Fiscale

Vigenza dei testi TUIR e D.P.R. 600: fino al 31/12/2026; dal 01/01/2027 vedi 13.

- **Art. 50 c. 1.** Lett. g): indennità comunque denominate per cariche elettive e funzioni della L. 816/1985, e vitalizi. Lett. f): indennità, gettoni e compensi corrisposti da Stato, regioni, province e comuni per pubbliche funzioni, se non resi nell'arte o professione. **norma certa** [N5]
- **Art. 52 c. 1 lett. b).** Non concorrono le somme a titolo di rimborso spese a titolari di cariche elettive, se erogazione e criteri sono disposti dagli organi competenti. **norma certa** [N5]
- **Rimborsi art. 84:** rientrano in questa previsione. **prassi-interpretazione**. Trattamento del c. 3 per residenti fuori capoluogo: **da verificare**.
- **Art. 24 c. 1 D.P.R. 600.** Ritenuta **a titolo d'acconto** all'atto del pagamento, con rivalsa, sulla parte imponibile; si applicano in quanto compatibili le regole dell'art. 23. **norma certa** [N6]
- **Detrazioni.** Art. 13 c. 5 TUIR, **non** il c. 1. **norma certa** [N5]
- **Addizionali.** Le istruzioni CU certificano addizionali su questi redditi. **norma certa** [A1]. Regola art. 50 D.Lgs. 446/1997 e art. 1 D.Lgs. 360/1998 non letti: **da verificare**.
- **Art. 26 L. 724/1994.** Soppressi i regimi fiscali particolari per le indennità (richiamato da art. 86 c. 4). **norma certa** [N7]
- **Indennità di fine mandato.** Risoluzione AdE 29/E del 15/04/2010 [A3] **norma certa** come prassi amministrativa:
  - redditi assimilati art. 50 lett. g);
  - tassazione separata art. 17 c. 1 lett. a), che richiama le lettere a), d) e g) dell'art. 50;
  - imponibile ridotto ex art. 19 c. 2-bis di 309,87 euro per anno;
  - **concorre alla base IRAP** in quel medesimo ammontare.
- **IRAP.**
  - Art. 10-bis c. 1 D.Lgs. 446/1997: base = retribuzioni, redditi assimilati dell'allora art. 47, co.co.co. e lavoro autonomo occasionale. **norma certa** [N8]
  - Art. 16 c. 2: aliquota 8,5%. **norma certa** [N8]. Seconda fonte: circolare RGS controllo IN4 sull'8,5%. [R1]
  - Risoluzione 16/02/2001 n. 24, richiamata da 29/E: per gli assimilati la base è quella IRPEF, a prescindere dalla rilevanza previdenziale. **norma certa** come riportata in [A3].

#### Verifica del tool `indennita-amministratori`

Controllo chiesto da Luca nel grilling, domanda 11. Letto il sorgente di `index.html` (commit `6d19640`, unico del repo, senza novità sul remoto il 06/11/2026). È l'unico tool del portale su questo tema.  
La copia in `Progetto HR Tools/calcolo indennità amministratori/` è diversa e più vecchia (12/07): non è stata confrontata riga per riga.

- **Che cosa contiene:** base 13.800 euro, percentuali per fascia dell'art. 1 c. 583 L. 234/2021, percentuali di vicesindaco, assessori e presidente del consiglio dal D.M. 119/2000, maggiorazioni art. 2 cumulabili, dimezzamento, tetto del gettone, una mensilità di fine mandato per il sindaco. Sono la pista dell'importo atteso.
- **Che cosa non contiene:** art. 86 TUEL, quota forfettaria, gestione separata, IRAP, ritenute, permessi e rimborsi. Il README promette «oneri a carico dell'ente», ma il codice non li calcola e la nota a video li esclude. Conferma quanto scritto in `conoscenza-tool.md`.
- **Punti da riscontrare prima del corpus (da verificare):**
  - il tool applica le maggiorazioni prima di calcolare il tetto del gettone, mentre l'art. 82 c. 2 parla di indennità massima: non è chiaro se la massima comprenda le maggiorazioni;
  - il tool stesso dichiara controversa l'applicabilità delle maggiorazioni dopo il c. 583;
  - il tool non distingue le regioni a statuto speciale, e il c. 583 riguarda le ordinarie;
  - la base di 13.800 euro nel codice è un valore fisso, senza vigenza, e richiede una seconda fonte.
- **Pista non riscontrata:** il monitor normativo del 05/11/2026 segnala una nota ANCI sui rimborsi di viaggio e soggiorno degli amministratori, con allineamento ai parametri del CCNL dirigenti. Riguarda la misura dell'art. 84 TUEL, oggi **da verificare**.

### B. Co.co.co.

#### 5. Ammissibilità, fiscale, contributi

- **Art. 7 c. 5-bis D.Lgs. 165/2001.** Divieto di contratti di collaborazione con prestazioni esclusivamente personali, continuative e **organizzate dal committente anche quanto a tempi e luogo**. Nulli, responsabilità erariale. Applicazione dal 01/07/2019 (art. 22 c. 8 D.Lgs. 75/2017 come modificato, ultima data nelle note lette). **norma certa** [N9]
- **Art. 7 c. 6.** Solo incarichi individuali con contratti di lavoro autonomo ad esperti di particolare e comprovata specializzazione, con presupposti di legittimità; c. 6-bis procedure comparative. **norma certa** [N9]. La circolare RGS riassume: oggetto coerente, impossibilità di risorse interne, natura temporanea e altamente qualificata, niente rinnovo, durata, oggetto e compenso determinati preventivamente. [R1] **norma certa**
- **Art. 2 D.Lgs. 81/2015.** La riconduzione a subordinazione non si applica alle PA (c. 4). **norma certa** [N10]
- **Che cosa resta.** Nell'ente locale resta ammessa la collaborazione autonoma nel perimetro del c. 6, non organizzata dal committente. Il tipo rapporto 11 INPS esiste ancora. **prassi-interpretazione**
- **Requisiti di forma:** scritto, pubblicità: art. 15 D.Lgs. 33/2013, art. 3 c. 18 L. 244/2007, art. 1 c. 173 L. 266/2005 non letti. **da verificare**
- **Fiscale.** Art. 50 c. 1 lett. c-bis) (rapporto unitario, continuativo, senza mezzi organizzati, retribuzione periodica prestabilita; esclusa se nell'oggetto dell'arte o professione). Art. 13 c. 1 per la detrazione. **norma certa** [N5]
- **Art. 2 c. 26 L. 335/1995.** Obbligo di iscrizione dal 01/01/1996; c. 30 riparto 1/3-2/3. **norma certa** [N11]
- **Aliquota 2026, tipo 11** «Collaborazioni coordinate e continuative presso PP.AA.»: 33,00 + 0,50 + 0,22 + 1,31 = **35,03%**. Iscritti con altra copertura o pensionati: 24%. **norma certa** [I1]; riepilogo concorde [T1].
- **DIS-COLL.** Art. 15 D.Lgs. 22/2015 c. 15-bis e c. 15-quinquies: dal 01/01/2022 aliquota pari a quella NASpI; circolare INPS: 1,31%. Spettanza esclude pensionati e titolari di partita IVA (c. 1). **norma certa** [N12, I1]
- **Riparto e versamento.** 2/3 committente, 1/3 collaboratore; versamento del committente **entro il 16 del mese successivo al pagamento**, con F24 EP per le PA (circolare par. 4.1). **norma certa** [I1]
- **Massimale** 122.295,00 euro; **minimale** per accredito 18.808,00 euro; 6.588,44 sul 35,03%. **norma certa** [I1]
- **INAIL.** Art. 5 D.Lgs. 38/2000, testo dal 16/03/2000: obbligo se il parasubordinato svolge attività protette o usa non occasionalmente veicoli a motore personalmente condotti; **committente** tenuto agli adempimenti; premio 1/3 lavoratore, 2/3 committente; base compensi effettivamente percepiti. **norma certa** [N13]
- **Altri tipi.** Partecipanti a collegi e commissioni: tipo 03, 33,72% (circolare). Componenti OIV e revisori: da trattare nel ticket sui titoli fuori da questa lista. **norma certa** il codice.

#### 6. UniEmens collaboratori

- **Elemento.** `<ListaCollaboratori>` → `<Collaboratore>`, non ListaPosPA. Identificato in modo univoco da `<CFCollaboratore>`, `<TipoRapporto>`, `<Aliquota>`. Cambio aliquota nel mese: due elementi. Con `<CodiceComune>` (Belfiore). **norma certa** [I3, v. 4.33]
- **Identità dell'ente.** La lista ha `<CAP>` e `<ISTAT>`, con `NS0010` per committenti non sostituti o senza ISTAT, sotto `<Azienda>` identificata da `<AnnoMeseDenuncia>` e `<CFAzienda>`. `<Matricola>` è elemento di `<PosContributiva>`. **norma certa** [I3]. Che l'ente pubblico non debba esporre alcuna matricola per i soli collaboratori: **prassi-interpretazione**, da confermare su un flusso reale.
- **Termine.** Ultimo giorno del mese successivo a quello di competenza. **Per i parasubordinati il mese di competenza è quello di erogazione del compenso.** **norma certa** [I3]
- **Cassa allargata.** Compensi pagati **entro il 12 gennaio**: si considerano percepiti nell'anno precedente, con applicazione delle aliquote di quell'anno; modalità rinviate alla circolare INPS 10/2002 (par. 5 circolare). **norma certa** [I1]. Circolare 10/2002 non letta: esposizione nel mese **da verificare**.

### C. LSU/LPU

#### 7. Chi paga, che cosa, natura

**Fonti e vigenza**

- **D.Lgs. 468/1997 è abrogato dal D.Lgs. 150/2015.** Artt. 7 e 8 si applicano solo ai progetti iniziati prima della convenzione quadro (art. 26 c. 12 D.Lgs. 150/2015). **norma certa** [N14, N15]
- Art. 8 letto nel testo a 01/01/2015, in vigore dal 27/04/2001. **norma certa**
- D.Lgs. 81/2000: platea storica; testo dal 22/04/2000 per gli articoli letti (1, 2, 4, 8). **norma certa** [N16]
- D.Lgs. 280/1997: solo intestazione letta (borse di lavoro). **da verificare**
- Regime corrente per nuovi progetti: art. 26 D.Lgs. 150/2015, testo dal 01/01/2016. **norma certa** [N15]

**Chi paga**

| Voce | Chi | Riferimento |
|---|---|---|
| Assegno LSU | **INPS**, previa certificazione presenze dell'ente | Art. 8 c. 3 D.Lgs. 468/1997; art. 26 c. 5 D.Lgs. 150/2015 |
| Oneri dell'assegno ex art. 26 | Regioni e province autonome stipulanti | Art. 26 c. 5 |
| Platea storica | Fondo sociale occupazione e formazione | Ministero del lavoro [M3, D] |
| Autofinanziati | **Ente utilizzatore** | Ministero del lavoro [M3, D] |
| Importo integrativo per ore oltre 20 | **Ente utilizzatore**, per giornate di presenza | Art. 8 c. 2, 3 e 6 |
| INAIL e RC verso terzi | **Ente utilizzatore** | Art. 8 c. 9; art. 26 c. 8 |

Tutte **norma certa** salvo diversa indicazione. Ai sensi dell'art. 26 c. 5 e dell'art. 8 l'ente non è pagatore dell'assegno ordinario. Le tre categorie (platea storica, autofinanziati, percettori) sono riportate dal Ministero; la pagina non è datata.

**Non è rapporto di lavoro:** art. 8 c. 1 D.Lgs. 468/1997; art. 4 c. 1 D.Lgs. 81/2000; art. 26 c. 3 D.Lgs. 150/2015. **norma certa**

**Importo.** Le misure in lire dei testi citati (800.000 e 850.000) sono superate da rivalutazioni. Importo 2026: **da verificare**; riferimenti solo da stampa [T2], assegno sociale ex art. 26 c. 5.

**Fiscale**

- Art. 50 c. 1 lett. l). **norma certa** [N5]
- Art. 13 c. 1 per la detrazione. **norma certa**
- Regime agevolato: art. 52 c. 1 lett. d-bis): età pensionabile e reddito complessivo fino a 18 milioni di lire: imponibile sopra 6 milioni. Le istruzioni CU e il TU convertono in 9.296,22 e 3.098,74 euro. Due fonti. **norma certa** [N5, A1, N20]
- Art. 24 c. 1-bis D.P.R. 600: su quella parte ritenuta **a titolo d'imposta**, primo scaglione più addizionali. **norma certa** [N6]
- Mancata spettanza: annotazione AG in CU. **norma certa** [A1]
- **Sostituto.** L'ente è sostituto sull'importo che paga (art. 23-24 D.P.R. 600). **prassi-interpretazione**. INPS certifica il proprio assegno: non riscontrato. **da verificare**
- Cumulo su due sostituti: CU punti 565-570 per compensi LSU erogati da altri sostituti. **norma certa** [A1]

**Contributi sull'integrazione.** L'importo è calcolato **detraendo** le ritenute previdenziali e assistenziali dei dipendenti analoghi (art. 8 c. 2). Non è un imponibile contributivo evidente. Il periodo LSU è riconosciuto d'ufficio ai soli fini dei requisiti (art. 26 c. 11, che richiama art. 7 c. 9 L. 223/1991). La circolare RGS prevede contributi e IRAP in P055 e P061 se a carico dell'ente. Obbligo contributivo sull'integrazione, gestione e flusso: **da verificare**. Provato: Normattiva, circolare RGS, ricerca.

**IRAP.** Art. 10-bis copre i redditi assimilati, quindi l'importo pagato dall'ente; la tabella SICO indica IRAP separata. **prassi-interpretazione**

**Attiva o residuale, 2026**

- La circolare RGS sul 2025 mantiene colonna, voce e causale «Personale stabilizzato da LSU/LPU/ASU». **norma certa** [R1]
- Ministero del lavoro: pagamenti annualità 2026 ai comuni fino a 5.000 abitanti per stabilizzazioni [T3, estratto]. **prassi-interpretazione**
- L. 160/2019 art. 1 c. 495: assunzioni a tempo indeterminato anche in deroga, fino al 31/12/2024. **norma certa** [N17]. Proroghe successive: **da verificare**.
- L. 234/2021: **nessuna occorrenza** di «socialmente utili» nei commi 1-1000 letti. Il riferimento «c. 490-?» della domanda non è stato riscontrato; commi 1001-1013 non letti. **norma certa** come ricerca testuale.
- Esclusi dal Conto Annuale i soggetti in pubblica utilità da provvedimenti dell'Autorità Giudiziaria, inclusa la messa alla prova. **norma certa** [R1]
- Conclusione: figura residuale ma ancora rilevante, con forte variabilità regionale. **prassi-interpretazione**

### D. Segretario

#### 8. Ordinamento, convenzione, scavalco, CCNL

**Ordinamento**

- Artt. 97-99 TUEL: titolare, funzioni, albo, nomina. Art. 97 c. 1 cita ancora l'Agenzia; RGS parla di rapporto di lavoro con il Ministero dell'interno e rapporto di servizio con l'ente. **norma certa** [N1, R1]. Norma di soppressione dell'Agenzia: non letta. **da verificare**
- Convenzione: art. 98 c. 3 TUEL; D.P.R. 465/1997 art. 10, testo dal 01/06/2005: deliberazioni consiliari; la convenzione individua il sindaco competente, modalità, **ripartizione degli oneri**, durata, recesso; c. 3 retribuzione aggiuntiva e viaggio. **norma certa** [N18]
- Art. 30 TUEL: convenzioni generali. Classe dalla somma degli abitanti (art. 16-ter c. 11 d.l. 162/2019). **norma certa** [N19]

**Scavalco.** Art. 62 c. 1 CCNL 16/07/2024: attribuito ai titolari di sede con provvedimento motivato del Ministero dell'Interno, sentite le amministrazioni, solo in via residuale rispetto ai segretari in disponibilità, per massimo **120 giorni** per le reggenze e **un anno** per le supplenze. **norma certa** [C2]. Differenze:

| | Convenzione | Scavalco |
|---|---|---|
| Fonte | Deliberazioni consiliari, atto stabile | Provvedimento ministeriale, temporaneo |
| Titolarità | Unica sede convenzionata | Titolare altrove |
| Compenso | Retribuzione aggiuntiva **25%** della base (art. 63 c. 1) | **15%** fino a 60 giorni, **25%** oltre; elevabile al 25% anche sotto; restano più alti valori integrativi (art. 62 c. 2-3) |
| Base | Art. 56 c. 1 lett. a-d: stipendio, RIA, posizione, maturato | Stessa |
| Viaggio | Art. 63 c. 2 | Art. 62 c. 4, se non è possibile operare da remoto, a carico dell'ente utilizzatore |
| Ripartizione | Art. 63 c. 3, come da convenzione | Ente dell'incarico |

**norma certa** il testo; le percentuali 15% e 25% sono anche in un commento [E4, estratto]. Art. 3 CCNI 22/12/2003 (8%, 30 giorni, testo letto) è **disapplicato** (art. 62 c. 5). ARAN conferma il calcolo sulla posizione graduata ex art. 60 [E3, estratto]; art. 60 è ora sostituito da art. 38 CCNL 23/02/2026.

**Catena contrattuale: testo vigente**

| Istituto | CCNL 16/05/2001 | Testo vigente |
|---|---|---|
| Struttura | Art. 37 | Art. 56 CCNL 16/07/2024, che sostituisce art. 105 CCNL 17/12/2020 |
| Posizione | Art. 41 | **Art. 38 CCNL 23/02/2026**, che sostituisce art. 60 CCNL 16/07/2024 |
| Maggiorazione art. 41 c. 4 | Art. 41 | Superata secondo RGS, che elimina la voce U06Z dal 01/01/2025. Art. 38 c. 7 conferma la disapplicazione di art. 107 c. 3 CCNL 2020, contenuto non letto |
| Risultato | Art. 42 | **Art. 39 CCNL 23/02/2026**, che sostituisce art. 61 |
| Risorse ulteriori | | Art. 40 CCNL 23/02/2026 |
| Disponibilità | Art. 43 | Art. 43 c. 2 ancora richiamato da art. 38 c. 6 |
| Direttore generale | Art. 44 | Art. 44 ancora citato da RGS |
| Convenzione e viaggio | **Art. 45** | **Art. 63 CCNL 16/07/2024** (c. 4 sostituisce art. 45) |
| Scavalco | CCNI 2003 | Art. 62 CCNL 16/07/2024 |
| Interim | | Art. 64 CCNL 16/07/2024 |

**norma certa** le clausole di sostituzione lette: art. 38 c. 9, art. 39 c. 3, art. 56 c. 4, art. 62 c. 5, art. 63 c. 4 [C1, C2]. Il raccordo con gli artt. 37, 41 e 42 del 2001 è **prassi-interpretazione**, per titolo e richiami [C3, R1]. CCNL 17/12/2020 non letto direttamente. Rinnovo Area 2025-2027: non cercato. **da verificare**

**Posizione, art. 38 CCNL 23/02/2026.** Valori annui lordi per 13 mensilità:

| Classe | Minimo | Massimo |
|---|---|---|
| A metropolitani | 46.707,00 | 68.139,96 |
| A oltre 250.000, capoluoghi, province | 38.593,00 | 56.668,99 |
| A fino a 250.000 | 25.507,00 | 37.901,97 |
| B oltre 10.000 fino a 65.000 | 18.236,00 | 27.532,22 |
| B da 3.000 a 10.000 | 9.374,00 | 14.796,80 |
| C fino a 3.000 | 8.829,00 | 11.617,87 |

**da verificare** riga per riga: PDF con colonne disallineate, stessa fonte in due copie.

Altri elementi certi del testo: graduazione c. 2; elevazione del tetto fino al 15% o 20% (c. 3 e 3-bis); galleggiamento c. 5 nel rispetto dell'art. 23 c. 2; incrementi 2024 ex art. 36, tabella non estratta.

**Risultato, art. 39 CCNL 23/02/2026**

- Risorse a **carico dei bilanci**, nel rispetto dell'art. 23 c. 2, **fino al 10%** del monte salari erogato al segretario nell'anno. **norma certa**; seconda fonte **da verificare**.
- **15%** per enti con dirigenza, incarico su posizione apicale in enti senza dirigenza, segretario di unione. **20%** per enti art. 38 c. 3 e 3-bis, calamità o commissariamento. **norma certa**; seconda fonte **da verificare**.
- Art. 40 c. 1: + 0,80% monte salari 2021 dal 01/01/2024, destinabile anche a welfare. Art. 40 c. 2: fino a + 0,22% oltre il limite art. 23 c. 2. **norma certa**; seconda fonte RGS. [R1]

#### 9. Datore, pagatore, contributi, CU e 770

**Convenzione**

- Nessuna norma letta fissa chi paga: il D.P.R. 465 art. 10 rimette alla convenzione. **norma certa**
- Schema pubblicato da una Prefettura: il comune capo convenzione **eroga le intere competenze e recupera con cadenza annuale** le quote degli altri [M4]. **prassi-interpretazione**
- Conto Annuale: capofila in Tab. 1, 7, 8, 9, 3 out; enti convenzionati Tab. 3 in; retribuzione aggiuntiva I223 **solo se direttamente corrisposta**. Ciascuno rileva «contributi ed IRAP e eventuali rimborsi». Quindi **la circolare ammette pagamenti diretti** anche da enti non capofila. **norma certa** [R1]
- Se paga il capofila: sostituto, CU, 770 e flusso previdenziale in capo a chi corrisponde (art. 23 D.P.R. 600 c. 1; art. 24). **prassi-interpretazione**. Circolari INPS specifiche non trovate. **da verificare**
- Rimborso tra enti: P090 ricevuti e P071 pagati, con oneri riflessi e IRAP (circolare), elenco enti obbligatorio nelle note. **norma certa** [R1]. U.1.09.01.01.001 ed E.3.05.02.01.001. **norma certa** [R2]
- Assenze: secondo il quadro sinottico, ognuno per le giornate presso di sé; giustificazione predefinita per assenze rilevate altrove. **norma certa** [R1]
- Previdenza del segretario titolare: gestione pubblica e ListaPosPA come dipendente. **prassi-interpretazione**, nessun testo dedicato letto. CPDEL e TFS/TFR vanno confermati su ListaPosPA.

**Scavalco**

- Ente dello scavalco: **eroga direttamente l'indennità**, Tab. 13 S740, **nessun dato di organico**; non in Tab. 3 né da titolare né da utilizzatore. Incongruenze da giustificare. **norma certa** [R1]
- Ente titolare: tutte le tabelle.
- CPDEL e quota TFR ripartite tra ente e segretario, IRAP all'ente: da determine di enti e commento a Corte conti Veneto 400/2018 [E4, estratti]. **prassi-interpretazione**
- Corte Liguria considera l'indennità componente retributiva [E5, estratto]. **prassi-interpretazione**
- Sostituto, CU, conguaglio con il titolare, 770, ListaPosPA e posizione per TFS/TFR: **da verificare**. Provato: istruzioni CU, circolare RGS, documento UniEmens, ricerche. Non è stato trovato nessun testo primario.

**Disponibilità.** Reggenza o supplenza: grava sull'ente anche se anticipato dal Ministero, rimborso P074 e P099; comando P071 e P090. **norma certa** [R1]

**Unione.** Art. 32 c. 5-ter TUEL, come riportato da RGS: segretario di un comune dell'unione senza ulteriori indennità; se erogate, Tab. 13 «Altre spese» con giustificazione. **norma certa** [R1]

#### 10. Risultato, fondo, Conto Annuale

- **Bilancio, non fondo.** Art. 39 c. 2; RGS: «la tabella 15 del Segretario … è rappresentata da trattamenti accessori finanziati con risorse di bilancio». **norma certa** [C1, R1]
- **Dentro art. 23 c. 2:** art. 38 c. 8 e art. 39 c. 2. **norma certa**. Eccezioni individuate:
  - F33T: art. 40 c. 1, 0,80%, con Dichiarazione congiunta n. 2 su art. 11 c. 1 d.l. 135/2018.
  - F24T: art. 61 c. 3 CCNL 2019-21, 0,22% monte salari 2018.
  - F33U: art. 40 c. 2, 0,22%.
  - F20M: quota posizione art. 43 c. 2 CCNL 2001.
  - LEG545: incremento posizione art. 36 c. 1.
  - F24K: PNRR.

  **norma certa** RGS. Le voci F rientrano nella LEG398 SICI.
- **Sezione sinistra Tab. 15:** budget annuo, a prescindere da cessazione, assenza o scavalco per frazione d'anno. **Destra:** erogato effettivo. **norma certa**
- Utilizzi: U448 posizione al netto del galleggiamento; U07Z galleggiamento; U449 risultato. **norma certa**
- **Fuori da Tab. 15:** diritti di segreteria; **retribuzione aggiuntiva per sedi convenzionate** (pareri ARAN SEG032 e AFL4, citati); indennità Direttore generale. **norma certa** RGS.
- **Interim:** art. 64: a carico del **fondo dirigenti**, voce U08B. **norma certa**
- Direttore generale: S710. Scavalco e rogito: S740. Convenzione: I223. **norma certa**
- Macrocategoria «Segretario comunale e provinciale» con Tab. 15 propria. Non esiste un «fondo segretario» in senso proprio. **norma certa**

### E. Trasversali

#### 11. Conto Annuale, rilevazione 2025

Circolare RGS n. 12 del 26/06/2026, allegato [R1]. Risponde alla domanda aperta 9 del documento #10. Tutto **norma certa** salvo diversa indicazione. Tab. 14 per cassa.

| Soggetto | Organico | Spesa |
|---|---|---|
| **Amministratori** | Nessuna tabella | Non previsti. Caso esplicito: dipendente del comune eletto sindaco nello stesso ente: resta in organico, in Tab. 3 «aspettativa» se al 31/12; **«l'indennità di carica non deve essere rilevata, ma vanno registrati i relativi contributi e l'IRAP»** |
| **Co.co.co.** | **Non in Tab. 2 né 2A.** Scheda informativa 1: numero contratti di collaborazione professionale, art. 7 c. 6 | L111, compresi contributi e IRAP a carico. Attivi nell'anno, proroga unificata |
| **Occasionali e autonomi** | Scheda 1 | L111, L112 studio e consulenza, L115 servizi obbligatori |
| **LSU/LPU/ASU** | Tab. 2 in unità uomo-anno, anche per ore | P065 solo la parte a carico, lordo dipendente; contributi P055, IRAP P061. Se a carico di altri: solo Tab. 2, incongruenza 11 giustificata. Se l'ente paga e riceve rimborso: Tab. 2, Tab. 14 e P099 |
| **Segretario titolare** | Tab. 1 con macrocategoria | Tab. 12, 13, 14, 15 |
| **Convenzione, capofila** | Tab. 1, 7, 8, 9, Tab. 3 out | Tab. 12, 13, I223, 14, P090 |
| **Convenzione, altri** | Tab. 3 in | Solo se pagato direttamente; P071 |
| **Scavalco** | Nessuna, salvo titolare | S740 presso l'utilizzatore |

Altri fatti:

- **Novità 2025:** «Con l'eliminazione delle collaborazioni coordinate e continuative dalla tabella 2A, questa tabella fa ora riferimento al solo personale a tempo determinato». Sostituisce quanto ipotizzato nel documento #10.
- L111 **esclude** «le attività di amministratore, sindaco o revisore, componente dell'OIV in quanto organi dell'ente», collegi e commissioni. L'esclusione si riferisce alle cariche di organo, e non cita espressamente gli eletti. **prassi-interpretazione**
- Riconciliazione SICO/SIOPE: U.1.03.02.12.002 → P065; .001 → P062; .003 → L111; U.1.09.01.01.001 → P071 e altri rimborsi; E.3.05.02.01.001 → P090 e altri (lettura da tabella). U.1.03.02.01 (organi) non compare. Conferma che gli amministratori sono fuori. **norma certa** come assenza di occorrenza; associazione voci **da verificare** per disallineamento.
- SI1A: domanda «L'ente è titolare (Capofila) della segreteria convenzionata al 31.12?»: SI → Tab. 3 Personale dell'amministrazione/Convenzioni; NO → Personale esterno/Convenzioni. **Controllo bloccante.**
- Tab. 14: voce «somme a personale esterno» non presente con questo nome nella tabella letta. Vicini: P071, P074, L110 per personale cessato.
- Calcolo uomo-anno e FTE: nella circolare; non trascritto qui.

#### 12. Limiti di spesa

**Art. 33 c. 2 d.l. 34/2019, testo dal 18/01/2023** [N21]: «spesa complessiva per tutto il personale dipendente, al lordo degli oneri riflessi». **norma certa**

**D.M. 17/03/2020 art. 2:** testo non letto. Da estratti: «impegni di competenza» [E6]. Secondo la Lombardia 96/2022, co.co.co., somministrazione, art. 110 rientrano. Già riportato nel documento #10. **prassi-interpretazione**. Testo: **da verificare**.

**Numeratore RGS, Scheda A33** [R1]: dalla BDAP «U.1.01.00.00.000, U1.03.02.12.001, U1.03.02.12.002, U1.03.02.12.003, U1.03.02.12.999», meno arretrati U.1.01.01.01.001 e .005 (art. 3 c. 4-ter d.l. 36/2022), meno spese finanziate da altri ex art. 57 c. 3-septies d.l. 104/2020, altre esclusioni motivate. **norma certa**

| Titolo | Art. 33 secondo A33 | Note |
|---|---|---|
| Co.co.co. | **Sì** (.003) | Conforme a estratti Corte |
| LSU | **Sì** (.002), quota a carico | Trattazione Corte: non trovata |
| Amministratori | **No** (1.03.02.01 non estratto) | Testo espresso non trovato: **da verificare** |
| Segretario | Sì (1.01) | Dedotto dal macroaggregato. **prassi-interpretazione** |
| Convenzione | **Discrepanza** | Lombardia 125/2020 [E7, tramite commento]: il capofila imputa tutto e riceve le entrate; gli enti convenzionati considerano la propria quota come spesa di personale, per sostanza. RGS **non estrae** U.1.09 |

La discrepanza va trattata: l'estrazione RGS non vede i rimborsi 1.09 pagati. Il blog indica una voce di entrata (Titolo 2, Tipologia 101) diversa dal piano dei conti (E.3.05.02.01.001). **da verificare** su deliberazione e circolare 13/05/2020.

**Art. 9 c. 28 d.l. 78/2010, testo dal 08/08/2026** [N22], **norma certa**:

- Limite 50% della spesa 2009 per tempo determinato, convenzioni, **co.co.co.**, formazione lavoro, somministrazione, accessorio.
- Principio generale per gli enti locali; superabile per polizia locale, istruzione, sociale. Non si applica «agli enti locali in regola con l'obbligo di riduzione» dei c. 557 e 562, ma resta il tetto della spesa 2009.
- Non si applica **anche per LSU, LPU e cantieri** se il costo è coperto da finanziamenti aggiuntivi o UE; con cofinanziamento, esclusa solo la quota altrui.
- **Effetto del d.l. 144/2026** su «in regola con» i c. 557 e 562: **da verificare**. La norma non è stata coordinata nel testo letto.

**L. 296/2006 e d.l. 144/2026.**

- Art. 2 c. 1 d.l. 7 agosto 2026 n. 144, convertito con L. 5 ottobre 2026 n. 174 (GU 06/10/2026), in vigore dall'08/08/2026: «Alle amministrazioni soggette ai vincoli di cui all'articolo 33» non si applicano **i c. da 557 a 557-quater e 562**. **norma certa** [N23]. Chiude la domanda aperta 3 del documento #10.
- C. 557-bis: co.co.co., somministrazione, art. 110 e utilizzati in organismi partecipati. **norma certa** [N24]. Rilevante ora solo per gli enti non soggetti all'art. 33. **prassi-interpretazione** Unioni: secondo il documento #10 restano fuori dalla disapplicazione; **da verificare** sul caso.
- Lombardia 154/2022 (costo del segretario senza deroga al c. 557-quater, [estratto]) riguarda una norma ora disapplicata per questi enti: valore storico.
- **Art. 23 c. 2 D.Lgs. 75/2017, testo dal 24/10/2026** [N25]: resta. **norma certa**. Note d'aggiornamento non lette: **da verificare**.

#### 13. Successione dal 01/01/2027

**Atti**

- D.Lgs. 19/06/2026 n. 117: testo unico imposte sui redditi, allegato; in vigore 04/07/2026; **si applica dal 01/01/2027** (TU art. 377); abroga dalla stessa data TUIR artt. da 1 a 191 (TU art. 376 c. 1 lett. e). **norma certa** [N20]
- D.Lgs. 24/03/2025 n. 33: testo unico versamenti e riscossione, allegato; **si applica dal 01/01/2027** (TU art. 243, data modificata). **norma certa** [N26]
- Vigenza dei vecchi articoli: fino al 31/12/2026 (Normattiva indica «in vigore … al 31-12-2026» per art. 23 e 51, già provati nel documento #17). **norma certa**. Per gli altri articoli qui citati è deduzione dall'abrogazione. **prassi-interpretazione**
- Ogni articolo dei due TU riporta in testa la fonte d'origine. **norma certa**

| Vecchio | Nuovo | Note |
|---|---|---|
| TUIR art. 49 | TU 117 art. 51 | Lavoro dipendente |
| TUIR art. 50 | **TU 117 art. 52** | Assimilati; lettere h) e p) riprendono leggi speciali, come da intestazione |
| Art. 50 c. 1 **lett. c-bis)** | Art. 52 c. 1 **lett. d)** | Testo equivalente, rinvii a 51 e 55 |
| Art. 50 c. 1 **lett. f)** | Art. 52 c. 1 **lett. g)** | «corti di giustizia tributarie» |
| Art. 50 c. 1 **lett. g)** | Art. 52 c. 1 **lett. i)** | **L. 816/1985 sostituita da D.Lgs. 267/2000** |
| Art. 50 c. 1 **lett. l)** | Art. 52 c. 1 **lett. o)** | Identica |
| TUIR art. 51 | TU 117 art. 53 | Cassa allargata al c. 1 |
| TUIR art. 52 | TU 117 art. 54 | |
| Art. 52 c. 1 lett. b) | Art. 54 c. 1 lett. b) | Rimborsi spese |
| Art. 52 c. 1 lett. d-bis) | Art. 54 c. 1 lett. e) | Importi in euro: 9.296,22 e 3.098,74 |
| TUIR art. 13 c. 1 | TU art. 13 c. 1 | Elenco ora a), b), c), d), e), m), o) |
| TUIR art. 13 c. 5 | TU art. 13 c. 5 | Elenco ora f), g), i), l), n) |
| TUIR art. 17 c. 1 lett. a) | TU art. 19 c. 1 lett. a) | Rinvio a 52 lett. a), e), i) |
| TUIR art. 19 c. 2-bis | **da verificare** | Articolo TU non individuato |
| D.P.R. 600 art. 23 | D.Lgs. 33/2025 art. 33 | Solo alcuni commi, indicati in testa |
| D.P.R. 600 art. 24 | D.Lgs. 33/2025 art. 34 | c. 1-bis → c. 2; c. 1-ter → c. 3 |
| D.P.R. 600 art. 25 | D.Lgs. 33/2025 art. 38 | |

Tutte **norma certa**, salvo l'equivalenza dei testi.

**Invarianza o cambiamento.** Per questi redditi le letture fatte mostrano rifusione: stessi criteri, importi in euro, nuovi rinvii. La L. 111/2023 è delega al riordino. Una verifica parola per parola non è stata fatta. Cambi visibili:

- il richiamo «L. 816/1985» diventa TUEL;
- la numerazione di lettere e articoli cambia, quindi **la tabella tipologie CU e tutte le causali con citazione dovranno cambiare**, ma CU 2027 non è stata cercata;
- restano da coordinare norme esterne che citano la vecchia numerazione: art. 10-bis D.Lgs. 446/1997 (art. 47 e 49, già vecchie), art. 2 c. 26 L. 335/1995, art. 5 D.Lgs. 38/2000. Clausola generale di rinvio: non trovata nelle pagine lette di TU art. 376. **da verificare**

**prassi-interpretazione**

**Per il corpus:** riferimenti alla data di competenza, come da documento #17: `urn:nir:stato:decreto.legislativo:2026-06-19;117:1~art52-com1-letd`.

#### 14. CU, 770, F24 EP

Istruzioni CU 2026, agg. 05/02/2026, reddito 2025 [A1]; istruzioni 770/2026 [A2]; tabella codici F24 EP [A4].

**CU, dati fiscali.** **norma certa**

| Titolo | Punto | Detrazione | Tipologia (punti 751-756) |
|---|---|---|---|
| Amministratori, gettoni, cariche elettive | **Punto 4** | Art. 13 c. 5 | 11, lett. g); gettoni pubbliche funzioni lett. f): codice non riletto |
| Co.co.co. | Punti 1 e 2 | Art. 13 c. 1 | 6 |
| Collegi e commissioni | Punti 1 e 2 | Art. 13 c. 1 | 5 |
| LSU | Punti 1 e 2; regime agevolato 496-499; altri sostituti 565-570 | Art. 13 c. 1 | 18 |

La nota del repo su «punto 4 CU, art. 13 c. 5 TUIR» è **confermata**, per gli amministratori, sul testo delle istruzioni. Punto 498: ritenute LSU agevolate, codici 1001 e 100E. Punto 513: tassazione separata anni precedenti: 1002, 102E e altri. La fine mandato (tassazione separata): punti da individuare. **da verificare**

**CU, dati previdenziali.** **norma certa**

- Quadro gestione pubblica: art. 86 TUEL, compilazione se denunciato o versato; rinvio alla nota INPDAP 6/2008.
- Sezione 3 Gestione separata: tipo rapporto 04, 11, 18, 19 e altri; certificazione compensi corrisposti nell'anno.
- Punto 9: CF dell'amministrazione di appartenenza. Punto 4: imponibile.

**770.** Le istruzioni citano le addizionali regionali sui compensi LSU in regime agevolato tra le trattenute da esporre. **norma certa** [A2]. Il quadro ST espone versamenti per codice tributo, non per titolo: la distinzione per titolo sta nelle CU. **prassi-interpretazione**. Non sono state lette tutte le sezioni.

**F24 EP.** **norma certa** [A4], tabella pubblicata dall'AdE, data di versione del file non verificata.

| Sezione | Codice | Denominazione |
|---|---|---|
| ERARIO (F) | 100E | Ritenute su lavoro dipendente ed **assimilati** |
| ERARIO (F) | 102E | Ritenute su emolumenti arretrati (citato con 1002 in CU) |
| ERARIO (F) | 104E | Ritenute su lavoro autonomo. Tabella disallineata su 104E, 105E e 106E: **da verificare** |
| REGIONI | 381E | Addizionale regionale, codice regione |
| ENTI LOCALI (S) | 384E | Addizionale comunale, saldo, con codice catastale |
| ENTI LOCALI (S) | 385E | Addizionale comunale, acconto |
| INPS (I) | **C10**, **CXX** | «Gestione Committenti»: sede, CAP e comune, mese di pagamento |
| INAIL (N) | Sezione con codice sede, ditta e causale | |

Sanzioni e varianti per ravvedimento nella stessa tabella. Quale aliquota si associa a C10 e a CXX: **da verificare** (la tabella riporta solo la gestione). La vecchia tabella 2020 riporta 100E e 381E; risoluzione 367/E del 2007 [estratto].

#### 15. Contabilità

**Art. 183 c. 2 lett. a) TUEL, testo dal 01/01/2019:** impegno automatico «per il trattamento economico tabellare già attribuito al **personale dipendente** e per i relativi oneri riflessi». **norma certa** [N1]

**Allegato 4/2, testo dal 2026, punto 5.2** [R3] **norma certa**:

- Lett. a): trattamenti fissi e continuativi con dinamica salariale da legge o CCNL, «anche se trattasi di personale comandato, avvalso o comunque utilizzato da altra amministrazione pubblica, ancorché direttamente pagato da quest'ultima»: impegno automatico a inizio esercizio. Accessorio e fondo: regole proprie.
- «Gettoni di presenza dei componenti del Consiglio» compare una volta: imputazione all'esercizio in cui la prestazione è resa.
- Ricerca di «collaborazion», «amministratori», «LSU», «indennità di funzione»: nessun esito. La ricerca è fatta su testo estratto da .doc, quindi l'assenza va confermata aprendo il documento. **da verificare**

**Conseguenza.** Amministratori (indennità fissa) e co.co.co.: **fuori dall'automatismo**, impegno ordinario su obbligazione giuridica. **prassi-interpretazione**. Punto del principio per fattispecie: **da verificare**. Per il segretario: l'automatismo vale, compreso il «comunque utilizzato»; per l'ente convenzionato il testo fa pensare all'impegno anche se paga altri. **prassi-interpretazione**

**Piano dei conti**, All. 6, dal 2026 e dal 2027 [R2]. Voci organi, U.1.03.02.12 e rimborsi riscontrate in entrambi i file; contributi e IRAP solo nel file dal 2026. **norma certa**

| Fattispecie | V livello |
|---|---|
| Indennità organi istituzionali | U.1.03.02.01.001 |
| Rimborsi organi istituzionali | U.1.03.02.01.002 |
| Collaborazioni coordinate e a progetto | U.1.03.02.12.003 |
| Quota LSU in carico all'ente | U.1.03.02.12.002 |
| Altre forme di lavoro flessibile n.a.c. | U.1.03.02.12.999 |
| Contributi obbligatori per il personale | U.1.01.02.01.001 |
| IRAP | U.1.02.01.01.001 |
| Rimborsi per spese di personale in uscita | U.1.09.01.01.001 |
| Rimborsi ricevuti per spese di personale | E.3.05.02.01.001 |

- Segretario: **nessuna voce dedicata** nel piano; ricerca sulla parola «segretari» senza esito. Macroaggregato 1.01 per il personale. **prassi-interpretazione**
- Contributi su collaboratori e amministratori, INAIL: voce non riscontrata. **da verificare**
- Entrata o trasferimento per il fondo indennità: non riscontrata. **da verificare**

## Domande aperte

1. **ListaPosPA per l'amministratore dipendente in aspettativa:** codice e ente dichiarante. Serve nota INPDAP 6/2008 o allegato tecnico. Ente del mandato e datore coincidenti: come si espone?
2. **Scavalco:** sostituto, CU, 770, ListaPosPA, TFS/TFR e conguaglio. Nessun testo primario trovato. Da chiedere a Luca l'esperienza su flussi reali.
3. **Convenzione:** convenzioni con pagamenti diretti da più enti: in pratica esistono? Il capofila conguaglia anche per il rimborso? Tempi di recupero.
4. **Art. 33:** come tratta gli enti convenzionati l'estrazione RGS che non prende 1.09? Il D.M. 17/03/2020 e la circolare 13/05/2020 vanno letti sul testo.
5. **Art. 9 c. 28:** effetto della disapplicazione dei c. 557 e 562 sulla clausola «in regola con».
6. **LSU:** obbligo contributivo sull'importo integrativo, gestione, flusso. Importo assegno 2026. Stabilizzazione dopo 31/12/2024.
7. **Amministratori:** esiste un testo INPS che escluda l'indennità da Gestione separata? Soggetti con doppio regime (forfettaria e aspettativa): casistica.
8. **Quote art. 86 c. 2:** modalità attuali per artigiani e commercianti e per casse; il bollettino del 2001 è ancora in uso? Tabelle INPS annue.
9. **INAIL amministratori:** applicazione dopo Cass. 22036/2025; posizione INAIL dell'ente.
10. **Coordinamento 2027:** clausola generale di rinvio ai nuovi TU per norme esterne, art. TU per l'ex art. 19 c. 2-bis, confronto parola per parola, CU 2027.
11. **Regioni a statuto speciale:** L. 234/2021 c. 583 riguarda le ordinarie; indennità speciali e Tab. Friuli, Trentino, Valle d'Aosta non esaminate.
12. **Titoli fuori dalla lista:** revisori, OIV, commissioni, art. 110, art. 90, occasionali. Trattati solo dove la fonte li incrocia.

## Fonti

(D) letta direttamente; (E) estratto o riproduzione, indicata.

**Norme, Normattiva**, tutte (D) al 06/11/2026 salvo TU, con base `https://www.normattiva.it/uri-res/N2Ls?` e `!vig=2026-11-06`:

- [N1] TUEL artt. 30, 79-82, 84, 86, 97-99, 183: `urn:nir:stato:decreto.legislativo:2000-08-18;267~art82`
- [N2] L. 234/2021 art. 1: `urn:nir:stato:legge:2021-12-30;234~art1`
- [N3] D.M. 119/2000: `urn:nir:ministero.interno:decreto:2000-04-04;119~art2`
- [N5] TUIR artt. 13, 19, 50, 51, 52: `urn:nir:stato:decreto.del.presidente.della.repubblica:1986-12-22;917~art50`
- [N6] D.P.R. 600/1973 artt. 23-25: `urn:nir:stato:decreto.del.presidente.della.repubblica:1973-09-29;600~art24`
- [N7] L. 724/1994 art. 26: `urn:nir:stato:legge:1994-12-23;724~art26`
- [N8] D.Lgs. 446/1997 artt. 10-bis, 16: `urn:nir:stato:decreto.legislativo:1997-12-15;446~art10bis`
- [N9] D.Lgs. 165/2001 art. 7: `urn:nir:stato:decreto.legislativo:2001-03-30;165~art7`
- [N10] D.Lgs. 81/2015 art. 2: `urn:nir:stato:decreto.legislativo:2015-06-15;81~art2`
- [N11] L. 335/1995 art. 2: `urn:nir:stato:legge:1995-08-08;335~art2`
- [N12] D.Lgs. 22/2015 art. 15: `urn:nir:stato:decreto.legislativo:2015-03-04;22~art15`
- [N13] D.Lgs. 38/2000 art. 5: `urn:nir:stato:decreto.legislativo:2000-02-23;38~art5`
- [N14] D.Lgs. 468/1997 artt. 7, 8, con `!vig=2015-01-01`: `urn:nir:stato:decreto.legislativo:1997-12-01;468~art8`
- [N15] D.Lgs. 150/2015 art. 26: `urn:nir:stato:decreto.legislativo:2015-09-14;150~art26`
- [N16] D.Lgs. 81/2000: `urn:nir:stato:decreto.legislativo:2000-02-28;81~art4`; D.Lgs. 280/1997: `urn:nir:stato:decreto.legislativo:1997-08-07;280~art1`
- [N17] L. 160/2019 art. 1: `urn:nir:stato:legge:2019-12-27;160~art1`
- [N18] D.P.R. 465/1997 art. 10: `urn:nir:stato:decreto.del.presidente.della.repubblica:1997-12-04;465~art10`
- [N19] D.L. 162/2019 art. 16-ter: `urn:nir:stato:decreto.legge:2019-12-30;162~art16ter`
- [N20] D.Lgs. 117/2026, allegato, artt. 13, 19, 50-55, 375-377 (senza `!vig`): `urn:nir:stato:decreto.legislativo:2026-06-19;117:1~art52`
- [N21] D.L. 34/2019 art. 33: `urn:nir:stato:decreto.legge:2019-04-30;34~art33`
- [N22] D.L. 78/2010 art. 9: `urn:nir:stato:decreto.legge:2010-05-31;78~art9`
- [N23] D.L. 144/2026 art. 2: `urn:nir:stato:decreto.legge:2026-08-07;144~art2`
- [N24] L. 296/2006 art. 1: `urn:nir:stato:legge:2006-12-27;296~art1`
- [N25] D.Lgs. 75/2017 art. 23: `urn:nir:stato:decreto.legislativo:2017-05-25;75~art23`
- [N26] D.Lgs. 33/2025, allegato, artt. 33-47, 242-243 (senza `!vig`): `urn:nir:stato:decreto.legislativo:2025-03-24;33:1~art34`
- [N4] D.M. 25/05/2001 (E, riproduzione Inarcassa): https://www.inarcassa.it/sites/default/files/legacy/documents/1329D.Lgs.25-05-01.pdf

**INPS**

- [I1] Circolare 8/2026 (D): https://www.inps.it/content/dam/inps-site/it/scorporati/circolari-e-messaggi/2026/02/Circolare_15153/Allegati/16573_Circolare-numero-8-del-03-02-2026.pdf
- [I2] Circolare 205/2001 (D): https://servizi2.inps.it/servizi/Bussola/VisualizzaDoc.aspx?sVirtualURL=%2FCircolari%2FCircolare+numero+205+del+21-11-2001.htm
- [I3] Documento tecnico UniEmens individuale v. 4.33 (D): https://www.inps.it/content/dam/inps-site/pdf/prestazioni-e-servizi/uniemens-aziende-private/UniEMENSind.pdf
- [I4] Messaggio 3268/2019 (E, riproduzione): https://www.studiocerbone.com/?p=426350
- [I5] Circolare 133/2012 (E): https://servizi2.inps.it/servizi/Bussola/VisualizzaDoc.aspx?sVirtualURL=%2FCircolari%2FCircolare+numero+133+del+26-11-2012.htm

**Agenzia delle Entrate**

- [A1] Istruzioni CU 2026, agg. (D): https://www.agenziaentrate.gov.it/portale/documents/d/guest/cu_istr_2026_agg-1-
- [A2] Istruzioni 770/2026 (D, parti): https://www.agenziaentrate.gov.it/portale/documents/20143/9771798/770_istr_2026.pdf/6175653a-80b7-42a6-cd77-4e48609d0dfc?t=1772197125449
- [A3] Risoluzione 29/E/2010 (D): https://www.agenziaentrate.gov.it/portale/documents/20143/305373/Ris+29+del+15+04+10_ris.+n.+29+del+15+aprile+2010.pdf/6fa617db-b56b-01ad-9080-0a0ecb5c4061
- [A4] Tabella codici F24 EP (D): https://www.agenziaentrate.gov.it/portale/documents/20143/448330/codici%20tributo%20per%20compilazione%20modello_Tabella%20codici%20tributo%20F24EP%20.pdf/f4ee4875-1489-14fa-55e1-bf60f3282bbe

**RGS**

- [R1] Circolare 12/2026, allegato (D): https://www.rgs.mef.gov.it/_Documenti/VERSIONE-I/CIRCOLARI/2026/12/Allegato-alla-Circolare-del-26-giugno-2026-n-12.pdf
- [R2] Piano dei conti, All. 6 dal 2026 e dal 2027 (D): https://www.rgs.mef.gov.it/_Documenti/VERSIONE-I/e-GOVERNME1/ARCONET/DOCUMENTAZIONE/2025/DM-6-agosto-2025/All-6_Piano_dei_conti_integrato-dal-2026_rev.xls , https://www.rgs.mef.gov.it/_Documenti/VERSIONE-I/e-GOVERNME1/ARCONET/DOCUMENTAZIONE/2025/DM-6-agosto-2025/All-6_Piano_dei_conti_integrato-dal-2027_rev.xls
- [R3] Allegato 4/2 dal 2026 (D, estrazione testo da .doc): https://www.rgs.mef.gov.it/_Documenti/VERSIONE-I/e-GOVERNME1/ARCONET/principi_contabili/2026/All-4-2-Principio-applicato-contabilita-finanziaria-dal-2026.doc

**CCNL**

- [C1] CCNL Area FL 2022-2024, 23/02/2026 (D): https://www.aranagenzia.it/wp-content/uploads/2026/02/2026_02_23_AREA-FL-2022-2024.pdf ; copia: https://www.regione.lazio.it/sites/default/files/2026-03/CCNL-Area-FL-2022-2024-.pdf
- [C2] CCNL Area FL 2019-2021, 16/07/2024 (D, copia Prefettura): https://prefettura.interno.gov.it/sites/default/files/101/2024-09/ccnl-area-funzioni-locali-2019-2021.pdf
- [C3] CCNL segretari 16/05/2001 (D, indice e titoli): https://prefettura.interno.gov.it/sites/default/files/1/2024-03/ccnl_16_maggio_2001_normativo_1998-2001_economico_1998-1999.pdf ; CCNI 22/12/2003 (D): https://prefettura.interno.gov.it/sites/default/files/1/2024-03/accordo_22_dicembre_2003.pdf

**Ministeri e organismi**

- [M1] DAIT, pareri su art. 86 (E): https://dait.interno.gov.it/pareri/14357 , https://dait.interno.gov.it/pareri/99124
- [M2] Osservatorio, atto di orientamento art. 86 c. 2 (D): https://dait.interno.gov.it/documenti/osservatorio-fl-atto-orientamento-versamento-forfettario-oneri.pdf
- [M3] Ministero del lavoro, LSU (D): https://lavoro.gov.it/temi-e-priorita/ammortizzatori-sociali/focus-on/lsu/pagine/lavori-socialmente-utili-lsu
- [M4] Bozza di convenzione, Prefettura (D): https://prefettura.interno.gov.it/sites/default/files/21/2024-03/10._bozza_convenzione_semplificata.doc

**Giurisprudenza e terzi**

- [G1] Cass. 22036/2025 (E, riproduzione): https://www.studiocerbone.com/?p=499982
- [T1] Riepilogo circolare INPS (E): https://enasc.it/2026/02/03/inps-gestione-separata-le-nuove-aliquote-contributive-per-lanno-2026/
- [T2] Importo assegno LSU, stampa non datata (E): https://www.pensionioggi.it/notizie/lavoro/lavori-socialmente-utili-l-assegno-e-pari-a-580-euro-al-mese-65467457
- [T3] Contributo 2026 comuni (E): https://www.mysolution.it/lavoro/informazioni/news/2026/09/07/prevista-lerogazione-del-contributo-annualita-2026-ai-comuni-con-meno-di-5.000-abitanti-per-la-stabilizzazione-lsu
- [E3] Risposta ARAN riportata (E): https://www.segretaricomunalivighenzi.it/?p=58932
- [E4] Commento e determine su oneri scavalco (E): https://www.lapostadelsindaco.it/servizi_pubblica_amministrazione/15208_compenso-spettante-al-segretario-comunale-con-incarico-a-scavalco.html
- [E5] Corte conti Liguria, indennità di scavalco (E): https://www.corteconti.it/Download?id=e1f7b369-51f6-42c7-b477-b2a97e0fc425
- [E6] Corte conti Lombardia 96/2022 e art. 2 D.M. 17/03/2020, come riportati (E): https://www.segretaricomunalivighenzi.it/?p=39602
- [E7] Commento a Lombardia 125/2020 (D il commento, E la deliberazione): https://www.segretaricomunalivighenzi.it/28-10-2020-spesa-per-le-sedi-convenzionati-di-segreteria-il-trionfo-dellirrazionalita/28/10/2020
