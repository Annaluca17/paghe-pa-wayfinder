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

**Origine dell'impegno**:
Dichiarazione dell'istituto, con date e riferimento, accanto alla sua classificazione ufficiale: automatico col bilancio, oppure l'atto che fa nascere l'obbligazione. Il modello propone l'impegno quando quell'atto è registrato, salvo l'automatico. Se manca, la versione di proposta non si emette.
_Avoid_: Tipo impegno, flag automatico

**Fatto contabile**:
Fatto comunicato dalla Ragioneria attraverso un canale di input, come un impegno sulla spesa di personale (numero, esercizio, classificazione, atto presupposto, disponibilità a una data). Il modello lo legge e non lo produce.
_Avoid_: Impegno del modello, anagrafica capitoli

**Abbinamento**:
Scelta, fatta da una regola dichiarata, dell'impegno che una riga di proposta consuma: stessa classificazione, atto presupposto richiesto dall'origine dell'impegno, esercizio della valuta prevista e, per un'origine da atto, i residui dal più vecchio; nello stesso esercizio il numero più basso. La riga va intera su un solo impegno. Se nessun impegno adatto è capiente scatta un fermo dei rapporti della riga; se l'impegno non è noto, nella proposta è un dato mancante. La Ragioneria può cambiarlo in conferma con un impegno noto della stessa classificazione. Per un importo finanziato dal fondo, la regola cerca l'impegno che ha come atto presupposto la sottoscrizione del contratto integrativo del fondo dell'anno di competenza, con la classificazione dell'istituto e l'esercizio della data di pagamento prevista.
_Avoid_: Imputazione automatica

**Versione di proposta**:
Istantanea immutabile delle righe di una proposta al momento dell'invio. Se dopo l'invio cambia un fatto che ne muove gli importi, la versione diventa superata e il modello ne emette una nuova. Stati: inviata, confermata, respinta (con motivo), superata.
_Avoid_: Bozza contabile, proposta aggiornata

**Conferma**:
Atto della Ragioneria su una versione di proposta: la accetta, cambiando al più l'abbinamento all'impegno con traccia, oppure la respinge con un motivo. Non corregge mai un importo: l'importo si corregge solo con un fatto.
_Avoid_: Validazione, approvazione contabile

