# Mese di prova: resoconto

> **Dati e corpus fittizi.** Ente, persone, codici fiscali, IBAN e atti sono di fantasia; nessun valore di questo resoconto e' un importo vero. Il percorso gira su un corpus **non reale**: l'unione del corpus reale (`corpus/funzioni-locali-cpdel.toml`, che non cambia) e di un'aggiunta fittizia (`prove/mese_di_prova/corpus_fittizio.toml`, tutti i riferimenti `fittizio:`). Il corpus reale rifiuta i riferimenti fittizi (ADR 0003): per questo l'unione si carica come corpus non reale.

Il resoconto e' generato da `python -m prove.mese_di_prova` e fissato da `tests/test_mese_di_prova.py`: ogni ticket futuro lo cambia nel punto che sblocca.

## Corpus

| Voce | Corpus reale | Aggiunta fittizia | Unione usata |
|---|---:|---:|---:|
| istituti con regola | 22 | 2 | 24 |
| basi imponibili | 4 | 0 | 4 |
| fermi dichiarati | 4 | 0 | 4 |
| categorie di reddito | 0 | 1 | 1 |
| regole di ritenuta | 0 | 1 | 1 |
| regole di conguaglio | 0 | 1 | 1 |
| dichiarazioni di pagamento fisiologico | 0 | 1 | 1 |
| dichiarazioni di composizione | 0 | 25 | 25 |
| mappature verso codici esterni | 0 | 10 | 10 |
| codici nel catalogo F24EP | 0 | 7 | 7 |
| regole di scadenza F24EP | 0 | 2 | 2 |
| calendari dei festivi | 0 | 2 | 2 |

## Scenario

Ente fittizio in una sola regione, con i fatti sull'ente della delega (codice fiscale, denominazione, e-mail, IBAN di tesoreria, sigla di provincia) e l'ultimo pagamento del 2026 al 2026-12-18. Mese: marzo 2026, piu' dicembre 2026 per il conguaglio. Undici rapporti, ognuno per un caso:

| Rapporto | Titolo | Area | Regime di fine servizio | Caso |
|---|---|---|---|---|
| R01 | comparto | funzionari | 3 | funzionario a tempo pieno, mese intero (il caso base) |
| R02 | comparto | istruttori | 3 | arretrato: progressione ad area funzionari con decorrenza dal 01/02, atto di marzo |
| R03 | comparto | operatori_esperti | 3 | performance 2025 di competenza dell'anno prima, pagata a marzo |
| R04 | comparto | operatori | 3 | tempo parziale (60%) |
| R05 | comparto | istruttori | 3 | cessa il 14/03, a meta' mese |
| R06 | comparto | operatori_esperti | 1 | assunto il 16/03, regime TFR |
| R07 | comparto | istruttori | 3 | rimborso 730 a dicembre (730-4 dal primo pagamento utile da luglio) |
| R08 | dirigente | - | - | dirigente |
| R09 | segretario | - | - | segretario comunale |
| R10 | sindaco | - | - | sindaco, mandato di amministratore |
| R11 | co.co.co. | - | - | collaboratore coordinato e continuativo |

## Dove arriva ogni rapporto

| Rapporto | Marzo 2026 | Dicembre 2026 |
|---|---|---|
| R01 | completo, fino all'esito versato | si ferma al passo «Delega F24EP»: anno_imposta_mancante: il codice 150E vuole l'anno d'imposta e l'importo non lo porta |
| R02 | completo, fino all'esito versato | si ferma al passo «Delega F24EP»: anno_imposta_mancante: il codice 150E vuole l'anno d'imposta e l'importo non lo porta |
| R03 | completo, fino all'esito versato | si ferma al passo «Delega F24EP»: anno_imposta_mancante: il codice 150E vuole l'anno d'imposta e l'importo non lo porta |
| R04 | si ferma al passo «Calcolo»: part-time, riproporzionamento non modellato | si ferma al passo «Calcolo»: part-time, riproporzionamento non modellato |
| R05 | completo, fino all'esito versato | fuori servizio |
| R06 | completo, fino all'esito versato | si ferma al passo «Delega F24EP»: anno_imposta_mancante: il codice 150E vuole l'anno d'imposta e l'importo non lo porta |
| R07 | completo, fino all'esito versato | si ferma al passo «Delega F24EP»: anno_imposta_mancante: il codice 150E vuole l'anno d'imposta e l'importo non lo porta |
| R08 | si ferma al passo «Calcolo»: regime del titolo assente nel corpus | si ferma al passo «Calcolo»: regime del titolo assente nel corpus |
| R09 | si ferma al passo «Calcolo»: regime del titolo assente nel corpus | si ferma al passo «Calcolo»: regime del titolo assente nel corpus |
| R10 | si ferma al passo «Calcolo»: regime del titolo assente nel corpus | si ferma al passo «Calcolo»: regime del titolo assente nel corpus |
| R11 | si ferma al passo «Calcolo»: regime del titolo assente nel corpus | si ferma al passo «Calcolo»: regime del titolo assente nel corpus |

