# Autoliquidazione INAIL per gli enti locali: regime, soggetti, base, scadenze, F24EP, tracciato, infortuni

Ticket: #52 (mappa #1). Data ricerca: 2026-11-06.

## Domanda

Come si assicura e come si autoliquida il premio INAIL per il personale di un ente locale? In particolare:

1. L'ente locale è in gestione ordinaria con premio, o in gestione per conto dello Stato? Da quale norma dipende?
2. Chi è assicurato (comparto, dirigenza, segretario, amministratori, co.co.co., LSU/LPU)?
3. Qual è la base imponibile del premio e quali voci di tariffa riguardano il personale dell'ente?
4. Quali sono le scadenze (dichiarazione delle retribuzioni, regolazione e rata, rate, riduzione del presunto)?
5. Come si versa in F24EP, e si possono compensare i crediti INAIL?
6. Com'è fatto il tracciato telematico della dichiarazione delle retribuzioni?
7. Risposta alla domanda 7 di `canali-input.md`: regime INAIL e servizi per i certificati di infortunio.

Questo documento riporta fatti riscontrati. Le decisioni spettano all'intervista e alle ADR (in particolare l'ADR 0024).

## Avvertenza sul metodo

**Legenda**

- **norma certa**: letta sul testo primario (norma, istruzione o circolare INAIL). Accanto è indicato che cosa è stato letto.
- **prassi-interpretazione**: deduzione del ricercatore da testi certi, oppure prassi dell'INAIL o dottrina senza un testo normativo dedicato.
- **da verificare**: non aperto, o aperto solo in parte. È scritto che cosa è stato provato.

**Regola sugli importi.** Per aliquote, tassi, importi e voci di tariffa servono due fonti indipendenti. Dove c'è solo il testo primario è scritto «**norma certa** il testo; seconda fonte **da verificare**». Dove c'è solo una fonte secondaria è scritto «**da verificare**».

**Come sono state lette le fonti.** Ogni riferimento tra parentesi quadre rinvia alla sezione Fonti, che distingue i testi letti direttamente (D) da quelli visti solo da estratti o da fonti secondarie (E).

**Aperti direttamente, 06/11/2026**

