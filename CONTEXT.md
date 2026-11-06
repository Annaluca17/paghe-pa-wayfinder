# Paghe Enti Locali

Modello alternativo di elaborazione delle retribuzioni per Enti Locali (CCNL Funzioni Locali). Glossario del dominio: i termini dei gestionali convenzionali (anagrafica, voce, cedolino, elaborazione mensile) non sono adottati finché un ticket non li giustifica.

## Language

### Attori

**Ente**:
Amministrazione locale da 10 a 400 dipendenti che elabora internamente le retribuzioni; utente del prototipo.
_Avoid_: Cliente, azienda

**Ufficio personale**:
Ruolo dell'ente che determina i trattamenti economici e produce gli adempimenti.
_Avoid_: Ufficio paghe

**Ragioneria**:
Ruolo dell'ente che conferma le proposte di movimento contabile, contabilizza e paga.
_Avoid_: Finanziaria, ufficio contabilità

**Personale correlato all'ente**:
Ogni persona che riceve dall'ente un compenso soggetto ad adempimenti da sostituto d'imposta o previdenziali, o che presta all'ente un'attività che genera adempimenti anche senza compenso: comparto, dirigenza, segretario, amministratori, co.co.co., LSU/LPU.
_Avoid_: Dipendente (quando si intende l'insieme intero)

**Persona**:
Individuo del personale correlato all'ente; soggetto dei fatti che non dipendono dal titolo di compenso (codice fiscale, nascita, genere, titolo di studio). Ha uno o più rapporti.
_Avoid_: Anagrafica, dipendente

**Scheda della persona**:
Vista di tutti i fatti di una persona e dei suoi rapporti, vigenti a una data e noti a un'altra; serve paga, gestione giuridica e adempimenti. Non è fonte di verità: una correzione è un nuovo fatto.
_Avoid_: Anagrafica, anagrafica dipendente

### Integrazione

**Fatto giuridico**:
Fatto su persona o rapporto che nasce da un atto dell'ente o da un evento della persona (assunzione, inquadramento, orario, ufficio, cessazione) e che l'Ufficio personale registra nel registro. Il registro è la sua unica forma strutturata: non c'è un secondo sistema giuridico con una verità propria.
_Avoid_: Dato anagrafico, variazione giuridica

**Fatto in attesa d'atto**:
Fatto che nasce da un atto dell'ente non ancora adottato: ha decorrenza e valori ma non il riferimento `ente:`. Si calcola come simulazione e alimenta il prospetto allegato all'atto. Non entra in un esito né in una proposta finché l'atto non gli dà numero e data. Non vale per gli atti esterni (pignoramenti, cessioni, notifiche), che si trascrivono.
_Avoid_: Bozza, fatto provvisorio

**Tipo di fatto**:
Categoria di fatto ammessa nel registro perché almeno un lettore dichiarato (regola, output obbligatorio, adempimento non stipendiale) la legge. Un nuovo lettore porta un nuovo tipo; un fatto che nessuno legge non entra (per esempio il catalogo dei corsi di formazione).
_Avoid_: Campo anagrafico

**Canale di input**:
Via da cui arriva un fatto già strutturato altrove (presenze, attestati di malattia, 730-4); il fatto registrato ne conserva la provenienza. Un canale non è fonte di verità concorrente del registro.
_Avoid_: Interfaccia, import

**Proposta di movimento contabile**:
Impegno, liquidazione o accertamento generati dal modello paghe e soggetti a conferma della Ragioneria. La liquidazione consuma l'impegno; l'impegno si propone solo quando l'obbligazione nasce da un fatto del registro (fondo, integrativo, arretrati da rinnovo) e non è già coperta dall'impegno automatico del bilancio; l'accertamento si propone per un credito che nasce da un fatto del registro, come il riparto di una convenzione. Mandato e reversale non si propongono: sono atti della Ragioneria.
_Avoid_: Export contabile, flusso contabile, proposta di mandato

**Fatto contabile**:
Fatto comunicato dalla Ragioneria attraverso un canale di input, come un impegno sulla spesa di personale (numero, esercizio, classificazione, atto presupposto, importo). Il modello lo legge e non lo produce.
_Avoid_: Impegno del modello, anagrafica capitoli

**Abbinamento**:
Scelta, fatta da una regola dichiarata, dell'impegno che un importo consuma (classificazione, esercizio di esigibilità, atto). Se nessun impegno è capiente scatta un fermo; se l'impegno non è noto, nella proposta è un dato mancante. La Ragioneria può cambiarlo in conferma. Per un importo finanziato dal fondo, la regola cerca l'impegno che ha come atto presupposto la sottoscrizione del contratto integrativo del fondo dell'anno di competenza, con la classificazione dell'istituto e l'esercizio della data di pagamento prevista.
_Avoid_: Imputazione automatica

**Versione di proposta**:
Istantanea immutabile delle righe di una proposta al momento dell'invio. Se dopo l'invio cambia un fatto che ne muove gli importi, la versione diventa superata e il modello ne emette una nuova. Stati: inviata, confermata, respinta (con motivo), superata.
_Avoid_: Bozza contabile, proposta aggiornata

**Conferma**:
Atto della Ragioneria su una versione di proposta: la accetta, cambiando al più l'abbinamento all'impegno con traccia, oppure la respinge con un motivo. Non corregge mai un importo: l'importo si corregge solo con un fatto.
_Avoid_: Validazione, approvazione contabile

**Evento di ritorno**:
Fatto contabile che riporta al modello ciò che è accaduto a una versione di proposta dopo l'invio (conferma o rifiuto, impegno e liquidazione numerati, mandato emesso o annullato, pagamento eseguito con valuta).
_Avoid_: Esito contabile (l'esito è del modello paghe), ritorno dati

**Assenza**:
Fatto giornaliero o orario su un rapporto, con una causale di assenza e l'atto o il documento di origine (attestato INPS, domanda, autorizzazione). Un solo fatto produce più effetti, ciascuno letto da un lettore diverso: riduzione stipendiale, comporto, adempimenti.
_Avoid_: Giustificativo, riepilogo presenze

**Causale di assenza**:
Elenco del modello, non del fornitore delle presenze, in cui ogni causale ha lettori dichiarati. L'adattatore delle presenze traduce le causali del fornitore in queste.
_Avoid_: Codice giustificativo

**Contratto neutro**:
Definizione, indipendente dal fornitore della contabilità, dei messaggi scambiati con la Ragioneria: versioni di proposta in uscita, fatti contabili ed eventi di ritorno in ingresso. Usa le classificazioni ufficiali e il vocabolario OPI; non legge né emette ordinativi. È uno schema versionato e indifferente al trasporto; ogni messaggio ha un identificativo stabile, e un evento ricevuto due volte non produce due fatti.
_Avoid_: Tracciato, API del fornitore

**Adattatore**:
Componente dell'ente che traduce il contratto neutro verso una sorgente concreta (contabilità, Giornale di cassa SIOPE+, inserimento manuale). La provenienza di ogni fatto nomina l'adattatore che l'ha portato.
_Avoid_: Connettore, integrazione

**Riga di proposta**:
Parte di una proposta per una classificazione ufficiale (missione, programma, piano dei conti di V livello) e un impegno, con l'elenco degli importi che la sommano. Non porta il capitolo.
_Avoid_: Riga per dipendente, dettaglio contabile

**Mappatura contabile dell'ente**:
Corrispondenza datata tra classificazione ufficiale e capitolo/articolo del bilancio dell'ente, tenuta dalla Ragioneria e applicata fuori dal modello paghe.
_Avoid_: Tabella capitoli, piano dei conti dell'ente

**Composizione del pagamento**:
Dati allegati alla liquidazione che dicono come pagarla: beneficiari e netti, ritenute collegate al mandato, versamenti a terzi. La Ragioneria ne ricava mandati e reversali senza ricostruire il legame netto–ritenute.
_Avoid_: Distinta, tracciato mandati

**Output obbligatorio**:
Prodotto richiesto da norma verso un ente esterno o un soggetto (UniEmens/ListaPosPA, F24EP, CU, 770, Conto Annuale, PASSWEB, conguagli, esiti 730-4).
_Avoid_: Stampa, report

### Calcolo

**Rapporto**:
Legame tra una persona e l'ente per un titolo di compenso; una persona può averne più di uno. È un solo concetto per ogni titolo. Le aggregazioni per persona (CU) sono viste; una regola può leggere un cumulo per persona (conguaglio, massimale) purché resti tracciato.
_Avoid_: Dipendente, matricola, posizione

**Titolo di compenso**:
Ragione giuridica di un rapporto (lavoro dipendente, mandato di amministratore, co.co.co., LSU/LPU, incarico), fissata alla sua nascita. Non cambia: un titolo diverso è un rapporto nuovo, non una variazione.
_Avoid_: Tipo dipendente, categoria

**Regime del titolo**:
Insieme delle dichiarazioni del corpus per un titolo di compenso: istituti, basi imponibili, concorsi, regole, fermi e output obbligatori alimentati. Sta nel corpus e non nel registro; se per un titolo manca, il calcolo si ferma.
_Avoid_: Modulo amministratori, gestione a parte

**Piano di rate**:
Input da atto del contratto di collaborazione: compenso totale, durata, date e importi delle rate. Ogni rata produce un importo che matura come evento, senza divisore né frazioni. Se la collaborazione cambia, cambia il piano con un altro atto.
_Avoid_: Compenso mensile, stipendio del collaboratore

**Attestazione della prestazione**:
Fatto sul rapporto, dal responsabile, che dichiara eseguita la prestazione di una rata. Senza attestazione l'importo resta calcolato ma non entra in una versione di proposta.
_Avoid_: Visto, nulla osta

**Convenzione di segreteria**:
Input da atto sul rapporto del segretario nell'ente capofila: enti partecipanti, capofila, ente che paga, quote e decorrenza. Il rapporto di titolarità è uno solo, nel capofila, che di norma paga, versa e dichiara. Un ente non capofila conosce la convenzione come fatto sull'ente, che alimenta il Conto Annuale; ha un rapporto solo se paga direttamente una quota, con un incarico da convenzione. Il pagamento diretto dell'intera retribuzione fissa da un non capofila ferma il calcolo e nomina il caso.
_Avoid_: Segretario condiviso, rapporto in quota

**Riparto della convenzione**:
Vista che applica le quote della convenzione di segreteria agli esiti pagati e versati di un periodo, con la periodicità dichiarata dalla convenzione. Inviato agli altri enti è un esito dichiarato. Nel capofila genera una proposta di accertamento; nell'ente non capofila è un atto esterno che si trascrive e genera una proposta di liquidazione verso il capofila.
_Avoid_: Rimborso (senza dire di chi), compensazione

**Utilizzazione LSU/LPU**:
Rapporto con titolo LSU/LPU, che non è lavoro subordinato e può non generare alcun importo. L'assegno pagato da altri non è un importo dell'ente: lo diventa solo se un fatto da atto dichiara l'ente come pagatore. Le presenze alimentano integrazione, uomo-anno e certificazione a INPS.
_Avoid_: Dipendente LSU, rapporto di lavoro socialmente utile

**Incarico del segretario**:
Rapporto con titolo incarico in un ente diverso da quello di titolarità, che paga solo ciò che eroga direttamente. Non è lavoro dipendente con quell'ente e non ha organico. Un fatto ne dice l'origine: scavalco, cioè reggenza o supplenza disposta dal Ministero, con la durata del provvedimento; oppure convenzione, per la quota che un ente non capofila paga direttamente. La base viene dal rapporto di titolarità, che quell'ente non conosce: è un input da atto esterno; la percentuale la applica una regola. Il regime si fonda su una nota di prassi.
_Avoid_: Scavalco come variazione del rapporto di titolarità, rimborso di scavalco, rapporto in quota

**Quota riconosciuta da altri enti**:
Input da atto, o atto esterno trascritto, in importo o percentuale, che riduce quanto il capofila paga al segretario in convenzione, con l'importo pieno visibile. Il riparto non la comprende. Se la somma delle quote supera il dovuto il calcolo si ferma.
_Avoid_: Detrazione, conguaglio tra enti

**Mandato di amministratore**:
Rapporto di un amministratore locale, dalla proclamazione o nomina alla cessazione. Una rielezione è un rapporto nuovo; un cambio di carica no. Delimita la durata su cui si calcola l'indennità di fine mandato, dove la norma la prevede.
_Avoid_: Mandato (senza dire quale: il mandato di pagamento è un atto della Ragioneria), carica (quando si intende il rapporto)

**Carica**:
Fatto categoriale datato su un mandato di amministratore (sindaco, vicesindaco, assessore, presidente del consiglio, consigliere). Se cambia apre una frazione e chiede una nuova misura da atto.
_Avoid_: Ruolo, qualifica (che è del lavoro dipendente)

**Misura dell'indennità di funzione**:
Input da atto che fissa, per carica e decorrenza, l'importo mensile pieno dell'indennità di un amministratore, con il suo importo atteso. Rinuncia o riduzione volontaria sono altri input da atto. Il dimezzamento non vi rientra: lo applica una regola sulla condizione lavorativa dell'amministratore.
_Avoid_: Indennità tabellare, indennità calcolata

**Condizione lavorativa dell'amministratore**:
Fatto datato sul mandato di amministratore che dice se l'amministratore è lavoratore dipendente, e se è in aspettativa. Può cambiare durante il mandato senza un nuovo atto dell'ente, e apre una frazione.
_Avoid_: Flag aspettativa

**Posizione previdenziale dell'amministratore**:
Fatto datato sul mandato di amministratore che nomina la gestione o cassa a cui la persona è iscritta. Con carica, popolazione dell'ente e condizione lavorativa decide se spetta un onere dell'art. 86 e verso chi.
_Avoid_: Cassa di appartenenza (senza data)

**Onere dell'art. 86**:
Istituto a carico dell'ente per un amministratore, separato dall'indennità, che resta esclusa da ogni base previdenziale. La quota forfettaria viene da una regola su minimale e aliquota; gli oneri in aspettativa e i rimborsi al datore vengono da un atto esterno trascritto.
_Avoid_: Contributi sull'indennità, ritenuta previdenziale dell'amministratore

**Presenza in seduta**:
Fatto sul rapporto per ogni seduta di un organo a cui l'amministratore partecipa, con data, organo e verbale o foglio presenze come fonte. Matura il gettone di presenza, il cui valore è un input da atto con importo atteso.
_Avoid_: Numero sedute, conteggio gettoni

**Tetto del gettone**:
Limite di legge ai gettoni di un consigliere, applicato da una regola: l'eccedenza non si paga e resta visibile nella derivazione.
_Avoid_: Capienza dei gettoni

**Istituto**:
Elemento retributivo o trattenuta definito da norma o contratto, con riferimento; i codici esterni (SICO, UniEmens, codice tributo, piano dei conti) sono mappature datate dell'istituto.
_Avoid_: Voce, codice voce

**Fatto**:
Evento su una persona, su un rapporto o su un fondo risorse decentrate, registrato in modo immutabile e bitemporale (validità e registrazione), con atto fonte quando esiste; si corregge solo con un nuovo fatto. Il valore è un numero o, per contratto, qualifica e simili, un codice che una formula non legge.
_Avoid_: Movimento, variazione anagrafica

**Importo**:
Unità del modello: valore riferito a rapporto, istituto e periodo di competenza, con eventuale data di pagamento e derivazione (regola, parametri, fatti). Entra in una base imponibile solo con la data di pagamento. Ricalcolabile finché non entra in un esito. Può derivare da altri importi (es. imponibili), senza cicli.
_Avoid_: Voce, riga di cedolino

**Frazione**:
Parte del mese in cui fatti, regole e parametri sono uniformi; ogni frazione produce il proprio importo. Il totale del mese è una vista.
_Avoid_: Rateo (quando si intende la parte di mese)

**Maturazione**:
Modo, dichiarato dalla regola, in cui un istituto matura: a giorni, a evento, sul periodo dichiarato o annuale.
_Avoid_: Tipo voce

**Periodo dichiarato**:
Intervallo esposto verso INPS, su cui si calcolano e si arrotondano i contributi; si apre per i cambi che INPS distingue, non per ogni frazione. Comprende gli importi pagati nel mese, a prescindere dalla loro competenza.
_Avoid_: Quadro (quando si intende l'intervallo)

**Periodo giuridico**:
Periodo dichiarato senza imponibili che dichiara il servizio di un mese pagato in un altro: per il principio di cassa gli importi stanno nel mese di pagamento.
_Avoid_: Periodo vuoto, mese a zero

**Data di pagamento**:
Giorno in cui la somma esce dalla disponibilità dell'ente per entrare nel patrimonio del dipendente, cioè la valuta dell'accredito, registrato come fatto legato all'esito pagato e letto dall'evento di ritorno del pagamento eseguito. Decide in quale denuncia entrano gli importi di quell'esito.
_Avoid_: Data di liquidazione (la liquidazione è una fase contabile), valuta prevista

**Valuta prevista**:
Data di pagamento ipotizzata dalla versione di proposta, usata solo per calcolare ritenute e netti della composizione del pagamento. Se la valuta effettiva è diversa, la differenza si regola sull'esito.
_Avoid_: Data di pagamento (finché il pagamento non è eseguito)

**Base imponibile**:
Insieme degli importi pagati su cui si calcola una contribuzione (CPDEL, Fondo Credito, TFS, TFR). Una base non deriva da un'altra, salvo che una norma lo dica.
_Avoid_: Imponibile (senza dire quale)

**Categoria di reddito**:
Elenco del modello, senza articoli nel nome (lavoro dipendente, carica elettiva, collaborazione, lavori socialmente utili), letto da regole di ritenuta, CU e 770. Ogni istituto la dichiara con date e riferimento, scelti in base all'anno d'imposta a cui il pagamento è attribuito, quindi con la cassa allargata dove vale: quando una norma è abrogata cambia il riferimento, non la categoria. Se manca, il calcolo si ferma.
_Avoid_: Redditi assimilati (senza dire quali), articolo 50

**Concorso**:
Dichiarazione, con date e riferimento, di come un istituto entra in una base: intero, parziale o escluso. Vale la dichiarazione vigente alla data di pagamento; se è assente o parziale il calcolo si ferma.
_Avoid_: Flag imponibile

**Regola di cassa**:
Regola che legge una base o un'altra regola di cassa. Si sceglie alla data di pagamento, con i parametri vigenti in quel giorno, e produce importi solo nella denuncia. Con `applica_se` vale solo per un codice, letto sul periodo o, fuori servizio, sull'ultimo giorno di servizio.
_Avoid_: Contributo per competenza

**Regola sul mese**:
Regola di cassa che legge il totale del mese delle basi, non il singolo periodo dichiarato, e si espone sull'ultimo periodo, come il contributo dell'1%.
_Avoid_: Contributo mensile (quando si intende un contributo per periodo)

**Recupero**:
Importo negativo pagato che entra in una base. Modellati i casi in servizio, detratto dal periodo, e su cessato, in un periodo fuori servizio; gli altri fermano il calcolo.
_Avoid_: Trattenuta (la trattenuta è un istituto)

**Fermo**:
Dichiarazione del corpus: se un fatto è presente nel mese, il calcolo o la denuncia si ferma e nomina il caso non modellato. Con un codice, scatta solo per quel valore del fatto.
_Avoid_: Blocco, errore generico

**Regime di fine servizio**:
Codice INPS del rapporto: 1 TFR, 2 optante, 3 TFS. Sceglie la contribuzione di fine servizio. TFS e TFR di un Comune stanno entrambi nella gestione ex INADEL.
_Avoid_: Tipo liquidazione

**Riduzione TFR**:
Riduzione del lordo di chi è in regime TFR, pari al 2,50% soppresso sull'80% delle voci utili al TFS. Non entra in nessuna base: le basi restano sul lordo intero, che è l'incremento figurativo del DPCM.
_Avoid_: Trattenuta 2,50% (il contributo è soppresso, non trattenuto)

**Ulteriori elementi TFR**:
Voci utili al TFR ma non al TFS, come la retribuzione di posizione: base propria al 100%, contributo al 6,91%.
_Avoid_: Voci solo TFR

**Caso**:
Situazione reale modellata con i suoi fatti, la sua regola, il riferimento e un esempio verificato. Finché un caso non è modellato, il calcolo si ferma e lo nomina.
_Avoid_: Eccezione, formula generica

**Nota di prassi**:
Documento scritto nel repo che motiva una regola priva di fonte ufficiale puntuale; chi la legge sa che è prassi, e la spiegazione dell'importo lo segnala.
_Avoid_: Regola di casa

**Esito**:
Istantanea immutabile di ciò che è stato pagato, dichiarato o versato verso terzi; base del confronto per ogni differenza successiva. L'esito pagato nasce dall'evento di ritorno del pagamento eseguito, con le righe della versione di proposta confermata, non dalla conferma; l'esito versato nasce allo stesso modo dall'evento di versamento eseguito, che sia mandato F24EP o regolarizzazione di un provvisorio. Anche ciò che si invia per gli adempimenti non stipendiali (Tab. 15 e SICI, relazione tecnico-finanziaria, invio al MEF, trasparenza) è un esito dichiarato; se poi un fatto cambia la vista, il modello segnala la differenza con l'ultimo esito.
_Avoid_: Elaborazione chiusa, storico cedolini

**Vista**:
Aggregazione di importi in una forma richiesta (cedolino, ListaPosPA, F24EP, proposta di movimento contabile); non è fonte di verità.
_Avoid_: Stampa, tabulato

**Controllo di completezza degli output**:
Verifica che ogni importo pagato sia compreso in ogni output obbligatorio dichiarato dal suo regime, o ne sia escluso da una dichiarazione esplicita. Un'assenza non dichiarata ferma l'invio di quell'output, non il calcolo.
_Avoid_: Quadratura, controllo finale

**Quadro**:
Elemento della ListaPosPA che dichiara un periodo: E0 per il mese corrente, V1 con una causale per un periodo precedente. Lo produce la vista dalla denuncia, mai il calcolo.
_Avoid_: Periodo dichiarato (che è l'intervallo, non l'elemento del tracciato)

**Quadro fermo**:
Quadro necessario che la vista non produce, perché il caso non è nella fetta, come il V1 causale 7. Nomina il quadro e conserva gli importi calcolati.
_Avoid_: Errore di esportazione

**Dato mancante**:
Dato obbligatorio del tracciato che il registro non ha, come il regime di fine servizio o il codice di cessazione: la vista lo chiede, non lo stima.
_Avoid_: Default, valore di comodo

**Bozza non trasmissibile**:
Vista completa nei dati, ma con un caso dichiarato dal corpus come non modellato, come lo erano TFS e TFR fino al ticket #33. Si serializza solo se richiesto, con l'avvertenza in testa.
_Avoid_: Anteprima, test

**Regola**:
Logica di calcolo generale, versionata, con riferimento normativo obbligatorio.
_Avoid_: Formula, voce calcolata

**Parametro**:
Valore numerico o tabellare con periodo di vigenza e fonte puntuale (norma, circolare, CCNL, delibera).
_Avoid_: Costante, tabella di sistema

**Input da atto**:
Decisione discrezionale dell'ente (contratto integrativo, costituzione del fondo, determina, valutazione) registrata come fatto con atto fonte e decorrenza; mai codificata come regola.
_Avoid_: Parametro locale, personalizzazione

### Fondo

**Fondo risorse decentrate**:
Identità a cui si riferiscono i fatti da atto che costituiscono e destinano le risorse per il trattamento accessorio: ente, anno di costituzione e ambito (per esempio comparto, dirigenza, EQ o segretario). Le risorse dell'EQ e quelle di posizione, galleggiamento e risultato del segretario, pagate dal bilancio e senza contratto integrativo, sono fondi con il proprio ambito, così il limite del trattamento accessorio le somma come le altre e la Tab. 15 le vede. Il fondo con ambito segretario sta nell'ente capofila, se c'è una convenzione. Non ha saldo né stato proprio: capienza, utilizzo e residui sono viste che incrociano quei fatti con gli importi degli istituti accessori.
_Avoid_: Fondo (senza anno), modulo fondo, salario accessorio (che è l'insieme degli importi pagati)

**Voce di costituzione**:
Input da atto che porta a un fondo un importo di un tipo di voce, con l'atto che lo dispone. Ogni voce ha il proprio atto, così le integrazioni successive restano distinte; senza numero e data d'atto è un fatto in attesa d'atto.
_Avoid_: Risorsa, riga del fondo

**Tipo di voce**:
Elemento del catalogo del corpus, datato per anno del fondo, che dice che cos'è una voce di costituzione: riferimento, natura (stabile, variabile, decurtazione), inclusione nel limite del trattamento accessorio con il suo riferimento, codice della Tab. 15 come mappatura datata e, dove la norma lo consente, la regola dell'importo atteso. Un tipo generico per le risorse di legge non elencate lascia all'ente la dichiarazione dell'inclusione, con riferimento; se manca, si ferma solo la vista del limite.
_Avoid_: Codice risorsa, voce Tab. 15

**Importo atteso**:
Importo che una regola ricava da parametri e fatti per un valore che l'ente fissa con un atto, come una voce di costituzione (un importo pro capite per la consistenza a una data) o la misura dell'indennità di funzione. Non sostituisce il valore dell'atto: il modello segnala la differenza.
_Avoid_: Importo calcolato del fondo, importo teorico

**Certificazione del fondo**:
Fatto sul fondo, con il verbale dell'organo di revisione come atto, che copre la costituzione nota alla data in cui è registrato. Una voce registrata o corretta dopo non è coperta, e le viste che dipendono dalla certificazione lo segnalano.
_Avoid_: Fondo certificato (come stato), visto dei revisori

**Destinazione**:
Input da atto, tratto dal contratto integrativo, che assegna una parte di un fondo a un istituto. È a importo oppure a residuo, cioè prende ciò che avanza dalle altre; un fondo ne ha al più una a residuo.
_Avoid_: Ripartizione, utilizzo (l'utilizzo è la vista degli importi che consumano la destinazione)

**Sottoscrizione del contratto integrativo**:
Fatto sul fondo, con il suo atto, da cui nasce l'obbligazione per le destinazioni. Alla sua registrazione il modello propone un impegno per ogni destinazione ed esercizio di esigibilità, salvo che la fonte sia già coperta dall'impegno automatico del bilancio. Prima della sottoscrizione le destinazioni valgono per la capienza ma non generano proposte.
_Avoid_: Accordo, firma (senza dire quale)

**Esigibilità attesa**:
Esercizio in cui la destinazione dichiara che i suoi importi saranno pagati: l'anno di costituzione per le indennità mensili, l'anno successivo per performance e premi legati alla valutazione. La parte esigibile dopo l'anno di costituzione esce nella proposta come coperta da fondo pluriennale vincolato.
_Avoid_: Scadenza, anno di pagamento (che è dell'importo)

**Vincolo di utilizzo**:
Dichiarazione del corpus su come le destinazioni di un fondo devono ripartirsi, per esempio una quota minima della parte variabile alla performance. Come il catalogo dei tipi di voce, si sceglie per anno del fondo. Il prospetto del contratto integrativo in attesa d'atto segnala la violazione; alla sottoscrizione le proposte di impegno si fermano e nominano il vincolo.
_Avoid_: Regola di ripartizione, percentuale del fondo

**Fonte di finanziamento**:
Dichiarazione dell'istituto, con date e riferimento, di che cosa lo paga: una destinazione del fondo del suo ambito, il bilancio o un'altra provvista dichiarata. Può essere parziale. Se manca, il calcolo si ferma. Un importo consuma il fondo del suo anno di competenza, non dell'anno di pagamento.
_Avoid_: Capitolo dell'istituto, tabella di ripartizione

**Utilizzo**:
Vista che somma sulla destinazione gli importi degli istituti che vi si finanziano, per anno di competenza: la performance di un anno pagata l'anno dopo è utilizzo del fondo del suo anno. La spesa per cassa (Tab. 13) è un'altra vista sugli esiti pagati.
_Avoid_: Speso, consuntivo del fondo

**Limite del trattamento accessorio**:
Fatto sull'ente per anno, fatto di componenti con atto e tipo (importo 2016 certificato, adeguamento al valore medio pro capite 2018, altre componenti di legge), ciascuna con l'importo atteso dove esiste una regola. La vista del limite lo confronta con la somma delle voci incluse di tutti i fondi dell'ente nell'anno. Se è superato, il prospetto dell'atto di costituzione lo segnala e le proposte di impegno nate dalla sottoscrizione dei fondi coinvolti si fermano; le liquidazioni su impegni già confermati proseguono.
_Avoid_: Tetto 2016 (che è solo una componente), tetto del fondo

**Chiusura del fondo**:
Vista sul fondo di un anno a una data di riferimento e a un tempo di registrazione: utilizzato, destinato ed esigibile dopo l'anno (fondo pluriennale vincolato), economie, e risorse vincolate se il contratto integrativo non è sottoscritto entro l'anno, distinguendo il fondo certificato da quello che non lo è.
_Avoid_: Consuntivo, saldo di fine anno

**Riporto**:
Voce di costituzione, con il proprio atto, che porta a un fondo risorse non utilizzate di un fondo precedente e cita la chiusura da cui deriva con la data alla quale era nota. Se poi la chiusura cambia, il modello segnala la differenza e non modifica il riporto: rimedia l'ente con un fatto.
_Avoid_: Residuo (senza dire di quale fondo), avanzo del fondo

**Capienza**:
Confronto tra l'utilizzo (esiti pagati più importi calcolati non ancora pagati) e la destinazione con atto, e tra la somma degli utilizzi e la costituzione coperta dalla certificazione. Una voce in attesa d'atto non apre capienza. Se la capienza è superata gli importi restano calcolati e visibili, ma nessuna versione di proposta li comprende; il fermo nomina fondo, destinazione, eccedenza e istituti. Che cosa ridurre lo decide l'ente con un fatto.
_Avoid_: Disponibilità, saldo del fondo

### Metodo

**Tool esistente**:
Applicazione già sviluppata dall'utente, usata come fonte di regole e conoscenza normativa deterministica e, dove utile, come generatore di output; non è un riferimento strutturale.
_Avoid_: Modulo, componente legacy

**Struttura di riferimento**:
Schema sigillato dell'utente, scritto prima della mappa, usato solo come controllo di completezza nel confronto finale.
_Avoid_: Modello di riferimento, architettura target
