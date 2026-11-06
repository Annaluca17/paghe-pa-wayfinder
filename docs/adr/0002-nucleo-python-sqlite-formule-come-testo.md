# Nucleo in Python e SQLite, formule come testo analizzato

Il nucleo dell'ADR 0001 è in Python, senza dipendenze a runtime. Il registro è su SQLite, con trigger che rifiutano UPDATE e DELETE. Regole e parametri stanno in file TOML; una formula è testo analizzato con una grammatica chiusa e mai eseguito come codice.

Scelto perché l'aritmetica `Decimal`, `tomllib` e `sqlite3` sono nella libreria standard, e perché per enti fino a 400 dipendenti un database relazionale append-only basta. Il corpus resta dato: si può versionare, confrontare e tradurre verso altri formati.

## Considered Options

- Regole come funzioni Python: più semplici, ma non restano dato leggibile e traducibile.
- Motore esistente: già scartato dall'ADR 0001.

## Consequences

- Una formula ammette solo costanti intere: ogni valore normativo deve essere un parametro con vigenza e fonte.
- Nessun arrotondamento implicito: lo dichiara la regola con `arrotonda`. Il mezzo per eccesso copre le regole trovate nel ticket #15 (`docs/research/arrotondamenti-norma.md`).
- La versione del corpus è l'impronta del contenuto. Una correzione cambia versione anche se l'autore dimentica di dichiararla; la `versione` della regola resta dichiarata.
- La competenza è mensile. Se un fatto, una regola o un parametro cambia dentro il mese, il calcolo si ferma con un errore: i ratei non sono ancora modellati e non vengono stimati.
- Il riferimento è testo libero non vuoto, finché il ticket #17 non fissa la sintassi.
- Ogni regola seleziona la vigenza per competenza. Le regole selezionate per data di pagamento non sono ancora supportate.
- Pagato e versato si confrontano per somma degli esiti; il dichiarato per sostituzione integrale dell'ultimo esito sul periodo.
