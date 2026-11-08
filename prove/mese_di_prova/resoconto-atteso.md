# Mese di prova: resoconto

> **Dati e corpus fittizi.** Ente, persone, codici fiscali, IBAN e atti sono di fantasia; nessun valore di questo resoconto e' un importo vero. Il percorso gira su un corpus **non reale**: l'unione del corpus reale (`corpus/funzioni-locali-cpdel.toml`, che non cambia) e di un'aggiunta fittizia (`prove/mese_di_prova/corpus_fittizio.toml`, tutti i riferimenti `fittizio:`). Il corpus reale rifiuta i riferimenti fittizi (ADR 0003): per questo l'unione si carica come corpus non reale.

Il resoconto e' generato da `python -m prove.mese_di_prova` e fissato da `tests/test_mese_di_prova.py`: ogni ticket futuro lo cambia nel punto che sblocca.

## Corpus

| Voce | Corpus reale | Aggiunta fittizia | Unione usata |
|---|---:|---:|---:|
| istituti con regola | 39 | 2 | 41 |
| basi imponibili | 6 | 0 | 6 |
| fermi dichiarati | 24 | 0 | 24 |
| categorie di reddito | 3 | 0 | 3 |
| regole di ritenuta | 2 | 0 | 2 |
| regole di conguaglio | 2 | 0 | 2 |
| dichiarazioni di pagamento fisiologico | 0 | 1 | 1 |
| dichiarazioni di composizione | 0 | 48 | 48 |
| mappature verso codici esterni | 0 | 20 | 20 |
| codici nel catalogo F24EP | 0 | 14 | 14 |
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
| R08 | dirigente | dirigente | 1 | dirigente a tempo pieno, tabellare su 13 mensilita' e posizione da atto |
| R09 | segretario | segretario | 1 | segretario comunale in fascia B, posizione da atto |
| R10 | sindaco | - | - | sindaco, lavoratore autonomo iscritto alla gestione separata senza altra cassa: indennita' e quota dell'art. 86 |
| R11 | co.co.co. | - | - | collaboratore coordinato e continuativo, senza altra cassa: rata di marzo attestata, rata di dicembre no |
| R12 | comparto | operatori | 1 | tempo determinato part-time verticale 50% in sostituzione (tipo impiego 18) |

## Dove arriva ogni rapporto

| Rapporto | Marzo 2026 | Dicembre 2026 |
|---|---|---|
| R01 | completo, fino all'esito versato | completo, fino al pagamento e alla ListaPosPA |
| R02 | completo, fino all'esito versato | completo, fino al pagamento e alla ListaPosPA |
| R03 | completo, fino all'esito versato | completo, fino al pagamento e alla ListaPosPA |
| R04 | si ferma al passo «ListaPosPA»: bozza non trasmissibile | completo, fino al pagamento e alla ListaPosPA |
| R05 | completo, fino all'esito versato | fuori servizio |
| R06 | completo, fino all'esito versato | completo, fino al pagamento e alla ListaPosPA |
| R07 | completo, fino all'esito versato | completo, fino al pagamento e alla ListaPosPA |
| R08 | si ferma al passo «ListaPosPA»: dato mancante qualifica | si ferma al passo «Versione di proposta»: conguaglio annuo di contributo_aggiuntivo in 2026-12 |
| R09 | si ferma al passo «ListaPosPA»: dato mancante qualifica | si ferma al passo «Versione di proposta»: conguaglio annuo di contributo_aggiuntivo in 2026-12 |
| R10 | si ferma al passo «Lista collaboratori»: tracciato della lista collaboratori: elementi e codici non letti sul testo ufficiale e non dichiarati nel corpus: bozza non trasmissibile | completo, fino al pagamento e alla ListaPosPA |
| R11 | si ferma al passo «Lista collaboratori»: tracciato della lista collaboratori: elementi e codici non letti sul testo ufficiale e non dichiarati nel corpus: bozza non trasmissibile | si ferma al passo «Versione di proposta»: manca il fatto attestazione_prestazione per <data>: l'importo resta calcolato ma non entra in una versione di proposta |
| R12 | si ferma al passo «ListaPosPA»: bozza non trasmissibile | completo, fino al pagamento e alla ListaPosPA |

## Cosa manca per un mese completo

I fermi del mese, raggruppati per causa. L'ordine e' per quanti rapporti bloccano e poi per quanti passi del percorso (calcolo, versione, conferma, pagamento, prospetto paga, denuncia, ListaPosPA, lista collaboratori, delega, file, ricevute, esito versato) restano chiusi, sommati su marzo e dicembre.

