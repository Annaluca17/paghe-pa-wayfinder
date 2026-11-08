# Nucleo in Python e SQLite, formule come testo analizzato

Il nucleo dell'ADR 0001 è in Python, senza dipendenze a runtime. Il registro è su SQLite, con trigger che rifiutano UPDATE e DELETE. Regole e parametri stanno in file TOML; una formula è testo analizzato con una grammatica chiusa e mai eseguito come codice.

Scelto perché l'aritmetica `Decimal`, `tomllib` e `sqlite3` sono nella libreria standard, e perché per enti fino a 400 dipendenti un database relazionale append-only basta. Il corpus resta dato: si può versionare, confrontare e tradurre verso altri formati.

*Precisato il 08/11/2026 (grilling del ticket #93, scelta di Luca):* la grammatica ammette `se(condizione, allora, altrimenti)`, con un solo confronto (`<`, `<=`, `>`, `>=`) fra due espressioni come condizione. La formula resta testo analizzato e mai eseguito, e le costanti restano intere. Serve alle norme a fasce con un salto, come la detrazione dell'art. 13 c. 1 TUIR, che passa da 1.955 a 3.100 euro appena il reddito supera 15.000, e che con `min` e `max` non si può scrivere. Le alternative scartate sono due. La prima è il gradino `min(1, max(0, (R - soglia) × 100))`, esatto al centesimo ma illeggibile. La seconda è una tabella a fasce nel corpus: dovrebbe contenere formule diverse per fascia, quindi richiederebbe più motore.

## Considered Options

- Regole come funzioni Python: più semplici, ma non restano dato leggibile e traducibile.
- Motore esistente: già scartato dall'ADR 0001.

## Consequences

- Una formula ammette solo costanti intere: ogni valore normativo deve essere un parametro con vigenza e fonte.
- Nessun arrotondamento implicito: lo dichiara la regola con `arrotonda`. Il mezzo per eccesso copre le regole trovate nel ticket #15 (`docs/research/arrotondamenti-norma.md`).
- La versione del corpus è l'impronta del contenuto. Una correzione cambia versione anche se l'autore dimentica di dichiararla; la `versione` della regola resta dichiarata.
- Le variazioni dentro il mese seguono l'ADR 0004.
- Il riferimento segue la sintassi dell'ADR 0003.
- Ogni regola seleziona la vigenza per competenza. Fanno eccezione le regole di cassa, che seguono la data di pagamento (ADR 0006).
- Pagato e versato si confrontano per somma degli esiti; il dichiarato per sostituzione integrale dell'ultimo esito sul periodo.
