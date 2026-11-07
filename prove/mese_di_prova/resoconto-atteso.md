# Mese di prova: resoconto

> **Dati e corpus fittizi.** Ente, persone, codici fiscali, IBAN e atti sono di fantasia; nessun valore di questo resoconto e' un importo vero. Il percorso gira su un corpus **non reale**: l'unione del corpus reale (`corpus/funzioni-locali-cpdel.toml`, che non cambia) e di un'aggiunta fittizia (`prove/mese_di_prova/corpus_fittizio.toml`, tutti i riferimenti `fittizio:`). Il corpus reale rifiuta i riferimenti fittizi (ADR 0003): per questo l'unione si carica come corpus non reale.

Il resoconto e' generato da `python -m prove.mese_di_prova` e fissato da `tests/test_mese_di_prova.py`: ogni ticket futuro lo cambia nel punto che sblocca.

## Corpus

| Voce | Corpus reale | Aggiunta fittizia | Unione usata |
|---|---:|---:|---:|
| istituti con regola | 28 | 2 | 30 |
| basi imponibili | 4 | 0 | 4 |
| fermi dichiarati | 10 | 0 | 10 |
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

Ente fittizio in una sola regione, con i fatti sull'ente della delega (codice fiscale, denominazione, e-mail, IBAN di tesoreria, sigla di provincia) e l'ultimo pagamento del 2026 al 2026-12-18. Mese: marzo 2026, piu' dicembre 2026 per il conguaglio. Dodici rapporti, ognuno per un caso:

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
| R12 | comparto | operatori | 1 | tempo determinato part-time verticale 50% in sostituzione (tipo impiego 18) |

## Dove arriva ogni rapporto

| Rapporto | Marzo 2026 | Dicembre 2026 |
|---|---|---|
| R01 | completo, fino all'esito versato | si ferma al passo «Delega F24EP»: debito_negativo: Il totale a debito del codice 100E e' negativo |
| R02 | completo, fino all'esito versato | si ferma al passo «Delega F24EP»: debito_negativo: Il totale a debito del codice 100E e' negativo |
| R03 | completo, fino all'esito versato | si ferma al passo «Delega F24EP»: debito_negativo: Il totale a debito del codice 100E e' negativo |
| R04 | si ferma al passo «ListaPosPA»: bozza non trasmissibile | si ferma al passo «Delega F24EP»: debito_negativo: Il totale a debito del codice 100E e' negativo |
| R05 | completo, fino all'esito versato | fuori servizio |
| R06 | completo, fino all'esito versato | si ferma al passo «Delega F24EP»: debito_negativo: Il totale a debito del codice 100E e' negativo |
| R07 | completo, fino all'esito versato | si ferma al passo «Delega F24EP»: debito_negativo: Il totale a debito del codice 100E e' negativo |
| R08 | si ferma al passo «Calcolo»: regime del titolo assente nel corpus | si ferma al passo «Calcolo»: regime del titolo assente nel corpus |
| R09 | si ferma al passo «Calcolo»: regime del titolo assente nel corpus | si ferma al passo «Calcolo»: regime del titolo assente nel corpus |
| R10 | si ferma al passo «Calcolo»: regime del titolo assente nel corpus | si ferma al passo «Calcolo»: regime del titolo assente nel corpus |
| R11 | si ferma al passo «Calcolo»: regime del titolo assente nel corpus | si ferma al passo «Calcolo»: regime del titolo assente nel corpus |
| R12 | si ferma al passo «ListaPosPA»: bozza non trasmissibile | si ferma al passo «Delega F24EP»: debito_negativo: Il totale a debito del codice 100E e' negativo |

## Cosa manca per un mese completo

I fermi del mese, raggruppati per causa. L'ordine e' per quanti rapporti bloccano e poi per quanti passi del percorso (calcolo, versione, conferma, pagamento, denuncia, ListaPosPA, delega, file, ricevute, esito versato) restano chiusi, sommati su marzo e dicembre.