**Evento di ritorno**:
Fatto contabile che riporta al modello ciò che è accaduto a una versione di proposta dopo l'invio (conferma o rifiuto, impegno e liquidazione numerati, mandato emesso o annullato, pagamento eseguito con valuta e rapporti pagati). Un identificativo ripetuto con lo stesso contenuto non ha effetto; con un contenuto diverso viene rifiutato.
_Avoid_: Esito contabile (l'esito è del modello paghe), ritorno dati

**Ricevuta della delega**:
Evento che riporta una delle fasi dopo la trasmissione di una delega F24EP: controlli formali, controllo dei crediti, addebito. Lo stato della delega (trasmessa, accettata, sospesa, addebitata, scartata) è una vista delle ricevute. Una ricevuta negativa rende la delega scartata e gli importi tornano da versare.
_Avoid_: Ricevuta AdE (senza dire quale), esito della delega

**Evento di versamento eseguito**:
Evento che dice che le righe di una liquidazione verso terzi sono state versate e in che data, dall'addebito della delega o dal bonifico al terzo. Da esso nasce l'esito versato, una sola volta. La regolarizzazione del provvisorio lo sostituisce solo se è l'unica notizia disponibile.
_Avoid_: Quietanza, regolarizzazione (che è un evento contabile successivo)

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
Parte di una proposta per una classificazione ufficiale (missione, programma, piano dei conti di V livello) e un impegno, con l'elenco degli importi che la sommano. Comprende solo la spesa: retribuzione, contributi a carico dell'ente, IRAP. Le ritenute restano nella composizione del pagamento. Non porta il capitolo.
_Avoid_: Riga per dipendente, dettaglio contabile

**Disponibilità dell'impegno**:
Quanto resta di un impegno a una data, secondo la Ragioneria, portato dal fatto contabile. Il modello ne sottrae le righe delle proprie versioni vive registrate dopo quella data; una disponibilità nuova è un fatto nuovo.
_Avoid_: Saldo dell'impegno, residuo (che è un impegno di un esercizio precedente)

**Programma del rapporto**:
Fatto datato del rapporto, scritto dall'ente: missione e programma dove la persona lavora, ai quali si imputa la sua spesa. Se manca, nella proposta è un dato mancante.
_Avoid_: Centro di costo, ufficio

**Mappatura contabile dell'ente**:
Corrispondenza datata tra classificazione ufficiale e capitolo/articolo del bilancio dell'ente, tenuta dalla Ragioneria e applicata fuori dal modello paghe.
_Avoid_: Tabella capitoli, piano dei conti dell'ente

**Pagamento**:
Ciò che una versione di proposta confermata fa eseguire: una sola valuta prevista e più rapporti. Non coincide con il mese: stipendio, tredicesima e arretrati possono essere pagamenti diversi.
_Avoid_: Elaborazione, cedolino, mensilità

**Composizione del pagamento**:
Dati allegati alla liquidazione che dicono come pagarla: beneficiari e netti, ritenute collegate al mandato, versamenti a terzi. È un elenco di righe di composizione, una struttura sola per Ragioneria, ritenute, trattenute a terzi e delega. La Ragioneria ne ricava mandati e reversali senza ricostruire il legame netto–ritenute.
_Avoid_: Distinta, tracciato mandati

**Riga di composizione**:
Parte della composizione del pagamento collegata a un importo, mai con un valore riscritto, con natura, effetto sul netto, destinatario e canale.
_Avoid_: Riga di cedolino, voce

**Dichiarazione di composizione**:
Dichiarazione datata dell'istituto, con riferimento: natura, effetto sul netto, destinatario e canale, oppure che l'istituto è solo intermedio e non entra nella composizione. Se manca, la proposta si ferma, non il calcolo.
_Avoid_: Tipo voce, segno della voce

**Netto**:
Somma delle righe di composizione di un rapporto in un pagamento che hanno effetto sul netto. Se è negativo si ferma quel rapporto, non gli altri. Il netto per persona è una vista.
_Avoid_: Netto in busta, netto a pagare (senza dire di quale pagamento)

**Ultimo pagamento dell'anno**:
Fatto sull'ente, uno per anno d'imposta, con la data prevista. La proposta con valuta prevista uguale o successiva, nello stesso anno d'imposta, porta il conguaglio fiscale delle persone che contiene.
_Avoid_: Mese di conguaglio, flag di conguaglio

**Output obbligatorio**:
Prodotto richiesto da norma verso un ente esterno o un soggetto (UniEmens/ListaPosPA, lista collaboratori, F24EP, CU, 770, Conto Annuale, PASSWEB, PIAO, trasparenza, conguagli, esiti 730-4, autoliquidazione INAIL). È sempre una vista del modello, mai il prodotto di un tool esistente.
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
Fatto sul rapporto, dal responsabile, che dichiara eseguita la prestazione di una rata. Senza attestazione l'importo resta calcolato ma non entra in una versione di proposta: il corpus la dichiara come condizione di proposta dell'istituto.
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

**Fascia del segretario**:
Fatto categoriale datato (A, B, C) sul rapporto del segretario, da atto: sceglie il tabellare annuo dell'art. 35 CCNL 23/02/2026 e cambia con l'inquadramento. Se cambia a metà mese apre una frazione. Senza fatto il calcolo si ferma e nomina il caso: nessuna fascia di default.
_Avoid_: Classe dell'ente (che decide il campo della posizione, non il tabellare), qualifica

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
Fatto datato sul mandato di amministratore che nomina la gestione o cassa a cui la persona è iscritta. Con carica, popolazione dell'ente e condizione lavorativa decide se spetta un onere dell'art. 86 e verso chi. Vale anche per il collaboratore, dove sceglie l'aliquota della gestione separata: `gestione_separata` (nessuna altra cassa, non pensionato), `pensionato`, `altra_cassa`.
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

**Mappatura esterna**:
Corrispondenza datata, nel corpus e con riferimento, tra un istituto e un codice di un sistema esterno (codice tributo, causale, SICO, punto CU). Più istituti possono avere lo stesso codice; se un istituto dovrebbe avere due codici, sono due istituti. Se manca, si ferma l'invio dell'output, non il calcolo. Eccezione: la causale F24EP della gestione separata (C10 o CXX) si sceglie per la posizione previdenziale del rapporto, con una mappatura di fatto (ticket #104); il riferimento A di quelle causali è mese e anno di pagamento (`MMAAAA`), non la competenza.
_Avoid_: Tabella codici, codice dell'istituto

**Fatto**:
Evento su una persona, su un rapporto, su un fondo risorse decentrate o sull'ente, registrato in modo immutabile e bitemporale (validità e registrazione), con atto fonte quando esiste; si corregge solo con un nuovo fatto. Il valore è un numero o, per contratto, qualifica e simili, un codice che una formula non legge.
_Avoid_: Movimento, variazione anagrafica

**Importo**:
Unità del modello: valore riferito a rapporto, istituto e periodo di competenza, con eventuale data di pagamento e derivazione (regola, parametri, fatti). Entra in una base imponibile solo con la data di pagamento. Ricalcolabile finché non entra in un esito. Può derivare da altri importi (es. imponibili), senza cicli.
_Avoid_: Voce, riga di cedolino

**Frazione**:
Parte del mese in cui fatti, regole e parametri sono uniformi; ogni frazione produce il proprio importo. Il totale del mese è una vista.
_Avoid_: Rateo (quando si intende la parte di mese)

**Part-time**:
Fatto datato del rapporto, da atto di trasformazione, con percentuale e tipo (orizzontale, verticale, misto). Il calcolo è lo stesso per i tre tipi: importo pieno per percentuale, mensilizzato anche nel verticale e nel misto. Il tipo decide solo cosa si dichiara.
_Avoid_: Orario ridotto (senza dire quale tipo), coefficiente

**Trattamento nel part-time**:
Dichiarazione datata dell'istituto, con riferimento: proporzionale, intero, oppure da integrativo, cioè misura fissata dall'ente con un input da atto. Se manca, il calcolo di un rapporto in part-time si ferma.
_Avoid_: Flag di riproporzionamento

**Programmazione del part-time**:
Input da atto del rapporto che fissa per un periodo (mese, trimestre, anno) i giorni lavorativi e le ore di ciascuno. La denuncia dichiara la programmazione, non il lavorato; senza programmazione per il mese è un dato mancante e la ListaPosPA è una bozza non trasmissibile.
_Avoid_: Turni (quando si intende l'atto), presenze

**Maturazione**:
Modo, dichiarato dalla regola, in cui un istituto matura: a giorni, a evento, sul periodo dichiarato o annuale. L'annuale con una condizione a codice matura sui giorni di servizio dell'anno e vale se la condizione è vera nell'ultimo.
_Avoid_: Tipo voce

**Tredicesima**:
Importo annuale del comparto, un istituto per area: il tabellare mensile dell'area dell'ultimo giorno di servizio, per i giorni di servizio dell'anno diviso 365, pesati sulla percentuale di part-time (ADR 0038). `calcola_annuale` ne dà l'importo atteso a fine anno e, con una data, il maturato. L'Ufficio personale sceglie il pagamento in cui metterla.
_Avoid_: Rateo mensile, gratifica natalizia

**Periodo dichiarato**:
Intervallo esposto verso INPS, su cui si calcolano e si arrotondano i contributi; si apre per i cambi che INPS distingue, non per ogni frazione. Comprende gli importi pagati nel mese, a prescindere dalla loro competenza.
_Avoid_: Quadro (quando si intende l'intervallo)

**Periodo giuridico**:
Periodo dichiarato senza imponibili che dichiara il servizio di un mese pagato in un altro: per il principio di cassa gli importi stanno nel mese di pagamento.
_Avoid_: Periodo vuoto, mese a zero

**Data di pagamento**:
Giorno in cui la somma esce dalla disponibilità dell'ente per entrare nel patrimonio del dipendente, cioè la valuta dell'accredito, registrato come fatto legato all'esito pagato e letto dall'evento di ritorno del pagamento eseguito. Per un recupero è il giorno in cui la trattenuta è operata o l'incasso è avvenuto. Decide in quale denuncia entrano gli importi di quell'esito.
_Avoid_: Data di liquidazione (la liquidazione è una fase contabile), valuta prevista

**Pagamento fisiologico**:
Dichiarazione dell'istituto, con date e riferimento, che il suo pagamento oltre l'anno di competenza rientra nei tempi ordinari, come la performance. Non richiede una causa del pagamento tardivo.
_Avoid_: Arretrato fisiologico, ritardo normale

**Causa del pagamento tardivo**:
Fatto, con date e riferimento, che dice perché importi con competenza in un anno precedente sono pagati dopo: legge, contratto collettivo, sentenza, atto sopravvenuto o situazione di fatto. Un atto è sopravvenuto solo se attribuisce il diritto dopo il periodo. Una situazione di fatto, come un errore di calcolo dell'ente, porta anche la scelta dell'ente e la motivazione. Serve se l'importo non è attribuito all'anno di competenza e l'istituto non dichiara un pagamento fisiologico; se manca, il calcolo fiscale si ferma.
_Avoid_: Tipo arretrato, flag tassazione separata

**Regime di tassazione**:
Trattamento fiscale di un importo: ordinario, separato o sostitutivo. Il separato lo ricava una regola datata dalla causa del pagamento tardivo; il sostitutivo vale per gli istituti che dichiarano di rientrare in un'agevolazione, come la sostitutiva sull'accessorio. Si congela nell'esito pagato. Non è una categoria di reddito.
_Avoid_: Tassazione dell'istituto, categoria (quando si intende il trattamento)

**Sostitutiva sull'accessorio**:
Imposta del 15% che nel 2026 sostituisce IRPEF e addizionali sugli importi degli istituti accessori del personale non dirigenziale, fino a 800 euro per persona nell'anno e con reddito di lavoro dipendente fino a 50.000 euro (L. 199/2025 c. 237, ADR 0035). Si calcola nella ritenuta del pagamento e si ricalcola al conguaglio. L'importo così tassato esce dall'imponibile fiscale ordinario. Non si applica dopo la rinuncia della persona.
_Avoid_: Detassazione, flat tax sull'accessorio

**Rinuncia alla sostitutiva**:
Fatto della persona, con validità e documento di origine, con cui rinuncia per iscritto alla sostitutiva sull'accessorio. Vale per i pagamenti successivi alla sua data.
_Avoid_: Opzione per l'ordinaria

**Valuta prevista**:
Data di pagamento ipotizzata dalla versione di proposta, usata solo per calcolare ritenute, contributi e netti della composizione del pagamento. Se la valuta effettiva cade in un altro mese, la differenza si regola sul pagamento successivo; se cambia l'anno d'imposta, il calcolo fiscale della persona si ferma.
_Avoid_: Data di pagamento (finché il pagamento non è eseguito)

**Base imponibile**:
Insieme degli importi pagati su cui si calcola una contribuzione (CPDEL, Fondo Credito, TFS, TFR, gestione separata). Una base non deriva da un'altra, salvo che una norma lo dica. Una base può avere un massimale annuo, un parametro: la base di ogni mese è ciò che resta sotto il massimale, sommando i mesi dell'anno nello stesso ente (gestione separata, 122.295 euro nel 2026).
_Avoid_: Imponibile (senza dire quale)

**Categoria di reddito**:
Elenco del modello, senza articoli nel nome (lavoro dipendente, carica elettiva, collaborazione, lavori socialmente utili), letto da regole di ritenuta, CU e 770. Ogni istituto la dichiara con date e riferimento, scelti in base all'anno d'imposta a cui il pagamento è attribuito, quindi con la cassa allargata dove vale: quando una norma è abrogata cambia il riferimento, non la categoria. Se manca, la versione di proposta non si emette.
_Avoid_: Redditi assimilati (senza dire quali), articolo 50

**Concorso**:
Dichiarazione, con date e riferimento, di come un istituto entra in una base: intero, parziale o escluso. Vale la dichiarazione vigente alla data di pagamento; se è assente o parziale il calcolo si ferma.
_Avoid_: Flag imponibile

**Regola di cassa**:
Regola che legge una base o un'altra regola di cassa. Si sceglie alla data di pagamento, con i parametri vigenti in quel giorno, e produce importi solo nella denuncia. Con `applica_se` vale solo per un codice, letto sul periodo o, fuori servizio, sull'ultimo giorno di servizio.
_Avoid_: Contributo per competenza

**Condizione di proposta**:
Fatto che il corpus richiede, per un istituto e con date e riferimento, perché un suo importo entri in una versione di proposta: deve coprire tutti i giorni dell'importo. Senza il fatto l'importo resta calcolato e visibile tra gli esclusi, col motivo. È il caso dell'attestazione della prestazione.
_Avoid_: Visto, blocco del calcolo (il calcolo prosegue)

**Condizioni congiunte**:
`anche_se` di una regola: altre condizioni `tipo=codice` che devono valere insieme ad `applica_se`, tutte sui fatti categoriali del periodo. Se una non vale la regola non produce nessun importo.
_Avoid_: Regola con più condizioni scritte nella formula

**Maturazione onere**:
Maturazione a giorni di un importo a carico dell'ente: non è reddito della persona e non concorre a nessuna base, come la quota forfettaria dell'art. 86. Entra nella composizione del pagamento ma non nel netto.
_Avoid_: Contributo (che deriva da una base)

**Output del regime**:
Dichiarazione del corpus, con date e riferimento, delle basi o degli istituti con cui il regime assegna a una vista i rapporti che le spettano: la ListaPosPA prende chi ha importi nelle basi della gestione dipendenti pubblici, la lista collaboratori chi ha importi in gestione separata più la quota forfettaria. Una vista non conosce i titoli.
_Avoid_: Filtro per titolo

**Regola sul mese**:
Regola di cassa che legge il totale del mese delle basi, non il singolo periodo dichiarato, e si espone sull'ultimo periodo, come il contributo dell'1%.
_Avoid_: Contributo mensile (quando si intende un contributo per periodo)

**Recupero**:
Importo negativo pagato che entra in una base. Modellati i casi in servizio, detratto dal periodo fino a capienza con riporto ai mesi successivi; su sospeso, rinviato al rientro in servizio; e su cessato, in un periodo fuori servizio. Gli altri fermano il calcolo, compreso un riporto ancora aperto alla cessazione.
_Avoid_: Trattenuta (la trattenuta è un istituto)

**Riporto del recupero**:
Parte di un recupero che non trova capienza nella base di un periodo e passa, calcolata, al periodo in servizio successivo per la stessa base. Non è un fatto: ogni denuncia la ricava dalla precedente.

**Cessazione**:
Fatto del rapporto, valido dal giorno dopo l'ultimo giorno di servizio, che dice che il servizio è finito. Diverso dal codice cessazione della ListaPosPA, che è un dato della vista.

**Sospensione**:
Fatto del rapporto, valido dal giorno dopo l'ultimo giorno di servizio, che dice che il servizio è interrotto e riprende con un nuovo fatto di servizio. Recuperi e riporti attendono il rientro.

**Indebito**:
Fatto che dichiara una somma pagata senza titolo, con atto, modalità di restituzione (netto o lordo), importo tassato, ritenute riferibili e data di definitività. Ne leggono CU e 770; il movimento nelle basi è il recupero.
_Avoid_: Recupero (che è il movimento), somma a debito

**Cessazione**:
Fatto che chiude un rapporto. Dopo di essa un recupero sta in un periodo fuori servizio. La fine del servizio senza una cessazione o una sospensione ferma il calcolo.
_Avoid_: Sospensione (quando il rapporto prosegue), fine servizio (senza dire quale)

**Sospensione**:
Fatto che interrompe il servizio di un rapporto che prosegue, con inizio e, quando è noto, rientro. Un recupero attende il rientro in servizio.
_Avoid_: Cessazione temporanea, aspettativa (che è una delle possibili cause)

**Fermo**:
Dichiarazione del corpus: se un fatto è presente nel mese, il calcolo o la denuncia si ferma e nomina il caso non modellato. Con un codice, scatta solo per quel valore del fatto. Con `manca` e una condizione su un altro fatto, scatta al contrario quando il fatto non c'è o ha un codice fuori da `valori`; con `solo_se` scatta se il fatto c'è dove la condizione non vale.
_Avoid_: Blocco, errore generico

**Regime di fine servizio**:
Codice INPS del rapporto: 1 TFR, 2 optante, 3 TFS. Sceglie la contribuzione di fine servizio. TFS e TFR di un Comune stanno entrambi nella gestione ex INADEL.
_Avoid_: Tipo liquidazione

**Riduzione TFR**:
Riduzione del lordo di chi è in regime TFR, pari al 2,50% soppresso sull'80% delle voci utili al TFS. Non entra in nessuna base: le basi restano sul lordo intero, che è l'incremento figurativo del DPCM. Riduce invece l'imponibile fiscale, come reddito negativo di lavoro dipendente.
_Avoid_: Trattenuta 2,50% (il contributo è soppresso, non trattenuto)

**Ulteriori elementi TFR**:
Voci utili al TFR ma non al TFS, come la retribuzione di posizione dell'EQ: base propria al 100%, contributo al 6,91%. Per la posizione di dirigente e segretario il trattamento è da verificare (nota di prassi 9).
_Avoid_: Voci solo TFR

**Caso**:
Situazione reale modellata con i suoi fatti, la sua regola, il riferimento e un esempio verificato. Finché un caso non è modellato, il calcolo si ferma e lo nomina.
_Avoid_: Eccezione, formula generica

**Nota di prassi**:
Documento scritto nel repo che motiva una regola priva di fonte ufficiale puntuale; chi la legge sa che è prassi, e la spiegazione dell'importo lo segnala.
_Avoid_: Regola di casa

**Esito**:
Istantanea immutabile di ciò che è stato pagato, dichiarato o versato verso terzi; base del confronto per ogni differenza successiva. L'esito pagato nasce dall'evento di ritorno del pagamento eseguito, non dalla conferma, con tutte le righe di composizione dei soli rapporti pagati; l'esito versato nasce allo stesso modo dall'evento di versamento eseguito, con le righe versate ai terzi. Anche ciò che si invia per gli adempimenti non stipendiali (Tab. 15 e SICI, relazione tecnico-finanziaria, invio al MEF, trasparenza) è un esito dichiarato; se poi un fatto cambia la vista, il modello segnala la differenza con l'ultimo esito.
_Avoid_: Elaborazione chiusa, storico cedolini

**Vista**:
Aggregazione di importi in una forma richiesta (cedolino, ListaPosPA, F24EP, proposta di movimento contabile); non è fonte di verità.
_Avoid_: Stampa, tabulato

**Controllo di completezza degli output**:
Verifica che ogni importo pagato sia compreso in ogni output obbligatorio dichiarato dal suo regime, o ne sia escluso da una dichiarazione esplicita. Un'assenza non dichiarata ferma l'invio di quell'output, non il calcolo.
_Avoid_: Quadratura, controllo finale

**DenunciaIndividuale**:
Vista della denuncia per chi è a tempo determinato con pensione in CPDEL: dichiara alla gestione privata INPS, sotto la matricola DM dell'ente, il contributo NASpI a carico dell'ente e i dati utili alla prestazione. Accompagna la ListaPosPA dello stesso mese e dello stesso rapporto, che resta la denuncia della pensione. Si emette in ogni mese di rapporto attivo, anche senza imponibile. Produce un esito dichiarato.
_Avoid_: UniEmens privatistico (che è il canale, non la vista), DM10, flusso DS

**Lista collaboratori**:
Vista della denuncia per chi è in gestione separata (co.co.co. e quote forfettarie degli amministratori), separata dalla ListaPosPA: ha struttura e identità proprie e segue il mese di erogazione. Produce un esito dichiarato. Finché i codici del tracciato non sono nel corpus resta una bozza non trasmissibile, e lo è anche con una somma di cassa allargata. La quota forfettaria non ha imponibile e sta a carico dell'ente.
_Avoid_: ListaPosPA dei collaboratori, flusso parasubordinati

**Prospetto paga**:
Vista di un rapporto in un pagamento eseguito, letta dal suo esito pagato: posizione, righe sul netto con il loro periodo, netto e, a parte, le righe senza effetto sul netto. Uno per rapporto e per pagamento, mai per mese. Si ferma solo se manca un dato del contenuto di legge; gli altri dati mancanti sono avvisi. Spetta a ogni titolo che il regime dichiara.
_Avoid_: Cedolino mensile, busta paga, nota di pagamento

**Messa a disposizione del prospetto**:
Evento portato dall'adattatore del canale di consegna, con data e riferimento, da cui nasce l'esito dichiarato del prospetto paga. Il modello non recapita.
_Avoid_: Invio del cedolino, stampa

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

### Fisco

**Anno d'imposta**:
Anno a cui un pagamento è attribuito ai fini fiscali: quello della data di pagamento, o l'anno prima per le somme pagate entro il 12 gennaio, se la categoria di reddito dichiara la cassa allargata. La proposta lo calcola sulla valuta prevista; l'esito pagato lo congela sulla data reale. Se i due anni differiscono, il calcolo fiscale della persona si ferma. Sceglie il testo di legge da applicare. Un importo in tassazione separata conserva anche l'anno di riferimento della sua competenza.
_Avoid_: Anno fiscale (senza dire di cosa), anno di competenza (che è un altro asse)

**Imponibile fiscale**:
Base per persona e anno d'imposta che somma gli esiti pagati di tutti i suoi rapporti con l'ente in regime ordinario, ciascuno con la sua categoria di reddito. Le ritenute e il conguaglio la leggono.
_Avoid_: Imponibile IRPEF del rapporto, imponibile del mese (che è il valore di un solo pagamento)

**Ritenuta**:
Importo sul rapporto del pagamento in cui è operata, calcolato sulle somme di quel periodo di paga con gli scaglioni ragguagliati al periodo; la derivazione risale all'imponibile fiscale della persona.
_Avoid_: Ritenuta progressiva, trattenuta IRPEF (la trattenuta a terzi è un'altra cosa)

**Mensilità aggiuntiva**:
Dichiarazione datata dell'istituto, con riferimento e finestra di pagamento: la norma la vuole tassata a parte, con gli scaglioni ragguagliati a mese. La ritenuta a parte non è modellata: senza il conguaglio nello stesso pagamento il calcolo fiscale del rapporto si ferma; con il conguaglio procede con un avviso (ADR 0038).
_Avoid_: Tredicesima (che è uno degli istituti che la dichiarano), mensilità (senza dire quale)

**Dichiarazione del sostituito**:
Fatto della persona, con validità e documento di origine, che chiede le detrazioni a richiesta e ne dà le condizioni, e che può indicare un'aliquota più alta o redditi di altri sostituti da conguagliare. Senza dichiarazione le detrazioni a richiesta non si applicano e il modello lo segnala, senza fermarsi; la detrazione automatica si applica comunque.
_Avoid_: Modulo detrazioni, carichi di famiglia (che sono solo una parte)

**Familiare a carico**:
Fatto della persona, uno per familiare (chiave: il suo codice fiscale), con relazione, data di nascita, percentuale, validità e documento di origine: è la richiesta delle detrazioni dell'art. 12 per quel familiare, senza passare dalla dichiarazione del sostituito. La detrazione si applica a mese, un dodicesimo della formula annua per ogni familiare a carico nel mese di paga; per i figli l'età si ricava dalla data di nascita e fuori fascia il familiare resta registrato con un avviso. Una variazione è un nuovo fatto datato (ADR 0033).
_Avoid_: Carico, dichiarazione dei carichi

**Detrazione a richiesta**:
Detrazione che si applica solo se la persona la chiede con la dichiarazione del sostituito, come quella per lavoro dipendente.
_Avoid_: Detrazione d'ufficio

**Detrazione per la carica elettiva**:
Detrazione a richiesta dell'art. 13 c. 5 per chi ha un reddito di carica elettiva. Non si somma a quella per lavoro dipendente: il modello applica la più alta, in ogni ritenuta e al conguaglio, salvo una scelta scritta nella dichiarazione del sostituito. Al conguaglio è intera, non rapportata ai giorni di servizio.
_Avoid_: Detrazione amministratori, detrazione per altri redditi

**Detrazione automatica**:
Detrazione che il sostituto riconosce senza richiesta della persona, come l'ulteriore detrazione per i redditi tra 20.000 e 40.000 euro.
_Avoid_: Bonus, cuneo (che comprende anche la somma esente, che non è una detrazione)

**Somma esente**:
Somma pagata in busta a chi ha un reddito di lavoro dipendente fino a 20.000 euro, in percentuale del reddito di lavoro dipendente del mese scelta sul reddito annuo stimato. Non concorre al reddito e non è una detrazione. Il sostituto la recupera in compensazione nella delega.
_Avoid_: Cuneo, bonus, detrazione

**Trattamento integrativo**:
Somma pagata in busta a lavoratori dipendenti e assimilati fino a 28.000 euro di reddito, ripartita fra i pagamenti e ricalcolata al conguaglio. Tra 15.000 e 28.000 euro conta le detrazioni note e gli oneri comunicati dalla persona. Il sostituto la recupera in compensazione nella delega.
_Avoid_: Bonus Renzi, ex bonus 100 euro

**Recupero a rate**:
Restituzione, decisa al conguaglio, di un beneficio pagato e non spettante: oltre 60 euro, otto rate per il trattamento integrativo e dieci per somma esente e ulteriore detrazione insieme, dal primo pagamento dopo il conguaglio. Alla cessazione si recupera tutto sul pagamento finale.
_Avoid_: Rateizzazione (che è anche quella del 730-4 o della richiesta di differimento)

**Periodo di lavoro nell'anno**:
I giorni dell'anno in cui la persona ha avuto servizio presso l'ente, su tutti i suoi rapporti, festivi compresi. Al conguaglio rapporta le detrazioni che la norma lega al lavoro svolto.
_Avoid_: Giorni lavorati (che escludono i festivi), mesi di servizio

**Calendario dei festivi**:
Dato del corpus per anno, con il riferimento di legge: le feste nazionali fisse, il 4 ottobre dal 2026 e il lunedì dell'Angelo, la cui Pasqua è calcolata e non scritta a mano. Un anno senza calendario resta «non dichiarato» e il calcolo si ferma.
_Avoid_: Festività (senza dire se nazionali o del patrono), giorni di chiusura

**Patrono**:
Festa del santo del comune di sede di lavoro: fatto datato del rapporto (`patrono_sede_lavoro`, «codice comune MM-GG»), con il riferimento al CCNL nel corpus. Si unisce ai festivi nazionali e non aggiunge giorni se cade di sabato, di domenica o su una festa nazionale. Per il segretario in convenzione si registra quello del comune capofila.
_Avoid_: Festa locale, santo patrono dell'ente

**Conguaglio fiscale**:
Ricalcolo dell'imposta dell'anno sull'imponibile fiscale della persona, confrontato con le ritenute già negli esiti. Si fa sull'ultimo pagamento attribuito all'anno, o su quello finale alla cessazione; se un fatto cambia il dovuto, ne segue uno nuovo per differenza, entro il 28 febbraio per l'anno precedente. Una proiezione resta visibile come avviso.
_Avoid_: Conguaglio (senza dire quale: c'è anche quello contributivo), ricalcolo di dicembre

**Richiesta di differimento**:
Fatto della persona che chiede di trattenere nei mesi successivi, con interesse, l'imposta del conguaglio che non trova capienza. Senza richiesta la trattenuta si ferma a capienza e il resto va in CU come non trattenuto.

**Incapienza del conguaglio**:
Parte del conguaglio IRPEF a debito che il netto del pagamento, dopo tutte le altre righe, non copre. Con la richiesta di differimento diventa resto differito; senza, non trattenuto.
_Avoid_: Capienza (che è quella del fondo), netto negativo

**Resto differito**:
Incapienza che passa, calcolata, ai pagamenti successivi con l'interesse dello 0,50% mensile, fino all'ultimo pagamento di dicembre dell'anno di trattenuta o alla cessazione. Non è un fatto: ogni pagamento lo ricava dal precedente. Quello che resta alla fine diventa non trattenuto.

**Non trattenuto**:
Imposta del conguaglio che il sostituto non ha potuto trattenere, per incapienza o cessazione: la CU la riporta e la persona la versa entro il 15 gennaio.
_Avoid_: Rateizzazione (che è anche quella del 730-4 o dei recuperi oltre i 60 euro)

**Domicilio fiscale**:
Fatto datato della persona, con il comune e la regione, letto dalle regole delle addizionali, che con il domicilio al 1° gennaio dell'anno scelgono le aliquote della regione e del comune.
_Avoid_: Residenza (quando si intende il domicilio fiscale), comune dell'anagrafica

**Addizionale**:
Imposta regionale o comunale sull'imponibile fiscale della persona dell'anno, dovuta solo se è dovuta l'IRPEF. Le aliquote, a fasce e con una soglia di esenzione, sono un parametro datato per regione e per comune. Si trattiene a rate nell'anno dopo: il **saldo** dal conguaglio e, per la comunale, l'**acconto** sul reddito dell'anno prima.
_Avoid_: Addizionale IRPEF (senza dire quale), aliquota del comune (che è solo una parte del parametro)

**Rata dell'addizionale**:
Quota del saldo o dell'acconto trattenuta in un mese: il residuo da trattenere diviso i mesi rimasti fino a novembre. Una per persona e mese. Alla cessazione il residuo si trattiene tutto insieme.
_Avoid_: Rateizzazione (che è del 730-4 o della richiesta di differimento), piano di rate

**Esito 730-4**:
Fatto della persona che arriva dal canale 730-4 con la sua provenienza: crediti, debiti, rate e acconti da operare, con l'anno dei redditi dichiarati. Un 730-4 rettificativo o integrativo lo sostituisce con un nuovo fatto. Le regole ne ricavano rimborsi e trattenute dal primo pagamento utile da luglio.
_Avoid_: 730 (che è la dichiarazione della persona, non il risultato contabile per il sostituto), importazione 730

**Conguaglio non effettuato**:
Fatto con il codice della CU che dice perché un conguaglio, da 730-4 o di fine anno, non si è potuto fare: cessazione, aspettativa, decesso, retribuzione insufficiente, incapienza, passaggio senza interruzione.
_Avoid_: Conguaglio sospeso, anomalia 730

**Reddito del biennio**:
Fatto della persona con i redditi corrisposti dall'ente nei due anni prima di quello in cui è sorto il diritto, preso dalle CU già consegnate, per l'aliquota media della tassazione separata quando quegli anni sono anteriori al modello. Un reddito nullo è un valore, non un dato mancante: la regola usa l'aliquota del primo scaglione. Se il fatto manca, il calcolo fiscale si ferma.
_Avoid_: Aliquota media (che è il risultato della regola), storico redditi

**Reddito annuo stimato**:
Pagato dall'inizio dell'anno diviso i giorni di servizio per 365 (circ. 4/E/2025), più i redditi di altri sostituti della dichiarazione del sostituito, usato quando una regola dipende dal reddito dell'anno e il sostituto deve operare prima di conoscerlo (limite della sostitutiva sull'accessorio, fascia della somma esente, soglie del trattamento integrativo). Il conguaglio fiscale la sostituisce con il reddito vero.
_Avoid_: Reddito presunto, proiezione del conguaglio (che è un avviso, non una base)

**Reddito dell'anno precedente**:
Fatto della persona, preso dalla CU, con il reddito imponibile dell'anno prima quando il modello non ha il suo conguaglio. Lo leggono la base e l'esenzione dell'acconto dell'addizionale comunale; senza, l'acconto non si trattiene e tutto passa al saldo.
_Avoid_: Reddito del biennio (che è della tassazione separata)

**Corrispondenza di riferimento**:
Dato datato che porta un riferimento abrogato al suo successore, articolo per articolo, comma per comma e lettera per lettera, come dall'art. 51 c. 2 TUIR all'art. 53 c. 2 del TU dal 01/01/2027. Cambia il riferimento, non la regola né il suo valore.
_Avoid_: Tabella di conversione, alias della norma

**Trattenuta a terzi**:
Importo che una regola calcola sul netto, dopo ritenute fiscali e contributi, per un pignoramento, una cessione o una delegazione trascritti come atto esterno sul rapporto. È un versamento a terzi nella composizione del pagamento. I limiti si misurano sul netto di ogni pagamento, meno le sole ritenute di legge. Tra istituti diversi vale chi è notificato prima; più pignoramenti, o un concorso non ancora modellato, fermano il calcolo.
_Avoid_: Trattenuta (senza dire quale), ritenuta (che è fiscale), quinto (che è solo uno dei limiti)

**Verifica 48-bis**:
Controllo presso l'agente della riscossione prima di pagare un netto sopra soglia (2.500 euro per i dipendenti, 5.000 per gli altri titoli), sul singolo pagamento. Richiesta ed esito sono fatti datati della persona; senza esito il rapporto è fermo (ADR 0036).
_Avoid_: Blocco (che è solo l'effetto), trattenuta 48-bis (non è una trattenuta)

**Somma sospesa 48-bis**:
Parte del netto che l'ente accantona dopo un esito inadempiente: il minore tra debito comunicato, fascia sul netto e metà del netto meno le trattenute a terzi. Diventa trattenuta a terzi con l'ordine di versamento; torna al dipendente col debito pagato o ridotto, o dopo 60 giorni senza ordine.
_Avoid_: Pignoramento (lo diventa solo con l'ordine), trattenuta

**Assenso dell'ente**:
Atto esterno datato con cui l'ente consente che cessione e delegazione insieme superino la metà del netto. Senza, oltre la metà il calcolo si ferma.

**Punto CU**:
Mappatura datata dell'istituto o della categoria di reddito verso un punto della CU, per anno di certificazione, come la voce SICO o il codice tributo. Se la numerazione cambia, cambia la mappatura e non l'istituto.
_Avoid_: Codice CU dell'istituto, rigo (che è del 770)

### Versamenti e altri output

**Delega F24EP**:
Vista delle liquidazioni verso terzi di una scadenza: righe per sezione, codice tributo o causale, riferimento, debito e credito, ricavate dalla composizione del pagamento delle proposte pagate. Il codice tributo è una mappatura datata dell'istituto. Trasmessa è un esito dichiarato che non cambia più; una correzione è una nuova delega.
_Avoid_: F24 (senza dire quale), modello F24EP mensile, tracciato F24EP (che è solo la forma del file)

**Credito da compensare**:
Credito del sostituto (rimborso da assistenza fiscale, trattamento integrativo, somme restituite col conguaglio e simili) che una regola ricava dagli esiti pagati, dalla natura della riga di composizione e qualunque sia il suo canale, e porta come riga a credito nella delega della stessa scadenza, mai come debito ridotto. Il rimborso resta una sola riga, sul netto del lavoratore. La parte non assorbita da tutti i debiti della delega passa alla scadenza successiva come fatto con la sua origine, salvo che l'Ufficio personale scelga il rimborso nel 770.
_Avoid_: Credito residuo (senza dire di quale scadenza), compensazione automatica

**Acconto IRAP**:
Istituto a carico dell'ente calcolato ogni mese sulla base IRAP dei pagamenti del mese, per regione della sede di lavoro, e versato nella delega del mese dopo. Il saldo annuale e la dichiarazione non ne fanno parte.
_Avoid_: IRAP (quando si intende solo l'acconto del mese), IRAP retributiva

**Sede di lavoro**:
Fatto datato sul rapporto che dice dove la persona lavora e da cui l'IRAP ricava la regione. Se manca vale la regione dell'ente. Non è il domicilio fiscale, che serve alle addizionali.
_Avoid_: Residenza, sede dell'ente (quando si intende quella della persona)

**Esclusione dalla base IRAP**:
Fatto datato sul rapporto, con il motivo (disabile, apprendista, CFL), che toglie la persona dalla base dell'acconto IRAP.
_Avoid_: Esenzione IRAP, deduzione IK4 (che è il rigo della dichiarazione)

**Data di versamento**:
Fatto scelto dall'Ufficio personale per una delega F24EP. Il modello avvisa se cade dopo la scadenza che la regola ricava. Non è la data dell'esito versato, che viene dall'evento di ritorno.
_Avoid_: Scadenza (che è della regola), data di pagamento (che è dei netti)

**Ultimo miglio**:
Vista dei valori da digitare in PASSWEB per una pratica di pensione o di fine servizio (TFS/TFR, DMA previste, miglioramento contrattuale), ricavata dagli esiti pagati e dai fatti del rapporto. Diventa esito dichiarato quando l'Ufficio personale registra l'inserimento. La sistemazione della posizione non ne fa parte: è la ListaPosPA a variazione.
_Avoid_: Pratica PASSWEB, modello TFR1 (sostituito)

**Retribuzioni pregresse**:
Fatto del rapporto, con fonte, sugli importi dei mesi anteriori all'avvio del modello che l'ultimo miglio deve leggere. Se manca, la vista lo chiede come dato mancante e non stima.
_Avoid_: Storico cedolini, ricostruzione retributiva

**Voce di tariffa INAIL**:
Fatto datato sul rapporto che lo classifica ai fini del premio INAIL. Con la base imponibile INAIL alimenta la dichiarazione delle retribuzioni.
_Avoid_: Posizione INAIL (che è dell'ente), codice rischio

**Dichiarazione delle retribuzioni INAIL**:
Vista annuale che espone la regolazione dell'anno precedente e la rata dell'anno sulla base imponibile INAIL, per voce di tariffa. L'invio è un esito dichiarato; il premio si versa nella sezione INAIL della delega F24EP, senza compensazioni.
_Avoid_: Autoliquidazione (quando si intende solo la dichiarazione), denuncia salari

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
Dichiarazione dell'istituto, con date e riferimento, di che cosa lo paga: una destinazione del fondo del suo ambito, il bilancio o un'altra provvista dichiarata. Può essere parziale. Se manca, la versione di proposta non si emette. Un importo consuma il fondo del suo anno di competenza, non dell'anno di pagamento.
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
Applicazione già sviluppata dall'utente, da cui si prendono regole, parametri con fonte e motori deterministici, riscritti nel modello; può servire da controllo indipendente su un output del modello. Non genera output e non è un riferimento strutturale.
_Avoid_: Modulo, componente legacy