1. **prospetto paga: dato mancante posizione**: 3 rapporti bloccati, 3 passi, al passo «Prospetto paga», in marzo. Casi: R08, R09, R11.
2. **conguaglio annuo di contributo_aggiuntivo in 2026-12**: 2 rapporti bloccati, 22 passi, al passo «Versione di proposta», in dicembre. Casi: R08, R09.
3. **bozza non trasmissibile**: 2 rapporti bloccati, 12 passi, al passo «ListaPosPA», in marzo. Casi: R04, R12.
4. **dato mancante contratto**: 2 rapporti bloccati, 12 passi, al passo «ListaPosPA», in marzo. Casi: R08, R09.
5. **dato mancante qualifica**: 2 rapporti bloccati, 12 passi, al passo «ListaPosPA», in marzo. Casi: R08, R09.
6. **tracciato della lista collaboratori: elementi e codici non letti sul testo ufficiale e non dichiarati nel corpus: bozza non trasmissibile**: 2 rapporti bloccati, 10 passi, al passo «Lista collaboratori», in marzo. Casi: R10, R11.
7. **manca il fatto attestazione_prestazione per <data>: l'importo resta calcolato ma non entra in una versione di proposta**: 1 rapporto bloccato, 11 passi, al passo «Versione di proposta», in dicembre. Casi: R11.

## Passaggi manuali

| Categoria | Avvio | Preparazione di febbraio | Marzo | Dicembre |
|---|---:|---:|---:|---:|
| Fatti di avvio, una tantum (anagrafica, assunzioni, inquadramento) | 166 | 0 | 14 | 0 |
| Fatti ricorrenti del mese (atti, variazioni, cessazioni, 730) | 0 | 0 | 17 | 1 |
| Conferme della Ragioneria | 0 | 1 | 1 | 1 |
| Scelte (valuta prevista, data di versamento, ultimo pagamento) | 0 | 1 | 2 | 3 |
| Eventi che oggi nessun adattatore porta (pagamento, ricevute, versamento) | 0 | 1 | 14 | 13 |
| Comandi di avvio (non sono dati: emissione, produzione dei file, trasmissione) | 0 | 1 | 3 | 2 |
| **Totale senza i comandi** | **166** | **3** | **48** | **18** |

La preparazione di febbraio e' il pagamento che precede il mese, scritto solo perche' l'arretrato di R02 e' una differenza rispetto a un esito pagato: non fa parte del mese e non e' nel totale di marzo.

Fatti di avvio per soggetto: R01 16, R02 15, R03 15, R04 17, R05 15, R07 15, R08 14, R09 15, R10 10, R11 9, R12 19, ente 6.
Assunzione di marzo (avvio di un rapporto nuovo): R06 14.

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
- [ricorrente] 1 x rapporto R11: attestazione_prestazione
- [conferma] 1 x conferma della versione 2
- [scelta] 1 x ente: data di versamento dei pagamenti di 2026-03
- [scelta] 1 x valuta prevista della versione (2026-03-27)
- [evento] 9 x messa a disposizione del prospetto paga
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
- [evento] 8 x messa a disposizione del prospetto paga
- [evento] 1 x pagamento eseguito della versione 3
- [evento] 1 x ricevuta della delega: addebito
- [evento] 1 x ricevuta della delega: controlli_formali
- [evento] 1 x ricevuta della delega: controllo_crediti
- [evento] 1 x versamento eseguito della delega
- [comando] 1 x emissione della versione di proposta (2026-12)
- [comando] 1 x trasmissione della delega (2026-12)

