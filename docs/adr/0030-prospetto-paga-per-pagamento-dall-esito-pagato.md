# Prospetto paga: un prospetto per rapporto e per pagamento, dall'esito pagato

Il **prospetto paga** è una **vista** del modello (ADR 0022). Se ne produce uno per ogni **rapporto** e per ogni **pagamento eseguito**, non uno per persona e per mese: stipendio e arretrati pagati con due valute diverse danno due prospetti. La vista legge l'**esito pagato**, mai la versione di proposta, e non calcola nulla: prima del pagamento eseguito non c'è prospetto.

**Contenuto.** Tutto e solo ciò che l'esito pagato del rapporto porta:
- in testa ente, persona con codice fiscale, posizione (qualifica, oppure carica o incarico), tipo di fine servizio, data di pagamento;
- le righe con effetto sul netto (competenze e trattenute), ognuna con il suo periodo, così gli arretrati si vedono;
- il netto del rapporto in quel pagamento;
- separate, le righe senza effetto sul netto: contributi a carico dell'ente, imponibili TFS e TFR, IRAP, oneri dell'art. 86.

Detrazioni, imponibile fiscale, progressivi annui, ferie residue e TFR maturato **non** entrano finché non sono importi di un esito: sarebbero calcoli nuovi.

**Dati mancanti.** Fermano il prospetto solo i dati del contenuto dell'art. 1 L. 4/1953 (nome e cognome, codice fiscale, posizione, periodo, voci, trattenute). Gli altri danno un avviso e il prospetto si consegna. Il codice del contratto collettivo è un avviso finché la sua fonte per i contratti pubblici non è verificata.

**Titoli.** Una sola vista per dipendenti, dirigenti, segretari, amministratori e co.co.co. Il corpus dichiara, per regime, che il prospetto spetta e quale tipo di fatto dà la posizione (qualifica, carica, incarico): la vista non conosce i titoli.

**Consegna.** Il modello non recapita. L'adattatore del canale (area riservata, posta) riporta un **evento di messa a disposizione** con data e riferimento; da esso nasce l'**esito dichiarato** del prospetto. Se poi un fatto cambia la vista, il modello segnala la differenza con l'ultimo esito.

**Fonti.** Per Comuni e Province l'art. 4 L. 4/1953 esclude il contenuto minimo dell'art. 1 (norma certa, letta in sintesi); la prassi ministeriale presuppone comunque un prospetto per i dipendenti degli enti pubblici (prassi); il LUL dell'art. 39 D.L. 112/2008 riguarda il datore privato (norma certa). La vista non scende sotto l'art. 1. Dettaglio e punti da verificare in `docs/research/prospetto-paga.md`.

Scelto da Luca l'08/11/2026 nel grilling del ticket #86, domande 1–7.

## Considered Options

- **Un cedolino per persona e per mese, come i gestionali:** somma pagamenti che il modello tiene distinti e mescola valute diverse; il riepilogo mensile, se servirà, è una vista sopra questa.
- **Prospetto dalla versione di proposta confermata:** arriva prima, ma mostra netti che possono non essere pagati.
- **Contenuto come il cedolino NoiPA** (detrazioni, imponibile fiscale, progressivi): richiede calcoli dentro la vista.
- **Nota di pagamento a parte per amministratori e co.co.co.:** un secondo documento per gli stessi importi.
- **Consegna dentro il modello:** farebbe del modello un servizio di recapito.

## Consequences

- Un rapporto senza esito pagato nel pagamento non ha prospetto; un rapporto fermo nella versione non lo ha.
- La consegna elettronica richiede un adattatore per canale, fuori dal nucleo.
- Quando detrazioni o saldo ferie diventeranno importi di un esito, entrano nel prospetto senza cambiare la vista.
