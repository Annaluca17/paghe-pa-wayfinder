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
Legame tra una persona e l'ente per un titolo di compenso (lavoro dipendente, mandato elettivo, co.co.co., LSU/LPU, incarico); una persona può averne più di uno. Le aggregazioni per persona (conguaglio, CU) sono viste.
_Avoid_: Dipendente, matricola, posizione

**Istituto**:
Elemento retributivo o trattenuta definito da norma o contratto, con riferimento; i codici esterni (SICO, UniEmens, codice tributo, piano dei conti) sono mappature datate dell'istituto.
_Avoid_: Voce, codice voce

**Fatto**:
Evento registrato in modo immutabile e bitemporale (validità e registrazione), con atto fonte quando esiste; si corregge solo con un nuovo fatto.
_Avoid_: Movimento, variazione anagrafica

**Importo**:
Unità del modello: valore riferito a rapporto, istituto e periodo di competenza, con eventuale data di pagamento e derivazione (regola, parametri, fatti). Ricalcolabile finché non entra in un esito. Può derivare da altri importi (es. imponibili), senza cicli.
_Avoid_: Voce, riga di cedolino

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
