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
Ogni persona che riceve dall'ente un compenso soggetto ad adempimenti da sostituto d'imposta o previdenziali: comparto, dirigenza, segretario, amministratori, co.co.co., LSU/LPU.
_Avoid_: Dipendente (quando si intende l'insieme intero)

### Integrazione

**Proposta di movimento contabile**:
Movimento di contabilità armonizzata (impegno, liquidazione, mandato, reversale) generato dal modello paghe e soggetto a conferma della Ragioneria.
_Avoid_: Export contabile, flusso contabile

**Output obbligatorio**:
Prodotto richiesto da norma verso un ente esterno o un soggetto (UniEmens/ListaPosPA, F24EP, CU, 770, Conto Annuale, PASSWEB, conguagli, esiti 730-4).
_Avoid_: Stampa, report

### Calcolo

**Rapporto**:
Legame tra una persona e l'ente per un titolo di compenso (lavoro dipendente, mandato elettivo, co.co.co., LSU/LPU, incarico); una persona può averne più di uno. Le aggregazioni per persona (CU) sono viste; una regola può leggere un cumulo per persona (conguaglio, massimale) purché resti tracciato.
_Avoid_: Dipendente, matricola, posizione

**Istituto**:
Elemento retributivo o trattenuta definito da norma o contratto, con riferimento; i codici esterni (SICO, UniEmens, codice tributo, piano dei conti) sono mappature datate dell'istituto.
_Avoid_: Voce, codice voce

**Fatto**:
Evento registrato in modo immutabile e bitemporale (validità e registrazione), con atto fonte quando esiste; si corregge solo con un nuovo fatto. Il valore è un numero o, per contratto, qualifica e simili, un codice che una formula non legge.
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
Giorno in cui la somma esce dalla disponibilità dell'ente per entrare nel patrimonio del dipendente, cioè la valuta dell'accredito, registrato come fatto legato all'esito pagato. Decide in quale denuncia entrano gli importi di quell'esito.
_Avoid_: Data di liquidazione (la liquidazione è una fase contabile)

**Base imponibile**:
Insieme degli importi pagati su cui si calcola una contribuzione (CPDEL, Fondo Credito, TFS, TFR). Una base non deriva da un'altra, salvo che una norma lo dica.
_Avoid_: Imponibile (senza dire quale)

**Concorso**:
Dichiarazione, con date e riferimento, di come un istituto entra in una base: intero, parziale o escluso. Vale la dichiarazione vigente alla data di pagamento; se è assente o parziale il calcolo si ferma.
_Avoid_: Flag imponibile

**Regola di cassa**:
Regola che legge una base o un'altra regola di cassa. Si sceglie alla data di pagamento, con i parametri vigenti in quel giorno, e produce importi solo nella denuncia.
_Avoid_: Contributo per competenza

**Regola sul mese**:
Regola di cassa che legge il totale del mese delle basi, non il singolo periodo dichiarato, e si espone sull'ultimo periodo, come il contributo dell'1%.
_Avoid_: Contributo mensile (quando si intende un contributo per periodo)

**Recupero**:
Importo negativo pagato che entra in una base. Modellati i casi in servizio, detratto dal periodo, e su cessato, in un periodo fuori servizio; gli altri fermano il calcolo.
_Avoid_: Trattenuta (la trattenuta è un istituto)

**Fermo**:
Dichiarazione del corpus: se un fatto è presente nel mese, il calcolo o la denuncia si ferma e nomina il caso non modellato.
_Avoid_: Blocco, errore generico

**Caso**:
Situazione reale modellata con i suoi fatti, la sua regola, il riferimento e un esempio verificato. Finché un caso non è modellato, il calcolo si ferma e lo nomina.
_Avoid_: Eccezione, formula generica

**Nota di prassi**:
Documento scritto nel repo che motiva una regola priva di fonte ufficiale puntuale; chi la legge sa che è prassi, e la spiegazione dell'importo lo segnala.
_Avoid_: Regola di casa

**Esito**:
Istantanea immutabile di ciò che è stato pagato, dichiarato o versato verso terzi; base del confronto per ogni differenza successiva.
_Avoid_: Elaborazione chiusa, storico cedolini

**Vista**:
Aggregazione di importi in una forma richiesta (cedolino, ListaPosPA, F24EP, proposta di movimento contabile); non è fonte di verità.
_Avoid_: Stampa, tabulato

**Regola**:
Logica di calcolo generale, versionata, con riferimento normativo obbligatorio.
_Avoid_: Formula, voce calcolata

**Parametro**:
Valore numerico o tabellare con periodo di vigenza e fonte puntuale (norma, circolare, CCNL, delibera).
_Avoid_: Costante, tabella di sistema

**Input da atto**:
Decisione discrezionale dell'ente (contratto integrativo, costituzione del fondo, determina, valutazione) registrata come fatto con atto fonte e decorrenza; mai codificata come regola.
_Avoid_: Parametro locale, personalizzazione

### Metodo

**Tool esistente**:
Applicazione già sviluppata dall'utente, usata come fonte di regole e conoscenza normativa deterministica e, dove utile, come generatore di output; non è un riferimento strutturale.
_Avoid_: Modulo, componente legacy

**Struttura di riferimento**:
Schema sigillato dell'utente, scritto prima della mappa, usato solo come controllo di completezza nel confronto finale.
_Avoid_: Modello di riferimento, architettura target