## Cosa manca per un mese completo

I fermi del mese, raggruppati per causa. L'ordine e' per quanti rapporti bloccano e poi per quanti passi del percorso (calcolo, versione, conferma, pagamento, denuncia, ListaPosPA, delega, file, ricevute, esito versato) restano chiusi, sommati su marzo e dicembre.

1. **anno_imposta_mancante: il codice 150E vuole l'anno d'imposta e l'importo non lo porta**: 5 rapporti bloccati, 20 passi, al passo «Delega F24EP», in dicembre. Casi: R07 (rimborso_irpef_730).
2. **regime del titolo assente nel corpus**: 4 rapporti bloccati, 80 passi, al passo «Calcolo», in marzo e dicembre. Casi: R08 (dirigente), R09 (segretario), R10 (sindaco), R11 (co.co.co.).
3. **part-time, riproporzionamento non modellato**: 1 rapporto bloccato, 20 passi, al passo «Calcolo», in marzo e dicembre. Casi: R04.

## Passaggi manuali

| Categoria | Avvio | Preparazione di febbraio | Marzo | Dicembre |
|---|---:|---:|---:|---:|
| Fatti di avvio, una tantum (anagrafica, assunzioni, inquadramento) | 113 | 0 | 13 | 0 |
| Fatti ricorrenti del mese (atti, variazioni, cessazioni, 730) | 0 | 0 | 16 | 1 |
| Conferme della Ragioneria | 0 | 1 | 1 | 1 |
| Scelte (valuta prevista, data di versamento, ultimo pagamento) | 0 | 1 | 2 | 3 |
| Eventi che oggi nessun adattatore porta (pagamento, ricevute, versamento) | 0 | 1 | 5 | 1 |
| Comandi di avvio (non sono dati: emissione, produzione dei file, trasmissione) | 0 | 1 | 3 | 1 |
| **Totale senza i comandi** | **113** | **3** | **37** | **6** |

La preparazione di febbraio e' il pagamento che precede il mese, scritto solo perche' l'arretrato di R02 e' una differenza rispetto a un esito pagato: non fa parte del mese e non e' nel totale di marzo.

Fatti di avvio per soggetto: R01 14, R02 14, R03 14, R04 14, R05 14, R07 14, R08 6, R09 6, R10 6, R11 6, ente 5.
Assunzione di marzo (avvio di un rapporto nuovo): R06 13.

Dettaglio di Marzo, escluso l'avvio:

- [ricorrente] 1 x rapporto R02: area
- [ricorrente] 1 x rapporto R02: qualifica
- [ricorrente] 1 x rapporto R03: performance
- [ricorrente] 1 x rapporto R05: annullamento di area
- [ricorrente] 1 x rapporto R05: annullamento di contratto
- [ricorrente] 1 x rapporto R05: annullamento di qualifica
- [ricorrente] 1 x rapporto R05: annullamento di regime_fine_servizio
- [ricorrente] 1 x rapporto R05: annullamento di tipo_impiego
- [ricorrente] 1 x rapporto R05: annullamento di tipo_servizio
- [ricorrente] 1 x rapporto R05: area
- [ricorrente] 1 x rapporto R05: codice_cessazione
- [ricorrente] 1 x rapporto R05: contratto
- [ricorrente] 1 x rapporto R05: qualifica
- [ricorrente] 1 x rapporto R05: regime_fine_servizio
- [ricorrente] 1 x rapporto R05: tipo_impiego
- [ricorrente] 1 x rapporto R05: tipo_servizio
- [conferma] 1 x conferma della versione 2
- [scelta] 1 x ente: data di versamento dei pagamenti di 2026-03
- [scelta] 1 x valuta prevista della versione (2026-03-27)
- [evento] 1 x pagamento eseguito della versione 2
- [evento] 1 x ricevuta della delega: addebito
- [evento] 1 x ricevuta della delega: controlli_formali
- [evento] 1 x ricevuta della delega: controllo_crediti
- [evento] 1 x versamento eseguito della delega
- [comando] 1 x emissione della versione di proposta (2026-03)
- [comando] 1 x produzione della denuncia e della ListaPosPA (2026-03)
- [comando] 1 x trasmissione della delega (2026-03)