1. **debito_negativo: Il totale a debito del codice 100E e' negativo**: 7 rapporti bloccati, 28 passi, al passo «Delega F24EP», in dicembre. Casi: R01, R02, R03, R04, R06, R07, R12.
2. **regime del titolo assente nel corpus**: 4 rapporti bloccati, 80 passi, al passo «Calcolo», in marzo e dicembre. Casi: R08 (dirigente), R09 (segretario), R10 (sindaco), R11 (co.co.co.).
3. **bozza non trasmissibile**: 2 rapporti bloccati, 10 passi, al passo «ListaPosPA», in marzo. Casi: R04, R12.

## Passaggi manuali

| Categoria | Avvio | Preparazione di febbraio | Marzo | Dicembre |
|---|---:|---:|---:|---:|
| Fatti di avvio, una tantum (anagrafica, assunzioni, inquadramento) | 133 | 0 | 13 | 0 |
| Fatti ricorrenti del mese (atti, variazioni, cessazioni, 730) | 0 | 0 | 16 | 1 |
| Conferme della Ragioneria | 0 | 1 | 1 | 1 |
| Scelte (valuta prevista, data di versamento, ultimo pagamento) | 0 | 1 | 2 | 3 |
| Eventi che oggi nessun adattatore porta (pagamento, ricevute, versamento) | 0 | 1 | 5 | 1 |
| Comandi di avvio (non sono dati: emissione, produzione dei file, trasmissione) | 0 | 1 | 3 | 1 |
| **Totale senza i comandi** | **133** | **3** | **37** | **6** |

La preparazione di febbraio e' il pagamento che precede il mese, scritto solo perche' l'arretrato di R02 e' una differenza rispetto a un esito pagato: non fa parte del mese e non e' nel totale di marzo.

Fatti di avvio per soggetto: R01 14, R02 14, R03 14, R04 16, R05 14, R07 14, R08 6, R09 6, R10 6, R11 6, R12 18, ente 5.
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

- [ricorrente] 1 x persona P07: esito 730-4
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
  - 146 fatti di avvio (ente, persone, rapporti, assunzione di R06) registrati nel registro
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
  - R04: 2 importi, lordo 1048.14
  - R05: 2 importi, lordo 946.94
  - R06: 3 importi, lordo 982.22
  - R07: 2 importi, lordo 2051.69
  - R12: 3 importi, lordo 873.45
- Fermi:
  - R08 (dirigente): nessun importo; il fatto compenso_mensile registrato dall'Ufficio personale non e' letto da nessuna regola del corpus
  - R09 (segretario): nessun importo; il fatto compenso_mensile registrato dall'Ufficio personale non e' letto da nessuna regola del corpus
  - R10 (sindaco): nessun importo; il fatto compenso_mensile registrato dall'Ufficio personale non e' letto da nessuna regola del corpus
  - R11 (co.co.co.): nessun importo; il fatto compenso_mensile registrato dall'Ufficio personale non e' letto da nessuna regola del corpus
- Su dati fittizi:
  - tabelle e parametri del corpus reale; regole del corpus fittizio per: performance

**Versione di proposta**

- Riuscito:
  - versione 2: 70 righe di composizione, valuta prevista 2026-03-27, 8 rapporti
  - netto R01: 1945.99
  - netto R02: 2085.69
  - netto R03: 2111.25
  - netto R04: 920.27
  - netto R05: 841.19
  - netto R06: 866.05
  - netto R07: 1806.31
  - netto R12: 775.85
  - conguaglio fiscale sull'ultimo pagamento: R05 0.00
- Fermi: nessuno
- Su dati fittizi:
  - categorie di reddito, ritenuta, conguaglio e dichiarazioni di composizione sono del corpus fittizio (valori fiscali finti)
- Note:
  - avviso proiezione_conguaglio: R01, R02, R03, R04, R06, R07, R12
  - avviso senza_dichiarazione_sostituito: R04, R06, R12

**Conferma della Ragioneria**

- Riuscito:
  - versione 2 confermata (8 rapporti)
- Fermi: nessuno
- Su dati fittizi:
  - la conferma e' una chiamata del percorso: nessun adattatore verso la Ragioneria

**Pagamento eseguito**

- Riuscito:
  - esito pagato 2: 70 righe, valuta 2026-03-27
