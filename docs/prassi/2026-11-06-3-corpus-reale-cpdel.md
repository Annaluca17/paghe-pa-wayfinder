# Nota di prassi 3: corpus reale CPDEL del comparto

Riferimento: `prassi:immedia:nota:2026-11-06;3`. Fonte: decisioni dell'operatore del 06/11/2026, registrate nel ticket #29, e scelte di progetto, come indicato in ogni sezione. Il corpus è `corpus/funzioni-locali-cpdel.toml`.

## Tabellare mensile

**Decisione dell'operatore.** Il mensile è `arrotonda(annuo / 12, 2)` della tab. B del CCNL 28/10/2026, per area. Moltiplicato per 12 si scosta dalla tab. B di 1 centesimo, 3 per i Funzionari. Lo scarto non si recupera su una mensilità.

| Area | 2026 | 2027 |
|---|---|---|
| Funzionari ed EQ | 2.192,02 | 2.231,36 |
| Istruttori | 2.019,63 | 2.055,86 |
| Operatori esperti | 1.796,60 | 1.828,80 |
| Operatori | 1.724,21 | 1.755,04 |

**Limiti.** La tab. B è annua e la tab. A dà solo gli incrementi. Nessuna fonte letta dice come ricavare il mensile.

## Quote CPDEL

**Scelta di progetto.** Il totale e la quota del lavoratore si arrotondano ciascuno al centesimo. La quota dell'ente è la differenza tra i due. È la proposta B3 della ricerca #15 (`docs/research/arrotondamenti-norma.md`): la ListaPosPA espone un solo contributo per periodo, mentre la ritenuta in busta e la CU chiedono la quota del lavoratore.

**Limiti.** Nessuna fonte primaria sceglie tra l'arrotondamento del totale e quello di ciascuna quota. Rispetto alla somma delle quote arrotondate i due metodi differiscono di 1 centesimo in casi reali. Da confermare con il manuale ListaPosPA o con INPS.

## Recupero su cessato

**Decisione dell'operatore (scelta (a) nel ticket #29).** Il recupero dopo la cessazione è un importo negativo nella base del mese in cui viene pagato, in un periodo fuori servizio. La vista ListaPosPA della parte 3 non lo espone: si ferma e indica il quadro necessario.

**Riscontrato il 06/11/2026 (norma certa, istruzione INPS).** Il codice motivo 7 è «Recupero competenze dipendente cessato» (Allegato tecnico UniEmens 4.33.1, p. 254). Il codice motivo si compila solo con la causale 7 (documento tecnico 4.33, p. 204). Il quadro è quindi il V1 causale 7, codice motivo 7. Le due fonti vengono dallo stesso istituto.

**Da verificare.** Il periodo da valorizzare, cioè quello che precede la sospensione, e il codice cessazione 32 vengono ancora solo dal vault, da una pagina PassWeb sui pensionamenti.

Il motore distingue i recuperi così:

- **In servizio:** l'importo negativo è detratto dalla base del periodo (nota di prassi 2).
- **Su cessato:** periodo fuori servizio, con un servizio terminato prima del mese.
- **Fuori servizio senza un servizio precedente:** il calcolo si ferma.
- **Mese negativo in servizio:** se la base del periodo resta negativa, il calcolo si ferma.

Restano fuori le riduzioni INADEL ed ENPAS, che riguardano il TFS e ricadono già nel suo fermo. Restano fuori anche il massimale, che ha un fermo proprio, e le sentenze e transazioni. Queste ultime oggi non si riconoscono dai fatti: un recupero da sentenza verrebbe trattato come in servizio o su cessato. Serve un fatto o un tipo di atto che le distingua.

## Fermi

**Scelta di progetto.** La prima fetta si ferma e nomina il caso quando trova:

- **regime di fine servizio (TFS o TFR):** contribuzione non modellata. Dall'ADR 0008 non ferma la denuncia: rende la ListaPosPA una bozza non trasmissibile;
- **part-time e retribuzione ridotta:** il riproporzionamento non è modellato. Fermano anche il calcolo;
- **aspettativa sindacale:** la retribuzione virtuale del Fondo Credito (Circ. INPS 6/2014 § 19) non è modellata;
- **più rapporti della stessa persona nell'anno**, riconosciuti dal codice fiscale: l'1% e il massimale si calcolano per persona;
- **superamento del massimale annuo**, sommando la base CPDEL da gennaio al mese. Il fermo scatta per chiunque, anche per chi non è soggetto al massimale, perché la data di prima iscrizione non è un fatto del modello;
- **conguaglio annuo dell'1%** a dicembre o nel mese di cessazione, se nell'anno il contributo aggiuntivo è stato diverso da zero. Se il contributo non è mai scattato, la somma dei dodici mesi resta sotto la prima fascia annua: 12 × 4.685 = 56.220, meno di 56.224.

Un fermo con un fatto assente non scatta. Il regime di fine servizio è un dato obbligatorio della ListaPosPA: la vista lo chiede (ADR 0008).

## Soglie annuali

La prima fascia e il massimale valgono per il 2026 e si chiudono il 31/12/2026. Una denuncia di gennaio 2027 si ferma finché la circolare 2027 non è nel corpus. L'indennità di comparto si chiude il 30/06/2027, perché per i Comuni l'incremento del 01/07/2027 dipende dal decreto di riparto (art. 36-bis c. 3 CCNL 28/10/2026).

## Quando rivedere

Quando INPS o il manuale ListaPosPA indicano come arrotondare le quote, quando il V1 causale 7 è riscontrato, o quando esce la circolare INPS sulle soglie 2027.