Dettaglio di Dicembre, escluso l'avvio:

- [ricorrente] 1 x rapporto R07: rimborso_irpef_730
- [conferma] 1 x conferma della versione 3
- [scelta] 1 x ente: data di versamento dei pagamenti di 2026-12
- [scelta] 1 x ente: ultimo pagamento dell'anno 2026
- [scelta] 1 x valuta prevista della versione (2026-12-18)
- [evento] 1 x pagamento eseguito della versione 3
- [comando] 1 x emissione della versione di proposta (2026-12)

Nota: la cessazione di R05 costa 13 scritture a mano. Il nucleo non ha un fatto di cessazione: i fatti sono immutabili e il servizio di un rapporto finisce solo se si annullano i sei fatti di inquadramento aperti e si riscrivono con una fine (piu' il codice di cessazione).

## Il percorso, passo per passo

### Marzo 2026

**Fatti**

- Riuscito:
  - 126 fatti di avvio (ente, persone, rapporti, assunzione di R06) registrati nel registro
  - 16 fatti del mese: performance, progressione, cessazione
- Fermi: nessuno
- Su dati fittizi:
  - tutti: ente, persone e rapporti sono di fantasia

**Calcolo**

- Riuscito:
  - R01: 2 importi, lordo 2228.35
  - R02: 6 importi, lordo 2405.01
  - R02: arretrato su febbraio, differenza rispetto all'esito pagato: 4 righe, netto 176.66
  - R03: 3 importi, lordo 2424.12
  - R03: performance di competenza 2025: 600.00, pagamento fisiologico dichiarato dal corpus fittizio
  - R05: 2 importi, lordo 946.94
  - R06: 3 importi, lordo 982.22
  - R07: 2 importi, lordo 2051.69
- Fermi:
  - R04: caso non modellato, part-time, riproporzionamento non modellato (fatto part_time dal 2026-01-01; prassi:immedia:nota:2026-11-06;3)
  - R08 (dirigente): nessun importo; il fatto compenso_mensile registrato dall'Ufficio personale non e' letto da nessuna regola del corpus
  - R09 (segretario): nessun importo; il fatto compenso_mensile registrato dall'Ufficio personale non e' letto da nessuna regola del corpus
  - R10 (sindaco): nessun importo; il fatto compenso_mensile registrato dall'Ufficio personale non e' letto da nessuna regola del corpus
  - R11 (co.co.co.): nessun importo; il fatto compenso_mensile registrato dall'Ufficio personale non e' letto da nessuna regola del corpus
- Su dati fittizi:
  - tabelle e parametri del corpus reale; regole del corpus fittizio per: performance

**Versione di proposta**

- Riuscito:
  - versione 2: 54 righe di composizione, valuta prevista 2026-03-27, 6 rapporti
  - netto R01: 1945.99
  - netto R02: 2085.69
  - netto R03: 2111.25
  - netto R05: 841.19
  - netto R06: 866.05
  - netto R07: 1806.31
  - conguaglio fiscale sull'ultimo pagamento: R05 0.00
- Fermi: nessuno
- Su dati fittizi:
  - categorie di reddito, ritenuta, conguaglio e dichiarazioni di composizione sono del corpus fittizio (valori fiscali finti)
- Note:
  - avviso proiezione_conguaglio: R01, R02, R03, R06, R07
  - avviso senza_dichiarazione_sostituito: R06

**Conferma della Ragioneria**

- Riuscito:
  - versione 2 confermata (6 rapporti)
- Fermi: nessuno
- Su dati fittizi:
  - la conferma e' una chiamata del percorso: nessun adattatore verso la Ragioneria

**Pagamento eseguito**

- Riuscito:
  - esito pagato 2: 54 righe, valuta 2026-03-27
- Fermi: nessuno
- Su dati fittizi:
  - l'evento di pagamento eseguito e' simulato dal percorso, con valuta uguale alla prevista

**Denuncia**

- Riuscito:
  - R01: 1 quadri, contributi nei quadri 834.53; contributi trattenuti uguali ai dovuti
  - R02: 1 quadri, contributi nei quadri 900.62; contributi trattenuti uguali ai dovuti
  - R03: 2 quadri, contributi nei quadri 879.15; contributi trattenuti uguali ai dovuti
  - R05: 1 quadri, contributi nei quadri 354.67; contributi trattenuti uguali ai dovuti
  - R06: 1 quadri, contributi nei quadri 367.90; contributi trattenuti uguali ai dovuti
  - R07: 1 quadri, contributi nei quadri 768.44; contributi trattenuti uguali ai dovuti
- Fermi: nessuno
- Su dati fittizi:
  - basi, concorsi e contributi del corpus reale; concorsi della performance e del rimborso 730 fittizi

**ListaPosPA**

- Riuscito:
  - R01: E0 2026-03-01/2026-03-31
  - R02: E0 2026-03-01/2026-03-31
  - R03: E0 2026-03-01/2026-03-31, V1 causale 5 2025-12-01/2025-12-31
  - R05: E0 2026-03-01/2026-03-14
  - R06: E0 2026-03-16/2026-03-31
  - R07: E0 2026-03-01/2026-03-31
  - file lista-pos-pa-2026-03.xml: 6 rapporti trasmissibili su 6 pagati (in produzione la fornitura e' un blocco solo; qui contiene i soli rapporti trasmissibili)
- Fermi: nessuno
- Su dati fittizi:
  - ente dichiarante, mittente e codici fiscali dei firmatari di fantasia

**Delega F24EP**

- Riuscito:
  - scadenza 2026-04-16, data di versamento scelta 2026-04-16
  - riga F 100E: debito 160.90, credito 0.00
  - riga Q P201: debito 3604.03, credito 0.00
  - riga Q P607: debito 454.07, credito 0.00
  - riga Q P608: debito 47.21, credito 0.00
  - riga Q P909: debito 38.63, credito 0.00
  - saldo 4304.84
  - delega DELEGA-2026-03 trasmessa il 2026-04-08
- Fermi: nessuno
- Su dati fittizi:
  - mappatura dei codici, catalogo dei codici F24EP, scadenza e festivi del corpus fittizio

**File telematico**

- Riuscito:
  - file f24ep-2026-03.txt: 4 record
- Fermi: nessuno
- Su dati fittizi:
  - dati dell'ente (codice fiscale, denominazione, IBAN di tesoreria) di fantasia

**Ricevute della delega**

- Riuscito:
  - stato della delega: addebitata
- Fermi: nessuno
- Su dati fittizi:
  - le tre ricevute (controlli formali, controllo dei crediti, addebito) sono simulate, tutte positive

**Esito versato**

- Riuscito:
  - esito versato 4: 36 righe, 4304.84 versati il 2026-04-16
  - righe ancora da versare nel mese: 0
- Fermi: nessuno
- Su dati fittizi:
  - l'addebito e' simulato dal percorso, alla data di versamento scelta

### Dicembre 2026 (conguaglio)

**Calcolo**

- Riuscito:
  - R01: 2 importi, lordo 2228.35
  - R02: 2 importi, lordo 2228.35
  - R03: 2 importi, lordo 1824.12
  - R06: 3 importi, lordo 1824.12
  - R07: 3 importi, lordo 2051.69
- Fermi:
  - R04: caso non modellato, part-time, riproporzionamento non modellato (fatto part_time dal 2026-01-01; prassi:immedia:nota:2026-11-06;3)
  - R08 (dirigente): nessun importo; il fatto compenso_mensile registrato dall'Ufficio personale non e' letto da nessuna regola del corpus
  - R09 (segretario): nessun importo; il fatto compenso_mensile registrato dall'Ufficio personale non e' letto da nessuna regola del corpus
  - R10 (sindaco): nessun importo; il fatto compenso_mensile registrato dall'Ufficio personale non e' letto da nessuna regola del corpus
  - R11 (co.co.co.): nessun importo; il fatto compenso_mensile registrato dall'Ufficio personale non e' letto da nessuna regola del corpus
- Su dati fittizi:
  - tabelle e parametri del corpus reale; regole del corpus fittizio per: rimborso_irpef_730
- Note:
  - R05: non in servizio nel mese, nessun importo

**Versione di proposta**

- Riuscito:
  - versione 3: 46 righe di composizione, valuta prevista 2026-12-18, 5 rapporti
  - netto R01: 2013.01
  - netto R02: 2046.51
  - netto R03: 1674.31
  - netto R06: 1626.83
  - netto R07: 1838.79
  - conguaglio fiscale sull'ultimo pagamento: R01 -67.02, R02 -100.52, R03 -53.93, R06 -96.99, R07 -32.48
- Fermi: nessuno
- Su dati fittizi:
  - categorie di reddito, ritenuta, conguaglio e dichiarazioni di composizione sono del corpus fittizio (valori fiscali finti)
- Note:
  - avviso senza_dichiarazione_sostituito: R06

**Conferma della Ragioneria**

- Riuscito:
  - versione 3 confermata (5 rapporti)
- Fermi: nessuno
- Su dati fittizi:
  - la conferma e' una chiamata del percorso: nessun adattatore verso la Ragioneria

**Pagamento eseguito**

- Riuscito:
  - esito pagato 5: 46 righe, valuta 2026-12-18
- Fermi: nessuno
- Su dati fittizi:
  - l'evento di pagamento eseguito e' simulato dal percorso, con valuta uguale alla prevista

**Denuncia**

- Non eseguito in questa prova:
  - con `--denuncia-di-dicembre` gira e non ha fermi nuovi rispetto a marzo; qui non e' eseguita perche' per i cumuli del mese di conguaglio il nucleo ricalcola la denuncia di tutti i mesi dell'anno per ogni rapporto: alcuni secondi, troppi per il test

**ListaPosPA**

- Non eseguito in questa prova:
  - con `--denuncia-di-dicembre` gira e non ha fermi nuovi rispetto a marzo; qui non e' eseguita perche' per i cumuli del mese di conguaglio il nucleo ricalcola la denuncia di tutti i mesi dell'anno per ogni rapporto: alcuni secondi, troppi per il test

**Delega F24EP**

- Riuscito:
  - scadenza 2027-01-18, data di versamento scelta 2027-01-18
- Fermi:
  - R07 (rimborso_irpef_730): Istituto rimborso_irpef_730: il codice 150E vuole l'anno d'imposta e l'importo non lo porta
- Su dati fittizi:
  - mappatura dei codici, catalogo dei codici F24EP, scadenza e festivi del corpus fittizio
- Note:
  - righe costruite ma non trasmissibili: 100E -177.14, P201 3316.16, P607 400.17, P608 87.67, P909 35.54

**File telematico**

- Riuscito: niente
- Fermi:
  - R01, R02, R03, R06, R07: non eseguito, la delega del mese non e' trasmessa
- Su dati fittizi:

**Ricevute della delega**

- Riuscito: niente
- Fermi:
  - R01, R02, R03, R06, R07: non eseguito, la delega del mese non e' trasmessa
- Su dati fittizi:

**Esito versato**

- Riuscito: niente
- Fermi:
  - R01, R02, R03, R06, R07: non eseguito, la delega del mese non e' trasmessa
- Su dati fittizi:

## Difetti del nucleo trovati

1. **Il rimborso 730 non puo' essere insieme nel netto e a credito nella delega.** R07, 2026-12-18: il rimborso 150.00 e' una riga con un solo effetto. Dichiarato a credito F24EP (effetto nessuno sul netto), il netto resta 1838.79 e il lavoratore non lo riceve; dichiarato sul netto, il sostituto non avrebbe il credito da compensare. Servirebbero due righe dallo stesso importo, e la struttura ne ammette una.
2. **Una delega con un debito negativo risulta pronta.** 2026-12: la riga F 100E ha debito -177.14. I conguagli a credito dei lavoratori (ritenuta con segno meno nella composizione) superano le ritenute del mese e la somma per codice va sotto zero; `costruisci_delega` non lo segnala e il serializzatore la rifiuta (File F24EP: modello 1, modulo 1, riga 1: importo a debito: importo non ammesso, Decimal('-177.14')). L'esempio nasce dall'anno fittizio con soli due pagamenti, ma il caso e' raggiungibile.

## Non esercitato dal mese

- La tredicesima non e' un istituto del corpus: il pagamento di dicembre non la contiene, anche se il tabellare annuo del corpus e' per dodici mensilita' piu' la tredicesima.
- Le addizionali regionale e comunale non si calcolano: nessuna regola le produce e il registro non ha il domicilio fiscale. Se un istituto le portasse con 384E o 380E, la delega si fermerebbe per il codice catastale o della regione, che nessun fatto porta (`codice_non_modellato`).
- Il contributo aggiuntivo dell'1% non scatta in nessun quadro del mese (nessun rapporto supera la prima fascia) e non ha una causale nel catalogo: se scattasse, la delega si fermerebbe per mappatura mancante (la ricerca non trova una causale dedicata).
- L'IRAP non e' calcolata; una riga IRAP nella delega la ferma (`irap`: scadenza e riparto non modellati).
- L'ente e' in una sola regione, ma il nucleo non ha un fatto per la regione: l'unico dato territoriale e' la sigla di provincia, che entra nella causale P201.

## File prodotti

- `f24ep-2026-03.txt`
- `lista-pos-pa-2026-03.xml`
