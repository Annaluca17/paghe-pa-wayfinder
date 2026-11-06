# Frazioni del mese e maturazione dichiarata

Il mese si divide in frazioni in cui fatti, regole e parametri sono uniformi, e ogni frazione produce il proprio importo. Ogni regola dichiara come matura: `giorni`, `evento`, `periodo` (sul periodo dichiarato) o `annuale`. Il motore offre i conteggi dei giorni, mentre il divisore sta nella regola come parametro con vigenza e fonte. Quanto non è modellato continua a fermare il calcolo con un errore.

Scelto perché ogni frazione conserva la propria derivazione, e perché nessun testo contrattuale trovato fissa il divisore del mese parziale: incorporarlo nel motore avrebbe nascosto una scelta di prassi.

## Considered Options

- Un solo importo per mese, con le frazioni nella derivazione: più semplice, ma la derivazione non corrisponderebbe a un importo.
- Una frazione apre sempre un periodo nella ListaPosPA: scartata, perché un aumento a metà mese non è di per sé un cambio che INPS distingue.
- Ratei mensili di tredicesima: scartati, perché l'importo si calcola sulla retribuzione di dicembre o dell'ultimo mese (art. 75 CCNL 16/11/2022).

## Consequences

- L'importo è riferito a un periodo con date, non più a un mese. Il totale del mese è una vista, e il confronto con gli esiti avviene per istituto, perché i fatti possono cambiare le frazioni.
- A mese intero la quota dell'ultima frazione è il residuo: la somma delle frazioni coincide col mensile, anche nei mesi con 27 giorni da lunedì a sabato. È una scelta di progetto, non letta su una fonte.
- I contributi maturano sul periodo dichiarato, leggendo la somma delle frazioni. Il corpus elenca in `[periodo_dichiarato]` i fatti che ne aprono uno nuovo; l'elenco reale è ancora da riscontrare sulle fonti INPS.
- Un importo annuale ha come periodo il servizio dell'anno e non entra nel calcolo mensile. Quota in 365esimi con tetto a 1; il trattamento dell'anno bisestile è un'interpretazione.
- Una nota scritta in `docs/prassi/`, citata come `prassi:immedia:nota:...`, può fondare una regola. Se è l'unica fonte, la spiegazione dell'importo lo segnala.
- Il divisore e l'indennità di comparto si appoggiano alla nota 1. I cedolini osservati sono in ventiseiesimi da lunedì a sabato, ma sono prassi di un gestionale, non norma.
- Un'esposizione divisa di giorni nella denuncia, come il «Dividi periodo» di SCAD, è un'altra operazione: se INPS ripartisce in giorni di calendario, può non coincidere con quanto calcolato qui.
- Restano fuori le assenze con riduzione e la divisione della tredicesima per part-time o cambio di regime: per ora fermano il calcolo o restano da modellare.