- Fermi: nessuno
- Su dati fittizi:
  - l'evento di pagamento eseguito e' simulato dal percorso, con valuta uguale alla prevista

**Denuncia**

- Riuscito:
  - R01: 1 quadri, contributi nei quadri 834.53; contributi trattenuti uguali ai dovuti
  - R02: 1 quadri, contributi nei quadri 900.62; contributi trattenuti uguali ai dovuti
  - R03: 2 quadri, contributi nei quadri 879.15; contributi trattenuti uguali ai dovuti
  - R04: 1 quadri, contributi nei quadri 392.70; contributi trattenuti uguali ai dovuti
  - R05: 1 quadri, contributi nei quadri 354.67; contributi trattenuti uguali ai dovuti
  - R06: 1 quadri, contributi nei quadri 367.90; contributi trattenuti uguali ai dovuti
  - R07: 1 quadri, contributi nei quadri 768.44; contributi trattenuti uguali ai dovuti
  - R12: 1 quadri, contributi nei quadri 327.25; contributi trattenuti uguali ai dovuti
- Fermi: nessuno
- Su dati fittizi:
  - basi, concorsi e contributi del corpus reale; concorsi della performance e del rimborso 730 fittizi

**ListaPosPA**

- Riuscito:
  - R01: E0 2026-03-01/2026-03-31
  - R02: E0 2026-03-01/2026-03-31
  - R03: E0 2026-03-01/2026-03-31, V1 causale 5 2025-12-01/2025-12-31
  - R04: E0 2026-03-01/2026-03-31 (non trasmissibile)
  - R05: E0 2026-03-01/2026-03-14
  - R06: E0 2026-03-16/2026-03-31
  - R07: E0 2026-03-01/2026-03-31
  - R12: E0 2026-03-01/2026-03-31 (non trasmissibile)
  - R12: DenunciaIndividuale 71 2/V/A, imponibile 873, contributo 14.06, PercPartTime 5000, PercPartTimeMese 5000, 5 settimane (1 D), 11 giorni lavorati su 31
  - DenunciaAziendale 2026-03: NumDenIndiv 1, TotaleADebito 14
  - controllo di completezza della DenunciaIndividuale: nessuna assenza
  - file lista-pos-pa-2026-03.xml: 6 rapporti trasmissibili su 8 pagati (in produzione la fornitura e' un blocco solo; qui contiene i soli rapporti trasmissibili)
- Fermi:
  - R04: Part-time verticale dal 2026-03-01: percentuale mensile (PercPartTime) non determinata dal documento tecnico INPS per un periodo lavorato in parte (docs/research/part-time-lista-pos-pa.md): bozza non trasmissibile
  - R12: Part-time verticale dal 2026-03-01: percentuale mensile (PercPartTime) non determinata dal documento tecnico INPS per un periodo lavorato in parte (docs/research/part-time-lista-pos-pa.md): bozza non trasmissibile
- Su dati fittizi:
  - mappature della DenunciaIndividuale e calendario dei festivi: le prime sono del corpus reale, il calendario e' fittizio
  - ente dichiarante, mittente e codici fiscali dei firmatari di fantasia

**Delega F24EP**

- Riuscito:
  - scadenza 2026-04-16, data di versamento scelta 2026-04-16
  - riga F 100E: debito 171.65, credito 0.00
  - riga Q P201: debito 4231.43, credito 0.00
  - riga Q P607: debito 504.55, credito 0.00
  - riga Q P608: debito 89.28, credito 0.00
  - riga Q P909: debito 45.36, credito 0.00
  - saldo 5042.27
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
  - esito versato 4: 47 righe, 5042.27 versati il 2026-04-16
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
  - R04: 2 importi, lordo 1048.14
  - R06: 3 importi, lordo 1824.12
  - R07: 3 importi, lordo 2051.69
  - R07: rimborso del 730-4: 150.00, anno dei redditi dichiarati 2025
  - R12: 3 importi, lordo 873.45
- Fermi:
  - R08 (dirigente): nessun importo; il fatto compenso_mensile registrato dall'Ufficio personale non e' letto da nessuna regola del corpus
  - R09 (segretario): nessun importo; il fatto compenso_mensile registrato dall'Ufficio personale non e' letto da nessuna regola del corpus
  - R10 (sindaco): nessun importo; il fatto compenso_mensile registrato dall'Ufficio personale non e' letto da nessuna regola del corpus
  - R11 (co.co.co.): nessun importo; il fatto compenso_mensile registrato dall'Ufficio personale non e' letto da nessuna regola del corpus
- Su dati fittizi:
  - tabelle e parametri del corpus reale
- Note:
  - R05: non in servizio nel mese, nessun importo

**Versione di proposta**

- Riuscito:
  - versione 3: 64 righe di composizione, valuta prevista 2026-12-18, 7 rapporti
  - netto R01: 2013.01
  - netto R02: 2046.51
  - netto R03: 1674.31
  - netto R04: 941.77
  - netto R06: 1626.83
  - netto R07: 1988.79
  - netto R12: 775.85
  - conguaglio fiscale sull'ultimo pagamento: R01 -67.02, R02 -100.52, R03 -53.93, R04 -21.50, R06 -96.99, R07 -32.48, R12 0.00
- Fermi: nessuno
- Su dati fittizi:
  - categorie di reddito, ritenuta, conguaglio e dichiarazioni di composizione sono del corpus fittizio (valori fiscali finti)
- Note:
  - avviso senza_dichiarazione_sostituito: R04, R06, R12

**Conferma della Ragioneria**

- Riuscito:
  - versione 3 confermata (7 rapporti)
- Fermi: nessuno
- Su dati fittizi:
  - la conferma e' una chiamata del percorso: nessun adattatore verso la Ragioneria

**Pagamento eseguito**

- Riuscito:
  - esito pagato 5: 64 righe, valuta 2026-12-18
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
  - R01, R02, R03, R04, R06, R07, R12: Il totale a debito del codice 100E e' negativo (-187.89; sezione F, riferimenti 0012/2026): i conguagli a credito superano le ritenute della delega. Il recupero dell'eccedenza non ha ancora una fonte, la delega non si trasmette
- Su dati fittizi:
  - mappatura dei codici, catalogo dei codici F24EP, scadenza e festivi del corpus fittizio
- Note:
  - righe costruite ma non trasmissibili: 100E -187.89, 150E -150.00, P201 3943.56, P607 450.65, P608 129.74, P909 42.27

**File telematico**

- Riuscito: niente
- Fermi:
  - R01, R02, R03, R04, R06, R07, R12: non eseguito, la delega del mese non e' trasmessa
- Su dati fittizi:

**Ricevute della delega**

- Riuscito: niente
- Fermi:
  - R01, R02, R03, R04, R06, R07, R12: non eseguito, la delega del mese non e' trasmessa
- Su dati fittizi:

**Esito versato**

- Riuscito: niente
- Fermi:
  - R01, R02, R03, R04, R06, R07, R12: non eseguito, la delega del mese non e' trasmessa
- Su dati fittizi:

## Difetti del nucleo trovati

Nessuno trovato.

## Non esercitato dal mese

- La tredicesima non e' un istituto del corpus: il pagamento di dicembre non la contiene, anche se il tabellare annuo del corpus e' per dodici mensilita' piu' la tredicesima.
- Le addizionali regionale e comunale non si calcolano: nessuna regola le produce e il registro non ha il domicilio fiscale. Se un istituto le portasse con 384E o 380E, la delega si fermerebbe per il codice catastale o della regione, che nessun fatto porta (`codice_non_modellato`).
- Il contributo aggiuntivo dell'1% non scatta in nessun quadro del mese (nessun rapporto supera la prima fascia) e non ha una causale nel catalogo: se scattasse, la delega si fermerebbe per mappatura mancante (la ricerca non trova una causale dedicata).
- L'IRAP non e' calcolata; una riga IRAP nella delega la ferma (`irap`: scadenza e riparto non modellati).
- L'ente e' in una sola regione, ma il nucleo non ha un fatto per la regione: l'unico dato territoriale e' la sigla di provincia, che entra nella causale P201.

## File prodotti

- `f24ep-2026-03.txt`
- `lista-pos-pa-2026-03.xml`