- Normattiva, testo vigente con `!vig=2026-11-06`: D.P.R. 1124/1965 artt. 1, 4, 9, 10, 12, 28, 29, 44, 52, 53, 116, 127, 128; D.Lgs. 38/2000 artt. 1, 4, 5; D.Lgs. 314/1997 art. 6; D.Lgs. 151/2015 art. 21; D.Lgs. 81/2008 artt. 3 e 18; L. 449/1997 art. 59; L. 144/1999 art. 55; D.L. 25/2025 art. 12; D.L. 185/2008 art. 32-ter. Gli artt. 28, 29 e 44 del D.P.R. 1124/1965 sono stati aperti anche con `!vig=2027-01-02`.
- INAIL, PDF scaricati dal sito: Istruzione operativa del 22/12/2025 sull'autoliquidazione 2025/2026; Guida all'autoliquidazione 2025/2026 (versione dell'8/1/2026, 68 pagine, con specifiche dei tracciati TXT e JSON); Circolare 38/2025 (voce 0722); Circolare 1/2026; guida illustrativa alle tariffe 2019, gestione Altre attività; Manuale utente «Comunicazione di infortunio telematica» v. 1.9.
- Ministero del lavoro: decreto interministeriale 2/4/2026 (PDF).
- Pagina INAIL «Gestione per conto Stato» (letta tramite estrazione automatica del testo).

**Non aperti o aperti solo in parte**

- **Circolare INAIL 62/2025** (gestione per conto dello Stato): l'indirizzo provato ha dato 404. È nota solo dalle citazioni della Circolare 1/2026 e da fonti secondarie.
- **D.M. 10/10/1985** (gestione per conto dello Stato) e **D.M. 9/2/2015** (termine del 28 febbraio): non letti. Sono noti solo perché citati da testi che ho letto.
- **Tariffa dei premi (D.M. 27/2/2019)**: il testo completo con le declaratorie e i tassi medi non è stato letto. Ho letto la guida illustrativa INAIL e il decreto di modifica del 2/4/2026. Quest'ultimo è un PDF a più colonne: l'associazione tra voce e testo può essere sfalsata e non l'ho usata per attribuire testi a voci.
- **Circolare INAIL 28/2026** (modifiche alle modalità di applicazione delle tariffe): vista solo da riassunti. Non letta.
- **Nota INAIL dell'8/1/2026** con i coefficienti degli interessi, sito MEF con il tasso medio 2025, circolari 29/2025 e 48/2025 sui minimali: non aperti.
- **Istruzioni F24EP dell'Agenzia delle Entrate e della RGS**: non trovate. Ho trovato solo la norma (art. 32-ter D.L. 185/2008) e le istruzioni dell'INAIL per il modello F24EP.
- **D.Lgs. 33/2025** (testo unico versamenti e riscossione, in vigore dal 1/1/2027): l'INAIL lo cita per i termini che cadono di sabato o di festivo. Il suo articolo 8, comma 1, e l'articolo 5, comma 3, dell'allegato non sono stati aperti: il portale restituiva l'atto intero senza posizionarsi sull'articolo.
- **Istruzione operativa 2026/2027**: non esiste ancora (di norma esce a fine dicembre). Le date 2027 sono calcolate da me.
- **Servizi online INAIL**, manuali di AL.P.I. online e dell'invio telematico, specifiche XSD della comunicazione di infortunio: non aperti. Il manuale della comunicazione di infortunio è stato letto per la parte descrittiva.
- Decreti MEF di aggiornamento dell'elenco delle amministrazioni in gestione per conto dello Stato: non cercati.
- Cassazione 22036/2025: non riaperta. Il tema è già in `regimi-titolo-compenso.md`, sezione A3.

**Vault.** `vault-pa` non è stato usato: nessuna affermazione poggia sul vault.

**Limiti dei PDF INAIL.** Il testo è estratto con `pdftotext`. Nelle note a piè di pagina alcune frasi sono sfalsate (per esempio un riferimento a un decreto-legge appare incollato a una data futura). Dove conta è segnalato.

## Sintesi

**Correzioni alla domanda del ticket.** Cinque rimandi o date del ticket non coincidono con quanto letto.

| Nel ticket | Che cosa risulta | Marcatura |
|---|---|---|
| Dichiarazione delle retribuzioni entro il 16 febbraio | Il 16 febbraio è la scadenza del **versamento** (premio in unica soluzione o prima rata) e della comunicazione del presunto ridotto. La **dichiarazione delle retribuzioni** scade il **28 febbraio** (29 negli anni bisestili), prorogato al primo giorno lavorativo se cade di sabato o festivo. Nel 2026: 2 marzo. | **norma certa** il testo della guida e dell'istruzione INAIL; il D.M. 9/2/2015 citato non è letto |
| Rate al 16/2, 16/5, 16/9, 16/11 | Le scadenze sono **16/2, 16/5, 16/8, 16/11**, con gli slittamenti di calendario (nel 2026: 16/2, 18/5, 20/8, 16/11) | **norma certa** art. 44 c. 2-3 D.P.R. 1124/1965 e art. 55 c. 5 L. 144/1999; guida INAIL |
| Riduzione del presunto: art. 28 c. 2 | È l'art. 28 c. 6. Il testo dice 20 febbraio, l'INAIL istruisce 16 febbraio | testo **norma certa**; il 16 febbraio è **prassi-interpretazione** |
| Art. 18 D.Lgs. 151/2015 per il certificato di infortunio | L'art. 18 di quel decreto riguarda il lavoro all'estero. La norma pertinente è l'**art. 21** | **norma certa** |
| Art. 1 c. 3 D.Lgs. 314/1997 per la base imponibile | Il testo che sostituisce l'art. 29 D.P.R. 1124/1965 è l'**art. 6** D.Lgs. 314/1997. L'art. 1 modifica l'art. 46 TUIR | **norma certa** |

**Risposte in breve**

1. **Gli enti locali sono in gestione ordinaria, con premio.** L'art. 127 c. 2 D.P.R. 1124/1965 parla solo di «dipendenti dello Stato». Dal 1/1/2026 il D.L. 25/2025 art. 12 c. 1-ter e 1-quater elenca le amministrazioni in gestione per conto dello Stato: comuni, province, regioni e unioni non ci sono. **norma certa** il testo; la conclusione è una deduzione (**prassi-interpretazione**), perché l'elenco è aggiornabile con decreto MEF e non ho cercato decreti successivi.
2. **Personale dell'ente.** Il comparto è assicurato per l'attività protetta (per gli impiegati, in pratica, l'attività d'ufficio con apparecchi elettrici). I dirigenti sono assicurati per legge anche con polizze private, con retribuzione pari al massimale di rendita. I co.co.co. sono assicurati se svolgono attività protette; il premio è per 2/3 del committente. Per amministratori e segretari vedi i punti 2.3 e 2.5.
3. **Base imponibile: reddito di lavoro dipendente lordo** (art. 29 D.P.R. 1124/1965 come sostituito dall'art. 6 D.Lgs. 314/1997), con i minimali. Le voci di tariffa sono assegnate dall'INAIL, che le comunica ogni anno nelle «basi di calcolo»; per un ente locale la voce tipica degli uffici è la 0722, ma l'elenco completo delle voci dell'ente non è stato ricostruito.
4. **Una sola dichiarazione e un solo importo.** Regolazione dell'anno precedente e rata dell'anno si sommano algebricamente in un unico versamento. La dichiarazione delle retribuzioni (28/2) è un adempimento separato dal pagamento (16/2).
5. **F24EP, sezione «N», causale P, codice tributo 902026 per il ciclo 2025/2026.** Con l'F24EP **non si compensa** tra crediti e debiti. **norma certa** il testo della guida INAIL.
6. **Tracciato:** TXT con record 010 (quadratura) e record 100 (modello 1031, uno per ogni voce di tariffa), oppure JSON in archivio ZIP (massimo 500 fogli salari). **norma certa** il testo della guida INAIL.
7. **Infortuni:** denuncia entro due giorni dalla notizia se la prognosi supera tre giorni; comunicazione entro 48 ore dal certificato se la prognosi va da uno a tre giorni. Il certificato lo trasmette il medico all'INAIL, non l'ente. **norma certa**.

**Punti che possono cambiare il modello**

1. La **dichiarazione delle retribuzioni e il pagamento non hanno la stessa data.** L'ADR 0024 parla di una vista annuale che raccoglie regolazione e rata; i due termini (dichiarazione e pagamento) vanno tenuti distinti.
2. La **voce di tariffa non è calcolabile dall'ente.** Arriva dall'INAIL con le basi di calcolo e può cambiare in corso d'anno (due periodi di classificazione nello stesso anno, campo dedicato nel tracciato).
3. Il **tasso di interesse** per le rate successive alla prima è un dato annuale esterno (tasso medio dei titoli di Stato dell'anno precedente, pubblicato dal MEF), non una costante.
4. L'**F24EP non compensa.** Un credito INAIL non si può usare in quel modello. Il credito rientra in un F24 ordinario con saldo zero.
5. **Dal 2027** cambiano la numerazione del TUIR e la regola del giorno lavorativo successivo (il testo unico del D.Lgs. 33/2025 è richiamato dall'INAIL «dall'1.1.2027»). Normattiva con `!vig=2027-01-02` mostra l'art. 29 D.P.R. 1124/1965 ancora con i rinvii agli artt. 46 e 48 del TUIR attuale: va ricontrollato (vedi `regimi-titolo-compenso.md`, punto 5).

## Findings

### 1. Regime degli enti locali

- **Art. 127 D.P.R. 1124/1965** (testo vigente al 06/11/2026) [N1]. Dopo l'elenco dei soggetti non assicurati presso l'INAIL, il testo prosegue: «Per i dipendenti dello Stato l'assicurazione presso l'INAIL può essere attuata con forme particolari di gestione e può anche essere limitata a parte delle prestazioni». Le norme sono emanate dal Ministro del tesoro di concerto con altri. **norma certa**. Il testo non nomina enti locali.
- **Art. 128**, ultimo comma [N1]: un decreto può incaricare l'INAIL di erogare prestazioni per infortuni in servizio dovute dalle «Amministrazioni dello Stato» a persone non soggette all'obbligo dell'assicurazione. **norma certa**.
- **Art. 9 c. 1** [N1]: sono datori di lavoro soggetti al titolo I «le persone e gli enti privati o pubblici, compresi lo Stato e gli Enti locali» che nell'esercizio delle attività dell'art. 1 occupano persone dell'art. 4. **norma certa**. Per gli enti locali vale quindi il regime ordinario del titolo I.
- **Art. 1 c. 1 lett. d) D.Lgs. 38/2000** [N2]: ai fini tariffari è istituita la gestione «altre attività», che comprende le attività svolte dagli enti pubblici, «compresi lo Stato e gli enti locali». **norma certa**. Questo dice dove sta l'ente nella tariffa, non il regime.
- **D.L. 25/2025 art. 12 c. 1-ter e 1-quater** [N3]. Dal 1/1/2026 la gestione per conto dello Stato (art. 127 c. 2 e D.M. Tesoro 10/10/1985, G.U. n. 46 del 25/2/1986) si applica, oltre che ai dipendenti delle amministrazioni statali, ai dipendenti delle amministrazioni elencate: organi di rilevanza costituzionale, Avvocatura dello Stato, TAR, Presidenza del Consiglio, Ministeri, istituzioni scolastiche statali, università pubbliche, istituzioni AFAM, alcuni istituti e agenzie nazionali (INGV, INAF, ISTAT, CNR, Agenzia delle entrate, Agenzia delle dogane e dei monopoli, Agenzia industrie difesa, ISS, Ispettorato nazionale del lavoro) e le scuole delle province autonome di Trento e Bolzano. L'elenco è aggiornato periodicamente con decreto MEF di concerto con il Ministero del lavoro. **norma certa** il testo. Comuni, province, regioni, città metropolitane e unioni non compaiono.
  - Conclusione: gli enti locali restano in gestione ordinaria. **prassi-interpretazione**: deduzione dall'elenco, non da un testo che lo dica espressamente. Il Manuale INAIL della comunicazione di infortunio [I6] chiama la gestione ordinaria «IASPA», cioè «Industria, Artigianato, Servizi e Pubbliche Amministrazioni», e distingue la «Pubblica amministrazione in gestione per conto dello Stato»: indizio coerente, non prova.
  - Decreti MEF successivi che aggiungano altri soggetti: **da verificare**. Non cercati.
- **Come funziona la gestione per conto dello Stato** (per distinguerla). Lo Stato non versa premio. Rimborsa all'INAIL le spese delle prestazioni erogate, esclusa l'indennità giornaliera per inabilità temporanea assoluta [I8]. Quindi nessuna autoliquidazione. **norma certa** il testo del D.P.R. e del D.L. 25/2025; la descrizione del meccanismo viene dalla pagina INAIL [I8], letta tramite estrazione automatica del testo (**prassi-interpretazione**).
- La **Circolare 62/2025** (definizione dell'ambito) è citata dalla Circolare 1/2026 [I4] con il titolo «Assicurazione con la speciale forma della gestione per conto dello Stato per i dipendenti delle amministrazioni pubbliche - definizione ambito di applicazione». Non letta. **da verificare** se tratta espressamente gli enti locali.
- **Unione di comuni, comunità montane, aziende speciali, istituzioni, società partecipate dell'ente:** regime non esaminato. **da verificare**.

### 2. Chi è assicurato

#### 2.1 Comparto (impiegati, operai, polizia locale)

- **Art. 4 c. 1 n. 1 D.P.R. 1124/1965** [N1]: sono assicurati coloro che prestano alle dipendenze e sotto la direzione altrui «opera manuale retribuita». **norma certa**. Per gli impiegati la tutela dipende dall'art. 1 c. 1 (persone addette ad apparecchi e impianti elettrici) e c. 4 (sono addetti anche coloro che compiono funzioni per effetto delle quali sono esposti al pericolo di infortunio prodotto da quegli apparecchi). **norma certa**.
- La Circolare INAIL 38/2025 [I3] ricostruisce che l'obbligo per il personale d'ufficio esposto al «rischio elettrico» è frutto di giurisprudenza (Cassazione, Corte costituzionale 114/1977 e 221/1986) e che la voce 0722 copre l'attività d'ufficio. **norma certa** il testo della circolare; la lettura della giurisprudenza è dell'INAIL (**prassi-interpretazione**).
- Quindi, in pratica, il personale amministrativo di un ente è assicurato quando usa non occasionalmente macchine o apparecchi elettrici (computer, stampanti). **prassi-interpretazione**. Non ho trovato un testo che dica «tutti i dipendenti degli enti locali sono assicurati».
- Polizia locale, operai, autisti, addetti al verde e alle manutenzioni, personale di nidi e cucine: assicurati per le attività protette dell'art. 1. Classificazione tariffaria caso per caso: vedi sezione 3.

#### 2.2 Dirigenti

- **Art. 4 D.Lgs. 38/2000** [N2]: sono soggetti all'obbligo i dipendenti dei datori di lavoro dell'art. 9 T.U. appartenenti all'area dirigenziale, **anche qualora vigano tutele con polizze privatistiche**. La retribuzione valida ai fini del premio e delle prestazioni è pari al **massimale per la liquidazione delle rendite** (art. 116 c. 3 T.U.). Un decreto ha individuato i riferimenti tariffari. **norma certa**.
- Il massimale è fissato ogni anno con decreto (art. 116 c. 3 T.U., letto [N1]). Valore 2025 e 2026 e tariffa applicata: **da verificare**. Non cercati.
- Chi, in un ente locale, rientra nell'«area dirigenziale» (dirigenti a tempo indeterminato, art. 110 TUEL, alte specializzazioni, posizioni organizzative): **da verificare**. Nessun testo o circolare letta.

#### 2.3 Amministratori

- Rinvio a `regimi-titolo-compenso.md`, sezione A3. Lì: Cass. 22036/2025 (letta da riproduzione) afferma che il sindaco non rientra tra i tutelati del T.U. e che il dipendente in aspettativa per l'intero mandato ha tutela ex art. 86 TUEL.
- Nuova informazione: l'art. 9 T.U. [N1] porta le note delle sentenze della Corte costituzionale 98/1990 e 171/2002; quest'ultima estende la tutela ai lavoratori in aspettativa per cariche sindacali. Non riguarda gli amministratori locali. **norma certa** il testo. Non c'è analogo intervento sugli amministratori.
- Premio e posizione INAIL per l'amministratore dipendente in aspettativa: **da verificare**. Non ho trovato istruzioni INAIL sul calcolo del premio (retribuzione di riferimento, voce, chi versa).

#### 2.4 Co.co.co.

- **Art. 5 D.Lgs. 38/2000** [N2], testo vigente: obbligo per i parasubordinati dell'art. 49 c. 2 lett. a) TUIR (testo attuale) se svolgono attività dell'art. 1 T.U. o se, per le mansioni, usano non occasionalmente veicoli a motore da loro condotti personalmente; il committente è tenuto a tutti gli adempimenti del datore di lavoro; premio **1/3 a carico del lavoratore e 2/3 del committente**; base imponibile: compensi effettivamente percepiti, con i limiti dell'art. 116 c. 3. **norma certa**.
- La **Guida INAIL 2025/2026** [I2] istruisce che il campo «Retribuzioni complessive» include «i compensi erogati ai collaboratori coordinati e continuativi e ai collaboratori a progetto». La base si determina con le regole del lavoro dipendente (art. 50 e 52 TUIR). **norma certa** il testo della guida.
- Come l'ente recupera 1/3 dal collaboratore: non letto. **da verificare**.
- Rinvii: dal 1/1/2027 le lettere del TUIR cambiano (regimi-titolo-compenso, punto 5). Il rinvio dell'art. 5 va ricontrollato.

#### 2.5 Segretario comunale

- Segretario titolare, in convenzione, a scavalco: nessun testo INAIL specifico trovato. **da verificare**. Se rientri nell'«area dirigenziale» dell'art. 4 D.Lgs. 38/2000 (massimale) o nel comparto, e chi sia il datore di lavoro ai fini INAIL (ente o Ministero): non risolto.

#### 2.6 LSU/LPU

- La guida illustrativa INAIL sulla gestione Altre attività [I5] descrive la **voce 0617** come «riferimento per coloro che effettuano lavori socialmente utili o sono impegnati in attività gratuite a fini di utilità sociale». **norma certa** il testo della guida (che è un documento illustrativo dell'INAIL, **prassi-interpretazione** quanto al valore).
- Chi paga, retribuzione di riferimento per il premio, e se l'ente deve dichiarare queste persone nella dichiarazione delle retribuzioni: **da verificare**. L'obbligo dell'ente utilizzatore è indicato in `regimi-titolo-compenso.md` (art. 8 c. 9 D.Lgs. 468/1997, letto lì). Non riaperto.
- Il Manuale INAIL [I6] prevede una polizza «VOLONTARI» per volontari, detenuti e soggetti in lavori di pubblica utilità giudiziari. Non è il caso LSU/LPU.

### 3. Base imponibile e voci di tariffa

#### 3.1 Base imponibile

- **Art. 29 D.P.R. 1124/1965** [N1], testo sostituito dall'**art. 6 D.Lgs. 314/1997** [N4]: sono redditi di lavoro dipendente ai fini contributivi quelli dell'art. 46 c. 1 TUIR maturati nel periodo; si applica l'art. 48 TUIR; gli importi sono al lordo di contributi e trattenute; l'elenco delle **esclusioni è tassativo** (c. 5): TFR, somme per incentivare l'esodo, risarcimenti, somme a carico di gestioni previdenziali, previdenza complementare entro i limiti, trattamenti di famiglia; gratifiche, conguagli retroattivi e premi di produzione si contano nel mese di corresponsione (c. 9). **norma certa**.
- Art. 29 c. 8: restano ferme le norme sul minimale (art. 1 D.L. 338/1989) e sui minimi e massimi imponibili. **norma certa**.
- La Guida INAIL 2025/2026 [I2] (pagine 2-4) istruisce: retribuzione effettiva = ammontare lordo del reddito di lavoro dipendente (art. 51 TUIR e art. 29 T.U.); va portata al più alto tra minimale contrattuale (art. 1 D.L. 338/1989) e minimale di retribuzione giornaliera (art. 1 D.L. 402/1981, rivalutato Istat); retribuzione convenzionale per categorie con decreto; retribuzione di ragguaglio solo in via residuale; part-time con retribuzione oraria convenzionale. I limiti 2025 sono nelle circolari 29/2025 e 48/2025 (non aperte). **norma certa** il testo della guida. Importi del minimale 2026: **da verificare**.
- Rispetto alla traccia del ticket: l'art. 1 c. 3 D.Lgs. 314/1997 **non** è la fonte (vedi Sintesi).
- Il campo «Retribuzioni complessive» del tracciato somma le retribuzioni dei dipendenti, comprese quelle con esenzione inferiore al 100%, e i compensi dei co.co.co. [I2]. **norma certa** il testo.
- Le retribuzioni «parzialmente esenti» e le riduzioni (Tabella dei codici da H a Y, ecc.) riguardano sgravi per assunzioni e simili. Quali ne spettino a un ente locale: **da verificare**. Non esaminato.
- Dirigenti: massimale, vedi 2.2.
- Per il 2027: il rinvio dell'art. 29 al TUIR (artt. 46 e 48) non risulta modificato su Normattiva al 06/11/2026 con `!vig=2027-01-02`. **da verificare** dopo l'entrata in vigore del nuovo testo unico (D.Lgs. 117/2026, già citato in `regimi-titolo-compenso.md`).

#### 3.2 Gestione tariffaria e voci

- L'ente locale è inquadrato nella gestione **«Altre attività»** (art. 1 c. 1 lett. d) D.Lgs. 38/2000 [N2]; campo «Gest. inq.», valore 4, nel tracciato [I2]). **norma certa**.
- Le **basi di calcolo** comunicate dall'INAIL nel «Fascicolo aziende» riportano per ogni codice ditta: gestione tariffaria, voce, tasso medio di tariffa, tasso applicabile (dopo due anni di attività), tasso applicato (corretto delle riduzioni per prevenzione), le agevolazioni con il loro codice [I2]. Il datore di lavoro non calcola il tasso. **norma certa** il testo.
- **Tariffa in vigore:** D.M. 27/2/2019 (lavoratori dell'«Industria, Artigianato, Terziario e Altre attività») [I2, I7]. La modifica dell'aliquota di oscillazione («bonus») e di alcune descrizioni è nel **decreto interministeriale 2/4/2026**, registrato alla Corte dei conti il 15/5/2026, effetto dal 1/1/2026 [I7: premesse e allegato letti; la registrazione e il numero 565 compaiono solo nei riassunti, **da verificare**]. Il decreto non sostituisce la tariffa del 2019: ne modifica le modalità di applicazione. **norma certa** il testo del decreto sulle premesse (richiama il D.M. 27/2/2019); nuova tariffa dei premi per il 2027: non trovata. **da verificare**.
- **Voci tipiche** (dalla guida illustrativa 2019, gestione Altre attività [I5]):

| Voce | Contenuto secondo la guida | Uso presumibile in un ente |
|---|---|---|
| 0722 | Attività d'ufficio, sportelli informatizzati, call center. Compreso l'uso del veicolo personalmente condotto per accedere ad altri uffici | Personale amministrativo (**prassi-interpretazione**) |
| 0723 | Attività amministrative, commerciali o tecniche con accessi sistematici in cantieri, opifici e simili | Personale tecnico con sopralluoghi (**prassi-interpretazione**) |
| 0721 | Personale con mansioni operative anche di servizio (nella guida: ordinamento corrispondenza e recapito; nella declaratoria successiva: uscieri, autisti, piccola manutenzione) | Uscieri, autisti, piccola manutenzione (**prassi-interpretazione**: il PDF del decreto del 2026 è a colonne e l'associazione va controllata) |
| 0617 | Lavori socialmente utili e attività gratuite a fini di utilità sociale | LSU (**prassi-interpretazione**) |
| 0615 | Asili nido e ludoteche | Servizi educativi |
| 0311 | Prestazioni assistenziali e sanitarie, residenziali, semiresidenziali, domiciliari | Servizi sociali |
| 0410 | Pulizie e sanificazione | Pulizie in economia |
| 0712 | Guardiania e sorveglianza | Custodia |

  Marcatura: la guida è un documento INAIL, **norma certa** quanto a ciò che dice; l'uso presumibile nell'ente è **prassi-interpretazione**, non c'è un testo che attribuisca queste voci agli enti locali. Il collegamento a **polizia locale, operai edili e stradali, manutenzione del verde, raccolta rifiuti, cimiteri, mense** non è stato riscontrato: **da verificare**. La classificazione è dell'INAIL, in base alle lavorazioni dichiarate nella denuncia (art. 12 T.U. [N1]).
- **Circolare 38/2025** [I3]: la voce 0722 ha autonomia classificativa anche se l'attività è complementare o sussidiaria. Sono escluse le operazioni di cassa e la realizzazione di software e siti web (voce 0726). L'elenco di attività della voce non è tassativo. Dal 1/7/2023 vi rientrano le attività amministrative per società sportive dilettantistiche e dal 1/1/2024 i giornalisti subordinati. **norma certa** il testo (letto da estratti di ricerca e dal PDF della circolare).
- **Tassi medi di tariffa** per voce: non letti. Il decreto 2/4/2026 e la guida 2019 non riportano le tabelle dei tassi. **da verificare**. Servono due fonti.
- **Voce come fatto datato.** La guida prevede **due periodi classificativi** nello stesso anno (campi «Dal/Al», campi 41-42 del record) [I2]. Quindi la voce ha una data di inizio e una di fine, e può cambiare in corso d'anno. **norma certa** il testo della guida. Per il cambio della classificazione, il decreto 2/4/2026 modifica gli artt. 7 e 8 delle modalità: la rettifica decorre dal primo giorno del mese successivo alla comunicazione INAIL (**da verificare**, visto solo in riassunti).

### 4. Scadenze

#### 4.1 Quadro normativo e prassi

| Adempimento | Termine | Fonte | Marcatura |
|---|---|---|---|
| Versamento rata anticipata e regolazione | **16 febbraio** (unica soluzione o prima rata) | Art. 44 c. 2 T.U. dice «20 febbraio»; art. 55 c. 5 L. 144/1999 unifica i termini degli artt. 44 c. 2, 3 e 4 «al giorno 16 dei rispettivi mesi di scadenza» [N1, N6]; Istruzione INAIL 22/12/2025 [I1] | **norma certa** |
| Quattro rate | **16/2, 16/5, 16/8, 16/11**, ciascuna 25% del premio annuale; interessi sulle rate dalla seconda | Art. 44 c. 3 T.U. (testo originale: 20/2, 31/5, 31/8, 30/11), art. 59 c. 19 L. 449/1997 e art. 55 c. 5 L. 144/1999 [N1, N5, N6]; Guida [I2] | **norma certa** |
| Regolazione | Sempre in **unica soluzione**, anche se la rata è in quattro tranche | Art. 44 c. 3 T.U. [N1] | **norma certa** |
| Rateizzazione della regolazione | L'art. 55 c. 5 L. 144/1999 dice che la rateizzazione «si applica anche alla regolazione» di cui all'art. 28 c. 5. L'art. 44 c. 3 dice che la regolazione va in unica soluzione. Le istruzioni INAIL 2025/2026 parlano di «premio di autoliquidazione» in quattro rate, cioè regolazione più rata sommate | [N1, N6, I1, I2] | Contrasto tra le due norme: **da verificare** come l'INAIL lo risolve. L'istruzione dice che il premio di autoliquidazione, cioè la somma, si può pagare in quattro rate |
| Dichiarazione delle retribuzioni | **28 febbraio** (29 se bisestile), prorogato al primo giorno lavorativo se sabato o festivo | Art. 28 c. 4 T.U. dice «20 febbraio»; l'INAIL cita il D.M. 9/2/2015 [I1, I2] | **norma certa** il testo INAIL; D.M. 9/2/2015 **da verificare** (non letto). Nel 2026 il termine è il 2 marzo [I1] |
| Comunicazione di riduzione del presunto | Entro il **16 febbraio**, con servizio «Riduzione Presunto» (online dal 2 gennaio) | Art. 28 c. 6 T.U.: testo dice «20 febbraio»; l'INAIL indica 16 febbraio [N1, I1] | testo **norma certa**; 16 febbraio **prassi-interpretazione** |
| Cessazione dell'attività | Dichiarazione entro il giorno 16 del secondo mese successivo; il testo di legge dice giorno 20 | Art. 28 c. 4 T.U. [N1]; Guida [I2] | **norma certa** il testo; servizio «Autoliquidazione ditte cessate» |
| Contributi associativi | 16 febbraio, unica soluzione | [I1] | **norma certa** il testo INAIL. Che un ente locale ne abbia: **da verificare** |
| Mancata dichiarazione | L'INAIL accerta le retribuzioni o liquida premio e rata sul **doppio** delle retribuzioni presunte dell'ultimo periodo | Art. 28 T.U., periodo finale [N1] | **norma certa** |
| Sanzione per omessa o tardiva comunicazione | Da 125 a 770 euro se non c'è premio inferiore al dovuto; altrimenti sanzioni civili sul premio | Guida [I2], che cita art. 195 T.U. (non letto) e art. 116 L. 388/2000 (non letta) | **norma certa** il testo della guida; norme citate **da verificare** |

**Come si arriva a 16 e non a 20.** Il testo dell'art. 44 conserva il 20 febbraio. L'art. 55 c. 5 L. 144/1999 lo ha portato al 16, e Normattiva lo riporta come nota all'articolo. Lo stesso vale per le rate. **norma certa**. Per la dichiarazione (art. 28 c. 4) e per il presunto (art. 28 c. 6) il testo conserva il 20 febbraio e non c'è una nota analoga: il 28 febbraio viene da D.M. 9/2/2015 citato dall'INAIL, il 16 febbraio del presunto dall'istruzione INAIL. **prassi-interpretazione**.

#### 4.2 Calendario 2026 (ciclo 2025/2026, letto)

- 16/2/2026 versamento in unica soluzione o prima rata. 2/3/2026 dichiarazione delle retribuzioni (28/2 era sabato). Rate: 16/2, **18/5** (il 16 era sabato), **20/8**, 16/11/2026 [I1, I2]. **norma certa** il testo.
- Slittamento dell'agosto al 20: la guida cita il D.L. 16/2012 e lo scrive in modo sfalsato nel PDF. Il riferimento esatto non è riscontrato. **da verificare**.
- Slittamento per sabato e festivo: art. 18 c. 1 D.Lgs. 241/1997, citato dalla guida. Per gli enti pubblici anche art. 32-ter c. 1-bis D.L. 185/2008, letto [N7]: versamento entro il 16 del mese; se cade di sabato o festivo, tempestivo il primo giorno lavorativo successivo. **norma certa**.
- Oggi (06/11/2026) resta da pagare solo la quarta rata del 16/11/2026, per chi ha scelto le rate.

#### 4.3 Calendario 2027 (ciclo 2026/2027, calcolato)

Date calcolate dal ricercatore sul calendario. L'istruzione INAIL 2026/2027 non è ancora uscita.

| Adempimento | Data nominale | Data calcolata | Marcatura |
|---|---|---|---|
| Versamento / prima rata | 16/2/2027 (martedì) | 16/2/2027 | **prassi-interpretazione** |
| Dichiarazione delle retribuzioni | 28/2/2027 (domenica) | 1/3/2027 | **prassi-interpretazione** |
| Seconda rata | 16/5/2027 (domenica) | 17/5/2027 | **prassi-interpretazione** |
| Terza rata | 16/8/2027 (lunedì) | 16/8/2027 o 20/8/2027 | **da verificare** (regola di agosto) |
| Quarta rata | 16/11/2027 (martedì) | 16/11/2027 | **prassi-interpretazione** |

Le date vanno confermate con l'istruzione operativa 2026/2027, di norma pubblicata a fine dicembre. Il testo unico D.Lgs. 33/2025, citato dall'INAIL «dall'1.1.2027» per le scadenze di sabato e festivo, può cambiare la regola: **da verificare**.

#### 4.4 Rate, interessi, riduzioni

- Le rate successive alla prima portano interessi con il «tasso medio di interesse dei titoli del debito pubblico dell'anno precedente», indicato dal Ministero [N1: art. 44 c. 3; I1]. **norma certa** il testo.
- **Tasso 2025/2026:** la ricerca ha dato 2,75%, riportato da più portali che citano l'INAIL. La nota INAIL con i coefficienti e il sito MEF non sono stati aperti. **da verificare**. Seconda fonte primaria mancante.
- **Scelta della rateazione:** si comunica nella dichiarazione delle retribuzioni, campo 71 della dichiarazione online; nel TXT, record 100, valore «R» (rate) o «W» (nessuna rata) [I2]. **norma certa** il testo.
- **Riduzione del presunto** (art. 28 c. 6): la comunicazione motivata dà la base per il premio anticipato in sostituzione delle retribuzioni dell'anno precedente, salvi i controlli INAIL [I1]. **norma certa** il testo.
- **Riduzioni per le imprese artigiane** (L. 296/2006): non riguardano gli enti. **norma certa** il testo; non rilevante.
- **Bonus per andamento infortunistico:** nuove aliquote applicate in via provvisoria dal 1/1/2026, con riserva di richiedere maggiori premi (D.L. 159/2025, delibera CdA INAIL 146/2025, delibera Presidente 17/2025) [I1]. Il decreto interministeriale 2/4/2026 le ha poi recepite [I7]. **norma certa** il testo. Se rimanga ancora un conguaglio da richiedere per il 2025/2026: **da verificare**.

### 5. Versamento in F24EP

- **Chi lo usa.** L'art. 32-ter c. 1 D.L. 185/2008 [N7] impone agli enti e organismi delle **tabelle A e B della L. 720/1984** di usare il modello «F24 enti pubblici» anche per i premi dovuti agli enti assicurativi. **norma certa**. La Guida INAIL [I2] lo ripete. Se un dato ente locale rientra nelle tabelle A o B (o in un regime di tesoreria unica «mista»): **da verificare**, non letto.
- **Compilazione** (Guida INAIL, pagina 46 [I2]). **norma certa** il testo.

| Campo F24EP | Che cosa indicare |
|---|---|
| Sezione | «N», che identifica i versamenti all'INAIL |
| Codice tributo / causale | **902026** per l'autoliquidazione 2025/2026. Il numero dipende dal ciclo: per ogni ciclo INAIL ne indica uno |
| Codice | Codice sede INAIL (cinque cifre), come per il modello ordinario |
| Estremi identificativi | Numero del **codice ditta, senza codice di controllo** (esempio dell'INAIL: se il codice ditta fosse «1234567/41», si indica «1234567») |
| Riferimento A | «P», causale per i premi |
| Riferimento B | **Non va compilato** |
| Importi a debito versati | Importo del premio |

- Nel modello F24 **ordinario** [I2]: sezione «Altri enti previdenziali e assicurativi - INAIL»; codice sede, codice ditta, codice di controllo, numero di riferimento (902026 per le PAT), causale «P». Un rigo per ogni codice contributo.
- **Divieto di compensazione.** Guida INAIL, pagina 46: «Per i versamenti disposti con il modello F24 EP non è possibile effettuare compensazioni tra importi a credito e a debito». Per compensare serve il modello F24 ordinario con saldo finale zero. **norma certa** il testo.
- **Credito a favore dell'ente.** Nel modello ordinario il saldo a credito dell'autoliquidazione deve essere usato, in tutto o in parte, per compensare debiti pregressi INAIL non iscritti a ruolo; l'eventuale resto si può usare verso altre amministrazioni; può pagare i contributi associativi; prima di compensare va verificato con la sede INAIL [I2]. **norma certa** il testo. Come si ottiene il rimborso del credito per un ente che paga solo con F24EP: **da verificare**. Art. 44 c. 4 T.U. [N1] prevede che l'INAIL rimborsi entro 60 giorni dalla comunicazione di un conguaglio ulteriore a favore del datore di lavoro, salvi i controlli. **norma certa**.
- **Seconda fonte:** istruzioni F24EP dell'Agenzia delle Entrate o della RGS: **non trovate**. Una nota INAIL del 2022 sui giornalisti, riportata da portali, indica anch'essa sezione «N» e riferimento A «P»: seconda fonte indiretta, non letta direttamente. **da verificare**.
- **Un rigo per ciascun codice contributo.** Se l'ente ha più codici contributo nelle basi di calcolo, un rigo per ciascuno [I2]. **norma certa** il testo.
- **Ciclo.** Il numero 902026 vale per l'autoliquidazione 2025/2026 e cambia ogni ciclo: per il 2026/2027 va preso dalla nuova istruzione. Per le PAN (settore marittimo) c'è invece un numero di sei cifre di ricevuta: non riguarda gli enti.
- **Arrotondamenti.** Non ho trovato istruzioni specifiche sugli arrotondamenti del premio e delle rate: **da verificare** (si veda `arrotondamenti-norma.md`).

### 6. Tracciato telematico della dichiarazione delle retribuzioni (PAT)

Fonte: Guida INAIL 2025/2026, specifiche tecniche (pagine 46-68) [I2]. **norma certa** il testo.

- **Canali.** Per i titolari di PAT: servizio «**AL.P.I. online**», che calcola anche il premio, e servizio «**Invio telematico Dichiarazione Salari**», con file nei formati **TXT** o **JSON** [I1]. Apertura dei servizi 2025/2026: 8/1/2026 per la dichiarazione, 2/1/2026 per la riduzione del presunto [I1].
- **Regole generali del file TXT.**
  - Un file contiene dati di un solo anno.
  - Un solo **record di quadratura TRK 010** all'inizio e almeno un **record retributivo TRK 100** (modello 1031).
  - Il record retributivo corrisponde al **periodo assicurativo per ogni voce di tariffa** delle basi di calcolo.
  - Massimo 1.000 record per file, compreso quello di quadratura.
  - Campi separati dal carattere `|` (esadecimale 7C). Fine record con `$`. Lunghezza del record 2000 caratteri. Campi numerici allineati a destra con riempimento a zero.
- **TRK 010, quadratura:** tipo record «010», anno di regolazione, totale record complessivi, totale record retributivi, totale record supplementari (sempre 0), totale di quadratura, nominativo o ragione sociale, codice fiscale, indirizzo, città, CAP, provincia, indicatore fonte, indicatore metodo, software utilizzato (casa produttrice e nome procedura, 30 caratteri).
- **TRK 100, retributivo (modello 1031):** tipo record «100», anno, codice sede INAIL (consentito zero se ignoto), ragione sociale, **codice ditta** e controcodice, codice fiscale, **indicatore di rateazione** («R» o «W»), richiesta di riduzione L. 296/2006 («S», «N» o vuoto), percentuale di riduzione L. 98/2013 per zone montane; poi **posizione assicurativa territoriale** (PAT) e controcodice, **voce di tariffa**, **gestione di inquadramento** (1 industria, 2 artigianato, 3 terziario, 4 altre attività), **periodo «dal» e «al»** nel formato gg/mm con eventuale secondo periodo classificativo, **retribuzioni complessive**, **quote di retribuzione parzialmente esenti** con i codici, retribuzioni soggette a sconto per tipo, dettagli dei periodi. I campi precisi con posizioni e lunghezze sono nel PDF della guida, pagine 52-61. Non riportati qui nel dettaglio.
- **Formato JSON.** Alternativa al TXT, «una migliore interazione» con i software esterni. Il file va in un **archivio ZIP**, estensione `.JSON`, massimo **500 fogli salari**. La radice si chiama `DatiSintetico` (quadratura) con gli stessi campi del TRK 010; i dati dei fogli salari seguono la stessa struttura del TRK 100; la tabella della guida riporta per ogni elemento JSON la posizione iniziale e finale nel TXT (pagine 62-68).
- **Zero.** Le aziende artigiane senza dipendenti e le aziende non artigiane con soli apprendisti devono indicare il valore zero in «Retribuzioni complessive». Non riguarda gli enti.
- **Specifiche scaricabili** (XSD, esempi, schemi JSON): non aperte. **da verificare**. L'INAIL rimanda alla pagina «Supporto - Guide e manuali operativi - Pagamento del premio assicurativo-autoliquidazione».
- **Ricevuta:** il servizio AL.P.I. online invia per posta elettronica la ricevuta con la riproduzione della dichiarazione [I2]. Un esito «dichiarato» leggibile dalla macchina: **da verificare**.
- **Limite:** le specifiche descrivono la dichiarazione delle retribuzioni **per codice ditta e PAT**. Il tracciato non prevede dettaglio per persona.

### 7. Certificati di infortunio e denuncia (domanda 7 di `canali-input.md`)

**Regime.** L'ente locale è in gestione ordinaria: denuncia di infortunio all'INAIL. Se invece un'amministrazione fosse in gestione per conto dello Stato, il Manuale INAIL [I6] prevede lo stesso strumento di comunicazione online con profilo dedicato. Per l'ente locale vale il profilo «Datore di lavoro» della gestione IASPA. **norma certa** il testo del manuale; la conclusione sull'ente locale è **prassi-interpretazione** (vedi sezione 1).

**Obblighi, testo vigente al 06/11/2026.**

| Evento | Obbligo | Termine | Fonte | Marcatura |
|---|---|---|---|---|
| Infortunio con prognosi **superiore a tre giorni** | **Denuncia** all'INAIL, con i riferimenti al certificato medico già trasmesso | **Due giorni da quello in cui il datore ha avuto notizia** | Art. 53 c. 1-2 T.U. [N1] | **norma certa** |
| Infortunio **mortale** o con pericolo di morte | Denuncia per telegrafo | **24 ore** dall'infortunio | Art. 53 c. 3 T.U. [N1] | **norma certa**. Il testo dice «telegrafo»: il mezzo oggi è telematico, **da verificare** |
| Prognosi guaribile in tre giorni che si prolunga al quarto | Il termine di denuncia decorre dal quarto giorno | | Art. 53 c. 4 T.U. [N1] | **norma certa** |
| Infortunio con assenza di **almeno un giorno** (escluso quello dell'evento) | **Comunicazione** a fini statistici e informativi | **48 ore dalla ricezione del certificato medico** | Art. 18 c. 1 lett. r) D.Lgs. 81/2008 [N8] | **norma certa** |
| Infortunio con prognosi superiore a tre giorni | La comunicazione a fini assicurativi si considera assolta con la denuncia dell'art. 53 | | Art. 18 c. 1 lett. r) [N8] | **norma certa** |
| Malattia professionale | Denuncia con riferimenti al certificato | **Cinque giorni** da quando il lavoratore ne ha dato notizia al datore | Art. 53 c. 5 T.U. [N1] | **norma certa** |
| Infortunio o malattia professionale **mortali o con prognosi superiore a trenta giorni** | La denuncia telematica dell'art. 53 vale come comunicazione dell'art. 54 T.U. all'autorità di pubblica sicurezza | | Art. 54 c. 1 e 5 T.U., come modificato da art. 21 D.Lgs. 151/2015 [N9] | **norma certa** il testo di modifica, art. 54 non riaperto in versione vigente |

- **Il certificato lo invia il medico.** Dal 2015 («art. 21 D.Lgs. 151/2015») qualunque medico che presti la prima assistenza deve rilasciare il certificato e **trasmetterlo esclusivamente per via telematica all'INAIL**, direttamente o tramite la struttura sanitaria, contestualmente alla compilazione. L'INAIL rende disponibili i dati delle certificazioni ai soggetti obbligati alla denuncia telematica [N1: art. 53, commi sul certificato telematico; N9]. Il datore di lavoro quindi non deve allegare il certificato, ma indicarne i **riferimenti**. **norma certa**.
- **Servizi online.** Il Manuale INAIL [I6] descrive il servizio «Comunicazione di infortunio» (prognosi fino a tre giorni) e il servizio «Denuncia/Comunicazione di infortunio» (prognosi oltre tre giorni), con accesso tramite SPID, CNS o CIE. Il datore di lavoro e i suoi delegati sono abilitati; per intermediari (consulenti del lavoro e simili) c'è un profilo diverso. L'invio può avvenire online o **tramite file** per le gestioni IASPA e conto Stato (specifiche XSD della comunicazione offline, versione 1.6, citate nel manuale, non aperte). **norma certa** il testo del manuale.
- **Cosa serve all'ente** per compilare: dati del lavoratore, rapporto di lavoro e qualifica assicurativa (codifiche ISTAT del manuale), data e ora dell'evento, luogo e dinamica, riferimenti del certificato medico, retribuzione degli ultimi quindici giorni (art. 53 T.U. [N1]: «ore lavorate e salario percepito» nei quindici giorni precedenti). **norma certa**. Dati disponibili nelle buste paga: ore e importi dei quindici giorni precedenti all'evento.
- **Intermediario.** Un consulente può inviare per conto dell'ente con delega: profilo «Intermediario del datore di lavoro» [I6].
- **Riferimento errato nel ticket:** l'art. 18 D.Lgs. 151/2015 non riguarda gli infortuni (vedi Sintesi). La riforma delle comunicazioni è nell'**art. 21**. Il manuale cita invece «art. 3, art. 18 c. 1 lett. r), e art. 21 d.lgs. 81/2008» per la comunicazione statistica.
- **Regola sugli amministratori:** per chi è tutelato (sindaco no, dipendente in aspettativa sì, secondo Cass. 22036/2025) vedi 2.3. Chi denuncia l'infortunio di un amministratore dipendente in aspettativa e con quale rapporto assicurativo: **da verificare**.
- Per il ruolo di «ricevute» e di «esiti» INAIL verso l'ente: il manuale parla di un numero progressivo assegnato alla denuncia e di una ricevuta [I6]. Formato machine-readable degli esiti: **da verificare**.

## Implicazioni per il modello

Fatti, non decisioni. Le decisioni spettano all'intervista e all'ADR.

1. **Regime.** Per un ente locale c'è un solo regime, ordinario. Non serve un campo «gestione per conto dello Stato»: se mai serve un controllo che segnali che l'ente non è in elenco. L'elenco di legge è aggiornabile con decreto, quindi la dichiarazione dell'ente deve poter dire «regime ordinario» come dato dichiarato e datato. (sezione 1; **prassi-interpretazione**)
2. **Base imponibile INAIL propria.** Coincide in larga parte con il reddito di lavoro dipendente lordo (artt. 46 e 48 TUIR), ma con elenco tassativo di esclusioni, minimale, e massimale per i dirigenti. Non coincide con l'imponibile INPS. (3.1; **norma certa**)
3. **Soggetti.** Il modello deve poter marcare per ogni compenso se rientra nella base INAIL: comparto (sì, quando attività protetta), dirigenti (retribuzione = massimale), co.co.co. (sì, compensi percepiti, 2/3 ente e 1/3 collaboratore), amministratori e segretario (aperto), LSU/LPU (aperto). (sezione 2)
4. **Voce di tariffa.** È un fatto datato sul rapporto o sulla posizione, con inizio e fine, che può cambiare più volte l'anno e che **l'ente riceve dall'INAIL**, non calcola. Un ente può avere più voci e più periodi nello stesso anno; ogni voce genera un record retributivo. Il modello dovrebbe tenerne anche il codice ditta e la PAT. (3.2; **norma certa** il testo della guida)
5. **Dichiarazione come vista annuale.** Ha due date distinte: dichiarazione delle retribuzioni (28/2 o primo giorno lavorativo) e pagamento (16/2). Contiene l'indicatore di rateazione e può contenere la riduzione del presunto. Il tracciato è per codice ditta, PAT e voce; non per persona. (4, 6)
6. **Regolazione e rata.** Si calcolano su due anni diversi (retribuzioni effettive dell'anno precedente per la regolazione; stesse retribuzioni, a meno di riduzione motivata, come presunte per la rata) e si sommano algebricamente. La regolazione non si rateizza secondo l'art. 44 c. 3, ma la guida parla di rateazione del premio di autoliquidazione: serve la lettura INAIL. (4.1; **da verificare** il contrasto)
7. **Rate e interessi.** Quattro rate uguali da 25%, interessi dalla seconda, tasso annuale esterno. Le date nominali sono 16/2, 16/5, 16/8, 16/11, con slittamenti per calendario e con la regola di agosto. Una tabella annuale di date e tassi come input. (4.4)
8. **F24EP.** Righe nella sezione «N» con causale/codice tributo del ciclo, codice sede, codice ditta senza controcodice, riferimento A «P», riferimento B vuoto. Nessuna compensazione. Per gli enti non in tabelle A e B l'F24 ordinario con campi diversi. (5)
9. **Crediti INAIL.** Se la regolazione dà un credito, non si può compensare nell'F24EP. Il modello può solo segnalarlo. Il modo per recuperarlo (compensazione in F24 ordinario, rimborso) resta aperto. (5; **da verificare**)
10. **Infortuni.** Un evento di infortunio è un fatto con prognosi, data di notizia e riferimenti del certificato; da esso derivano due scadenze diverse (due giorni dalla notizia se prognosi oltre tre giorni; 48 ore dal certificato se da uno a tre giorni). Il certificato non entra nel flusso dell'ente: lo trasmette il medico. L'ente ha bisogno dei riferimenti e della retribuzione dei quindici giorni precedenti. (7)
11. **Ciclo annuale 2026/2027.** L'istruzione operativa non è ancora pubblicata. Date, tasso, numero di riferimento F24 e voci cambiano ogni anno: devono essere dati di tabella, non codice. (4.3)
12. **Il vault** non è stato usato; nessuna cifra della guida INAIL è stata riscontrata con una seconda fonte, quindi nel modello nessun importo va considerato definitivo.

## Domande aperte

1. **Circolare INAIL 62/2025:** tratta espressamente gli enti locali? Serve il PDF.
2. **Decreti MEF** successivi a quello dell'art. 12 c. 1-quater D.L. 25/2025: l'elenco è stato esteso?
3. **Voci di tariffa** per polizia locale, operai, manutentori del verde, cimiteri, rifiuti, mense, nidi: quali voci porta in pratica un ente locale? Chiedere a Luca le basi di calcolo reali di un ente (senza dati identificativi nel repo).
4. **Tassi medi** di tariffa per la voce 0722 e le altre, con tabella della tariffa 2019 e seconda fonte.
5. **Massimale** per i dirigenti 2025 e 2026 e chi sia «area dirigenziale» in un ente (art. 110 TUEL, segretario).
6. **Segretario comunale:** datore di lavoro e inquadramento INAIL.
7. **Amministratore dipendente in aspettativa** (art. 86 TUEL, Cass. 22036/2025): retribuzione di riferimento, voce, versamento, denuncia di infortunio.
8. **Co.co.co.:** come l'ente recupera l'1/3 del premio dal collaboratore; se compare in dichiarazione per persona o solo come totale.
9. **LSU/LPU:** chi paga, quale retribuzione, voce 0617.
10. **Rateazione della regolazione:** come risolve l'INAIL il contrasto tra art. 44 c. 3 T.U. e art. 55 c. 5 L. 144/1999.
11. **Tasso di interesse 2025/2026** e coefficienti: nota INAIL 8/1/2026 e sito MEF.
12. **D.M. 9/2/2015** (28 febbraio) e **riferimento del 20 agosto**: testi non letti.
13. **F24EP:** istruzioni AdE/RGS; appartenenza di un ente locale alle tabelle A e B L. 720/1984; arrotondamento dei righi.
14. **Credito INAIL di un ente che paga in F24EP:** rimborso o compensazione in F24 ordinario con saldo zero.
15. **Specifiche scaricabili** dei tracciati (JSON schema, esempi) e **esiti** leggibili dalla macchina.
16. **Nuova tariffa 2027:** esiste una revisione della tariffa dei premi? Circolare INAIL 28/2026 e decreto del 2/4/2026 non esauriscono la questione.
17. **Dal 2027:** testo unico D.Lgs. 33/2025 (scadenze di sabato e festivo), nuovo TUIR (art. 29 T.U., art. 5 D.Lgs. 38/2000).
18. **Unioni di comuni, comunità montane, aziende speciali, istituzioni:** regime e posizione INAIL.
19. **Infortunio mortale:** modalità attuale della denuncia entro 24 ore, dato che l'art. 53 parla di telegrafo.

## Fonti

(D) letta direttamente; (E) estratto, riassunto o fonte secondaria, indicata.

**Norme, Normattiva**, tutte (D) al 06/11/2026, con base `https://www.normattiva.it/uri-res/N2Ls?` e `!vig=2026-11-06` salvo dove indicato:

- [N1] D.P.R. 1124/1965 artt. 1, 4, 9, 10, 12, 28, 29, 44, 52, 53, 116, 127, 128: `urn:nir:presidente.repubblica:decreto.del.presidente.della.repubblica:1965-06-30;1124~art127`. Artt. 28, 29 e 44 letti anche con `!vig=2027-01-02`.
- [N2] D.Lgs. 38/2000 artt. 1, 4, 5: `urn:nir:stato:decreto.legislativo:2000-02-23;38~art5`
- [N3] D.L. 25/2025 art. 12: `urn:nir:stato:decreto.legge:2025-03-14;25~art12`
- [N4] D.Lgs. 314/1997 artt. 1 e 6: `urn:nir:stato:decreto.legislativo:1997-09-02;314~art6`
- [N5] L. 449/1997 art. 59: `urn:nir:stato:legge:1997-12-27;449~art59`
- [N6] L. 144/1999 art. 55: `urn:nir:stato:legge:1999-05-17;144~art55`
- [N7] D.L. 185/2008 art. 32-ter: `urn:nir:stato:decreto.legge:2008-11-29;185~art32ter`
- [N8] D.Lgs. 81/2008 artt. 3 e 18: `urn:nir:stato:decreto.legislativo:2008-04-09;81~art18`
- [N9] D.Lgs. 151/2015 artt. 18 e 21: `urn:nir:stato:decreto.legislativo:2015-09-14;151~art21`
- D.Lgs. 33/2025: aperto solo l'art. 1 (approvazione del testo unico). Articoli dell'allegato **non letti** (E).

**INAIL, PDF scaricati dal sito (D)**

- [I1] Istruzione operativa, «Autoliquidazione 2025/2026. Istruzioni operative», 22/12/2025: `https://www.inail.it/content/dam/inail-hub-site/documenti/istruzioni-operative/2025/12/Autoliquidazione%202025-2026%20Istruzioni.pdf`
- [I2] Guida «Autoliquidazione 2025/2026. Premi e contributi associativi», versione dell'8/1/2026: `https://www.inail.it/content/dam/assicurazione/documenti/2025/12/Guida%20autoliquidazione%202025-2026.pdf`
- [I3] Circolare 24/6/2025 n. 38 (voce 0722): `https://www.inail.it/content/dam/inail-hub-site/documenti/circolari/2025/06/Circolare%20n%2038_24%20giugno%202025.pdf`
- [I4] Circolare 9/1/2026 n. 1: `https://www.inail.it/content/dam/inail-hub-site/documenti/circolari/2026/01/Circolare%20n%201_9%20gennaio%202026.pdf` (cita la Circolare 62/2025)
- [I5] Guida illustrativa alle nuove tariffe 2019, gestione Altre attività: `https://www.inail.it/content/dam/inail-hub-site/documenti/2019/04/ALTRE%20ATTIVITA'%20guida%20e%20tabelle%20_%20USO%20PUBBLICO,0.pdf`
- [I6] Manuale utente «Comunicazione di infortunio telematica», v. 1.9: `https://www.inail.it/content/dam/inail-hub-site/documenti/modulistica-prevenzione/2025/05/20250523-Manuale%20Comunicazione%20Infortunio%20Telematica%201.9.pdf`
- [I7] Decreto interministeriale 2/4/2026 (modifica delle modalità di applicazione delle tariffe del D.M. 27/2/2019), PDF del Ministero del lavoro: `https://www.lavoro.gov.it/temi-e-priorita-salute-e-sicurezza/normativa/decreto-interministeriale-del-2-aprile-2026.pdf`
- [I8] Pagina INAIL «Gestione per conto Stato», `https://www.inail.it/portale/assicurazione/it/Assicurazioni-Speciali/gestione-per-conto-stato.html` (E: testo estratto automaticamente, aggiornata al 20/1/2026).

**Fonti secondarie e non lette (E)**

- Circolare INAIL 62/2025: non scaricata (404). Nota di sintesi di un portale di settore sull'ambito della gestione per conto dello Stato dal 2026 (E).
- D.M. 9/2/2015 e riassunti sulla data del 28 febbraio, portali di settore (E).
- Tasso di interesse 2,75% per il 2025/2026: più portali di settore (E), nessuna fonte primaria aperta.
- Nota INAIL 12/12/2022 sul versamento F24EP per i giornalisti: citata da portali di settore (E).
- Circolare INAIL 28/2026 e articoli sul decreto del 2/4/2026: riassunti (E).
