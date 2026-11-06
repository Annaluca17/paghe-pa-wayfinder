# Ogni output è una vista del modello; i tool cedono regole e motori, non generano

Il modello paghe produce da sé **tutti** i suoi output obbligatori: F24EP, PASSWEB, Conto Annuale, PIAO, trasparenza e autoliquidazione INAIL, come già CU e 770 (ADR 0020). Ogni output è una **vista** e ogni invio produce un **esito dichiarato** immutabile. Se dopo l'invio un fatto cambia la vista, il modello segnala la differenza con l'ultimo esito e la correzione è un nuovo invio.

I **tool esistenti** non sono generatori, nemmeno quando conoscono un tracciato ufficiale già verificato. Dai tool si prendono:

- **regole e parametri** con la loro fonte, portati nel corpus;
- **motori deterministici**, riscritti nel nucleo del modello sulla specifica ufficiale;
- il ruolo di **controllo indipendente**: il tool legge l'output del modello, o ricalcola sugli stessi dati, e segnala le differenze.

I codici esterni (codice tributo, causale, voce SICO, punto CU, voce di tariffa INAIL) sono **mappature datate dell'istituto**, scelte per anno di riferimento: così la successione del 01/01/2027 (TU D.Lgs. 117/2026, D.Lgs. 33/2025) cambia la mappatura, non l'istituto.

Il **controllo di completezza degli output** (ADR 0015) vale per gli output che sommano importi: F24EP, Conto Annuale e autoliquidazione INAIL, oltre a CU e 770. PIAO e trasparenza non sommano importi propri: riusano altre viste o leggono fatti, e per loro vale la segnalazione della differenza con l'ultimo esito.

Scelto da Luca il 06/11/2026 nel grilling del ticket #45, domande 1, 9 e 10. Sulla domanda 10 Luca ha respinto il motore JavaScript di F24EP-editor come generatore integrato: paghe-pa è un sistema a sé stante e l'F24EP nasce dall'elaborazione del mese.

## Considered Options

- **Tool come generatore quando conosce un tracciato ufficiale** (proposta iniziale per F24EP-editor, con un ingresso JSON «da modello»): lega il modello a un altro linguaggio e a un altro repo per un output mensile, e il contenuto della delega passerebbe un confine in più.
- **Il modello esporta, l'operatore carica nel tool:** reintroduce un passaggio manuale, contro l'obiettivo della mappa.
- **Tool invariati, alimentati dai file intermedi del gestionale** (UniEmens per F24EP-editor, cedolini Halley per Pensione-2.0): ricostruiscono a valle ciò che il modello sa già alla fonte.

## Consequences

- Ogni nuovo output porta con sé un tipo di fatto con un lettore, se mancano dati (ADR 0012).
- Un tool usato come controllo non diventa una dipendenza del modello: i suoi controlli si replicano nei test, il tool resta fuori.
- Dai README, dai commenti e dalle fixture dei tool non si copiano dati reali.