Nota: la cessazione di R05 costa 13 scritture a mano. Il nucleo non ha un fatto di cessazione: i fatti sono immutabili e il servizio di un rapporto finisce solo se si annullano i sei fatti di inquadramento aperti e si riscrivono con una fine (piu' il codice di cessazione).

## Il percorso, passo per passo

### Marzo 2026

**Fatti**

- Riuscito:
  - 180 fatti di avvio (ente, persone, rapporti, assunzione di R06) registrati nel registro
  - 17 fatti del mese: performance, progressione, cessazione
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
  - R08: 3 importi, lordo 5385.06
  - R09: 3 importi, lordo 4769.68
  - R10: 2 importi, lordo 3000.00
  - R11: 1 importi, lordo 1500.00
  - R12: 3 importi, lordo 873.45
- Fermi: nessuno
- Su dati fittizi:
  - tabelle e parametri del corpus reale; regole del corpus fittizio per: performance

**Versione di proposta**

- Riuscito:
  - versione 2: 108 righe di composizione, valuta prevista 2026-03-27, 12 rapporti
  - netto R01: 1795.79
  - netto R02: 1911.00
  - netto R03: 1930.49
  - netto R04: 716.89
  - netto R05: 841.19
  - netto R06: 667.37
  - netto R07: 1692.60
  - netto R08: 3325.40
  - netto R09: 3022.72
  - netto R10: 2243.33
  - netto R11: 1020.13
  - netto R12: 593.44
  - conguaglio fiscale sull'ultimo pagamento: R05 -30.55
- Fermi: nessuno
- Su dati fittizi:
  - categorie di reddito, ritenuta, conguaglio e dichiarazioni di composizione sono del corpus fittizio (valori fiscali finti)
- Note:
  - avviso acconto_senza_base: R02, R03, R04, R06, R07, R08, R09, R10, R11, R12
  - avviso proiezione_conguaglio: R01, R02, R03, R04, R06, R07, R08, R09, R10, R11, R12
  - avviso senza_dichiarazione_sostituito: R04, R06, R10, R11, R12

**Conferma della Ragioneria**

- Riuscito:
  - versione 2 confermata (12 rapporti)
- Fermi: nessuno
- Su dati fittizi:
  - la conferma e' una chiamata del percorso: nessun adattatore verso la Ragioneria

**Pagamento eseguito**

- Riuscito:
  - esito pagato 2: 108 righe, valuta 2026-03-27
- Fermi: nessuno
- Su dati fittizi:
  - l'evento di pagamento eseguito e' simulato dal percorso, con valuta uguale alla prevista

**Prospetto paga**

- Riuscito:
  - R01: prospetto del pagamento del 2026-03-27 (esito 2), posizione 0FZEQF, 7 righe sul netto, netto 1795.79, 3 senza effetto sul netto; consegnato, esito dichiarato 3
  - R02: prospetto del pagamento del 2026-03-27 (esito 2), posizione 0FZEQF, 10 righe sul netto, netto 1911.00, 3 senza effetto sul netto; consegnato, esito dichiarato 4
  - R03: prospetto del pagamento del 2026-03-27 (esito 2), posizione 0OEESP, 7 righe sul netto, netto 1930.49, 3 senza effetto sul netto; consegnato, esito dichiarato 5
  - R04: prospetto del pagamento del 2026-03-27 (esito 2), posizione 0OP000, 6 righe sul netto, netto 716.89, 3 senza effetto sul netto; consegnato, esito dichiarato 6
  - R05: prospetto del pagamento del 2026-03-27 (esito 2), posizione 0IR000, 7 righe sul netto, netto 841.19, 3 senza effetto sul netto; consegnato, esito dichiarato 7
  - R06: prospetto del pagamento del 2026-03-27 (esito 2), posizione 0OEESP, 6 righe sul netto, netto 667.37, 3 senza effetto sul netto; consegnato, esito dichiarato 8
  - R07: prospetto del pagamento del 2026-03-27 (esito 2), posizione 0IR000, 6 righe sul netto, netto 1692.60, 3 senza effetto sul netto; consegnato, esito dichiarato 9
  - R08: prospetto del pagamento del 2026-03-27 (esito 2), posizione -, 7 righe sul netto, netto 3325.40, 3 senza effetto sul netto
  - R09: prospetto del pagamento del 2026-03-27 (esito 2), posizione -, 7 righe sul netto, netto 3022.72, 3 senza effetto sul netto
  - R10: prospetto del pagamento del 2026-03-27 (esito 2), posizione sindaco, 2 righe sul netto, netto 2243.33, 2 senza effetto sul netto; consegnato, esito dichiarato 10
  - R11: prospetto del pagamento del 2026-03-27 (esito 2), posizione -, 3 righe sul netto, netto 1020.13, 2 senza effetto sul netto
  - R12: prospetto del pagamento del 2026-03-27 (esito 2), posizione 0OP000, 6 righe sul netto, netto 593.44, 3 senza effetto sul netto; consegnato, esito dichiarato 11
- Fermi:
  - R08: dato mancante posizione
  - R09: dato mancante posizione
  - R11: dato mancante posizione
- Su dati fittizi:
  - la messa a disposizione e' simulata dal percorso (giorno dopo il pagamento, riferimento di canale di fantasia); la posizione di sindaco e collaboratori e la composizione sono dichiarate dal corpus fittizio
- Note:
  - avviso contratto_collettivo: R01, R02, R03, R04, R05, R06, R07, R08, R09, R10, R11, R12

**Denuncia**

- Riuscito:
  - R01: 1 quadri, contributi nei quadri 834.53; contributi trattenuti uguali ai dovuti
  - R02: 1 quadri, contributi nei quadri 900.62; contributi trattenuti uguali ai dovuti
  - R03: 2 quadri, contributi nei quadri 879.15; contributi trattenuti uguali ai dovuti
  - R04: 1 quadri, contributi nei quadri 392.70; contributi trattenuti uguali ai dovuti
  - R05: 1 quadri, contributi nei quadri 354.67; contributi trattenuti uguali ai dovuti
  - R06: 1 quadri, contributi nei quadri 367.90; contributi trattenuti uguali ai dovuti
  - R07: 1 quadri, contributi nei quadri 768.44; contributi trattenuti uguali ai dovuti
  - R08: 1 quadri, contributi nei quadri 2021.01; contributi trattenuti uguali ai dovuti
  - R09: 1 quadri, contributi nei quadri 1790.06; contributi trattenuti uguali ai dovuti
  - R10: contributi trattenuti uguali ai dovuti
  - R11: contributi trattenuti uguali ai dovuti
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
  - R08: E0 2026-03-01/2026-03-31 (non trasmissibile)
  - R09: E0 2026-03-01/2026-03-31 (non trasmissibile)
  - R12: E0 2026-03-01/2026-03-31 (non trasmissibile)
  - R12: DenunciaIndividuale 71 2/V/A, imponibile 873, contributo 14.06, PercPartTime 5000, PercPartTimeMese 5000, 5 settimane (1 D), 11 giorni lavorati su 31
  - DenunciaAziendale 2026-03: NumDenIndiv 1, TotaleADebito 14
  - controllo di completezza della DenunciaIndividuale: nessuna assenza
  - file lista-pos-pa-2026-03.xml: 6 rapporti trasmissibili su 10 della ListaPosPA (in produzione la fornitura e' un blocco solo; qui contiene i soli rapporti trasmissibili)
- Fermi:
  - R04: Part-time verticale dal 2026-03-01: percentuale mensile (PercPartTime) non determinata dal documento tecnico INPS per un periodo lavorato in parte (docs/research/part-time-lista-pos-pa.md): bozza non trasmissibile
  - R08: contratto (periodo 2026-03-01/2026-03-31)
  - R08: qualifica (periodo 2026-03-01/2026-03-31)
  - R09: contratto (periodo 2026-03-01/2026-03-31)
  - R09: qualifica (periodo 2026-03-01/2026-03-31)
  - R12: Part-time verticale dal 2026-03-01: percentuale mensile (PercPartTime) non determinata dal documento tecnico INPS per un periodo lavorato in parte (docs/research/part-time-lista-pos-pa.md): bozza non trasmissibile
- Su dati fittizi:
  - mappature della DenunciaIndividuale e calendario dei festivi: le prime sono del corpus reale, il calendario e' fittizio
  - ente dichiarante, mittente e codici fiscali dei firmatari di fantasia
- Note:
  - rapporti che il regime assegna alla ListaPosPA: R01, R02, R03, R04, R05, R06, R07, R08, R09, R12

**Lista collaboratori**

- Riuscito:
  - R10: mese di erogazione 2026-03, 1 righe: quota forfettaria 528.51 a carico dell'ente (non trasmissibile)
  - R11: mese di erogazione 2026-03, 1 righe: imponibile 1500.00, contributo 525.45 (collaboratore 175.15, ente 350.30) (non trasmissibile)
- Fermi:
  - R10: tracciato della lista collaboratori: elementi e codici non letti sul testo ufficiale e non dichiarati nel corpus: bozza non trasmissibile
  - R11: tracciato della lista collaboratori: elementi e codici non letti sul testo ufficiale e non dichiarati nel corpus: bozza non trasmissibile
- Su dati fittizi:
  - nessun dato fittizio oltre ai rapporti: il tracciato della lista collaboratori non e' dichiarato
- Note:
  - rapporti che il regime assegna alla lista collaboratori: R10, R11

**Delega F24EP**

- Riuscito:
  - scadenza 2026-04-16, data di versamento scelta 2026-04-16
  - riga F 100E: debito 5095.01, credito 0.00
  - riga R 380E: debito 2332.35, credito 0.00
  - riga S 385E: debito 3.30, credito 0.00
  - riga Q P201: debito 7554.80, credito 0.00
  - riga Q P607: debito 504.55, credito 0.00
  - riga Q P608: debito 584.83, credito 0.00
  - riga Q P909: debito 80.90, credito 0.00
  - riga Q ZGS1: debito 1053.96, credito 0.00
  - saldo 17209.70
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
  - esito versato 13: 77 righe, 17209.70 versati il 2026-04-16
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
  - R08: 3 importi, lordo 5385.06
  - R09: 3 importi, lordo 4769.68
  - R10: 2 importi, lordo 3000.00
  - R11: 1 importi, lordo 1500.00
  - R12: 3 importi, lordo 873.45
- Fermi: nessuno
- Su dati fittizi:
  - tabelle e parametri del corpus reale
- Note:
  - R05: non in servizio nel mese, nessun importo

**Versione di proposta**

- Riuscito:
  - versione 3: 77 righe di composizione, valuta prevista 2026-12-18, 8 rapporti
  - netto R01: 2163.21
  - netto R02: 2334.91
  - netto R03: 1855.07
  - netto R04: 716.88
  - netto R06: 1239.43
  - netto R07: 2102.50
  - netto R10: 2376.67
  - netto R12: 593.44
  - conguaglio fiscale sull'ultimo pagamento: R01 -360.82, R02 -535.82, R03 -382.95, R04 0.01, R06 0.00, R07 -259.90, R10 -133.34, R12 0.00
- Fermi:
  - R08: caso non modellato, conguaglio annuo di contributo_aggiuntivo in 2026-12 (già esposto nel periodo 2026-03-01/2026-03-31)
  - R09: caso non modellato, conguaglio annuo di contributo_aggiuntivo in 2026-12 (già esposto nel periodo 2026-03-01/2026-03-31)
  - R11: manca il fatto attestazione_prestazione per 2026-12-10/2026-12-10: l'importo resta calcolato ma non entra in una versione di proposta (prassi:immedia:nota:2026-11-07;10)
- Su dati fittizi:
  - categorie di reddito, ritenuta, conguaglio e dichiarazioni di composizione sono del corpus fittizio (valori fiscali finti)
- Note:
  - avviso persona_assente_dall_ultimo_pagamento: R11
  - avviso senza_dichiarazione_sostituito: R04, R06, R10, R12
  - avviso tempo_determinato_sotto_soglia: R12
  - escluso compenso_collaborazione di R11: manca il fatto attestazione_prestazione per 2026-12-10/2026-12-10: l'importo resta calcolato ma non entra in una versione di proposta (prassi:immedia:nota:2026-11-07;10)

**Conferma della Ragioneria**

- Riuscito:
  - versione 3 confermata (8 rapporti)
- Fermi: nessuno
- Su dati fittizi:
  - la conferma e' una chiamata del percorso: nessun adattatore verso la Ragioneria

**Pagamento eseguito**

- Riuscito:
  - esito pagato 14: 77 righe, valuta 2026-12-18
- Fermi: nessuno
- Su dati fittizi:
  - l'evento di pagamento eseguito e' simulato dal percorso, con valuta uguale alla prevista

**Prospetto paga**

- Riuscito:
  - R01: prospetto del pagamento del 2026-12-18 (esito 14), posizione 0FZEQF, 8 righe sul netto, netto 2163.21, 3 senza effetto sul netto; consegnato, esito dichiarato 15
  - R02: prospetto del pagamento del 2026-12-18 (esito 14), posizione 0FZEQF, 7 righe sul netto, netto 2334.91, 3 senza effetto sul netto; consegnato, esito dichiarato 16
  - R03: prospetto del pagamento del 2026-12-18 (esito 14), posizione 0OEESP, 7 righe sul netto, netto 1855.07, 3 senza effetto sul netto; consegnato, esito dichiarato 17
  - R04: prospetto del pagamento del 2026-12-18 (esito 14), posizione 0OP000, 7 righe sul netto, netto 716.88, 3 senza effetto sul netto; consegnato, esito dichiarato 18
  - R06: prospetto del pagamento del 2026-12-18 (esito 14), posizione 0OEESP, 7 righe sul netto, netto 1239.43, 3 senza effetto sul netto; consegnato, esito dichiarato 19
  - R07: prospetto del pagamento del 2026-12-18 (esito 14), posizione 0IR000, 8 righe sul netto, netto 2102.50, 3 senza effetto sul netto; consegnato, esito dichiarato 20
  - R10: prospetto del pagamento del 2026-12-18 (esito 14), posizione sindaco, 3 righe sul netto, netto 2376.67, 2 senza effetto sul netto; consegnato, esito dichiarato 21
  - R12: prospetto del pagamento del 2026-12-18 (esito 14), posizione 0OP000, 7 righe sul netto, netto 593.44, 3 senza effetto sul netto; consegnato, esito dichiarato 22
- Fermi: nessuno
- Su dati fittizi:
  - la messa a disposizione e' simulata dal percorso (giorno dopo il pagamento, riferimento di canale di fantasia); la posizione di sindaco e collaboratori e la composizione sono dichiarate dal corpus fittizio
- Note:
  - avviso contratto_collettivo: R01, R02, R03, R04, R06, R07, R10, R12

**Denuncia**

- Non eseguito in questa prova:
  - con `--denuncia-di-dicembre` gira e non ha fermi nuovi rispetto a marzo; qui non e' eseguita perche' per i cumuli del mese di conguaglio il nucleo ricalcola la denuncia di tutti i mesi dell'anno per ogni rapporto: alcuni secondi, troppi per il test

**ListaPosPA**

- Non eseguito in questa prova:
  - con `--denuncia-di-dicembre` gira e non ha fermi nuovi rispetto a marzo; qui non e' eseguita perche' per i cumuli del mese di conguaglio il nucleo ricalcola la denuncia di tutti i mesi dell'anno per ogni rapporto: alcuni secondi, troppi per il test

**Delega F24EP**

- Riuscito:
  - scadenza 2027-01-18, data di versamento scelta 2027-01-18
  - riga F 100E: debito 500.37, credito 0.00
  - riga F 150E: debito 0.00, credito 150.00
  - riga R 380E: debito 1281.64, credito 0.00
  - riga S 161E: debito 0.00, credito 3.30
  - riga Q P201: debito 3943.56, credito 0.00
  - riga Q P607: debito 450.65, credito 0.00
  - riga Q P608: debito 129.74, credito 0.00
  - riga Q P909: debito 42.27, credito 0.00
  - riga Q ZGS1: debito 528.51, credito 0.00
  - saldo 6723.44
  - delega DELEGA-2026-12 trasmessa il 2027-01-12
- Fermi: nessuno
- Su dati fittizi:
  - mappatura dei codici, catalogo dei codici F24EP, scadenza e festivi del corpus fittizio

**File telematico**

- Riuscito:
  - file f24ep-2026-12.txt: 4 record
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
  - esito versato 24: 58 righe, 7030.04 versati il 2027-01-18
  - righe ancora da versare nel mese: 0
- Fermi: nessuno
- Su dati fittizi:
  - l'addebito e' simulato dal percorso, alla data di versamento scelta

## Difetti del nucleo trovati

Nessuno trovato.

## Non esercitato dal mese

- La tredicesima non e' un istituto del corpus: il pagamento di dicembre non la contiene, anche se il tabellare annuo del corpus e' per dodici mensilita' piu' la tredicesima.
- Le addizionali regionale e comunale sono calcolate al conguaglio di dicembre sul domicilio fiscale delle persone (comune e regione di fantasia) e trattenute a rate dal 2027: nel mese di prova si vede solo l'acconto comunale di R01, che ha il reddito 2025 dalla CU (le rate del saldo, la cessazione e la restituzione a credito sono nei test). Per le altre persone, senza conguaglio 2025 ne' CU, niente acconto e un avviso. 381E, 384E, 385E, 160E e 161E hanno nel catalogo fittizio una forma assunta, da verificare.
- Il contributo aggiuntivo dell'1% scatta in almeno un quadro, e non ha una causale nel catalogo.
- L'acconto IRAP e' calcolato all'8,5% sulla base di ogni pagamento e versato col 380E, una riga per regione. Nessun rapporto del mese ha una sede di lavoro: vale la regione dell'ente, un fatto dell'ente. Il codice regione e' del corpus reale, da riscontrare sulla tabella AdE. Comando e convenzione non sono modellati (la convenzione di segreteria ferma gia' il calcolo del rapporto).

## File prodotti

- `f24ep-2026-03.txt`
- `f24ep-2026-12.txt`
- `lista-pos-pa-2026-03.xml`
