# Corpus reale: regole sul mese, fermi dichiarati e cumuli che fermano

Il primo corpus reale (`corpus/funzioni-locali-cpdel.toml`) si carica con `reale=True`, che rifiuta i riferimenti `fittizio:`. Per scriverlo il motore aggiunge quattro capacità:

- **Regola sul mese:** maturazione `mese`, che legge il totale del mese delle basi e si espone sull'ultimo periodo.
- **Parametro con fine vigenza:** l'ultima vigenza di un parametro può avere `al`; oltre quella data il calcolo si ferma.
- **Condizione su un codice:** `applica_se = "tipo=codice"` applica la regola solo se il fatto categoriale ha quel codice.
- **Fermi dichiarati:** un fatto presente nel mese ferma il calcolo o la denuncia e nomina il caso.

Più rapporti, massimale e conguaglio annuo non si calcolano: la denuncia si ferma quando servirebbero.

Scelto perché l'1% si calcola sul totale del mese e si espone sull'ultimo periodo (nota di prassi 2), e perché le soglie INPS valgono un anno: senza una fine, la soglia del 2026 continuerebbe in silenzio nel 2027. La grammatica resta chiusa. L'area sceglie la regola senza che una formula legga un codice.

## Considered Options

- **1% come regola sul periodo, sommando i periodi:** l'arrotondamento per periodo cambierebbe il totale, e la soglia è mensile.
- **Area come parametro scelto dal motore:** servirebbe una tabella per codice nella grammatica. Un istituto per area è più verboso, ma resta dato.
- **Calcolare conguaglio e massimale:** richiede i cumuli per persona e la data di prima iscrizione, fuori dalla prima fetta.
- **Fermi scritti nel codice:** un corpus diverso, per esempio la dirigenza, avrebbe fermi diversi.

## Consequences

- Una regola sul mese legge solo basi e altre regole sul mese, e nessun'altra regola la legge. La base del mese è la somma delle basi dei periodi, con le date di pagamento dei loro importi.
- Il fermo è per presenza del fatto, non per valore. Se il fatto manca il fermo non scatta: la vista della parte 3 deve chiedere i dati obbligatori della ListaPosPA.
- Il fermo di TFS e TFR blocca la denuncia di quasi ogni dipendente reale, finché quelle contribuzioni non sono modellate. Gli importi si calcolano comunque.
- `[denuncia]` dichiara il fatto che identifica la persona (il codice fiscale), la base e il parametro del massimale e le regole sul mese con conguaglio annuo. Se il codice fiscale manca, la denuncia si ferma.
- Massimale e conguaglio ricalcolano le denunce dei mesi precedenti dello stesso anno, senza controllarne a loro volta i cumuli.
- Recuperi: in servizio e su cessato sono casi modellati; mese negativo in servizio e recupero fuori servizio senza un servizio precedente fermano la denuncia (nota di prassi 3). Le sentenze e le transazioni non si distinguono ancora dai fatti.
- Le quote CPDEL seguono la proposta B3 della ricerca #15: totale e quota del lavoratore arrotondati, quota dell'ente per differenza. È prassi-interpretazione.
- Il corpus reale copre competenze e pagamenti dal 01/01/2026. Fuori dalla copertura il calcolo si ferma con un parametro mancante.
