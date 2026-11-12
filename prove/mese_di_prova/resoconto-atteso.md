# Mese di prova: resoconto

> **Dati e corpus fittizi.** Ente, persone, codici fiscali, IBAN e atti sono di fantasia; nessun valore di questo resoconto e' un importo vero. Il percorso gira su un corpus **non reale**: l'unione del corpus reale (`corpus/funzioni-locali-cpdel.toml`, che non cambia) e di un'aggiunta fittizia (`prove/mese_di_prova/corpus_fittizio.toml`, tutti i riferimenti `fittizio:`). Il corpus reale rifiuta i riferimenti fittizi (ADR 0003): per questo l'unione si carica come corpus non reale.

Il resoconto e' generato da `python -m prove.mese_di_prova` e fissato da `tests/test_mese_di_prova.py`: ogni ticket futuro lo cambia nel punto che sblocca.

## Corpus

| Voce | Corpus reale | Aggiunta fittizia | Unione usata |
|---|---:|---:|---:|
| istituti con regola | 44 | 2 | 46 |
| basi imponibili | 6 | 0 | 6 |
| fermi dichiarati | 24 | 0 | 24 |
| categorie di reddito | 3 | 0 | 3 |
| regole di ritenuta | 2 | 0 | 2 |
| regole di conguaglio | 2 | 0 | 2 |
| dichiarazioni di pagamento fisiologico | 0 | 1 | 1 |
| dichiarazioni di composizione | 6 | 55 | 61 |
| mappature verso codici esterni | 6 | 18 | 24 |
| codici nel catalogo F24EP | 0 | 18 | 18 |
| regole di scadenza F24EP | 1 | 2 | 3 |
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
| Fatti di avvio, una tantum (anagrafica, assunzioni, inquadramento) | 179 | 0 | 15 | 0 |
| Fatti ricorrenti del mese (atti, variazioni, cessazioni, 730) | 0 | 0 | 17 | 1 |
| Conferme della Ragioneria | 0 | 1 | 1 | 1 |
| Scelte (valuta prevista, data di versamento, ultimo pagamento) | 0 | 1 | 2 | 3 |
| Eventi che oggi nessun adattatore porta (pagamento, ricevute, versamento) | 0 | 1 | 14 | 13 |
| Comandi di avvio (non sono dati: emissione, produzione dei file, trasmissione) | 0 | 1 | 5 | 6 |
| **Totale senza i comandi** | **179** | **3** | **49** | **18** |

La preparazione di febbraio e' il pagamento che precede il mese, scritto solo perche' l'arretrato di R02 e' una differenza rispetto a un esito pagato: non fa parte del mese e non e' nel totale di marzo.

Fatti di avvio per soggetto: R01 18, R02 16, R03 16, R04 18, R05 16, R07 16, R08 15, R09 16, R10 11, R11 10, R12 21, ente 6.
Assunzione di marzo (avvio di un rapporto nuovo): R06 15.

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
- [comando] 1 x richiesta di verifica 48-bis per R08
- [comando] 1 x richiesta di verifica 48-bis per R09
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
- [comando] 1 x richiesta di verifica 48-bis per R01
- [comando] 1 x richiesta di verifica 48-bis per R02
- [comando] 1 x richiesta di verifica 48-bis per R03
- [comando] 1 x richiesta di verifica 48-bis per R07
- [comando] 1 x trasmissione della delega (2026-12)

Nota: la cessazione di R05 costa 13 scritture a mano. Il nucleo non ha un fatto di cessazione: i fatti sono immutabili e il servizio di un rapporto finisce solo se si annullano i sei fatti di inquadramento aperti e si riscrivono con una fine (piu' il codice di cessazione).

## Il percorso, passo per passo

### Marzo 2026

**Fatti**

- Riuscito:
  - 194 fatti di avvio (ente, persone, rapporti, assunzione di R06) registrati nel registro
  - 17 fatti del mese: performance, progressione, cessazione
- Fermi: nessuno
- Su dati fittizi:
  - tutti: ente, persone e rapporti sono di fantasia

**Calcolo**

- Riuscito:
  - R01: 2 importi, lordo 2228.35
  - R02: 8 importi, lordo 2208.41
  - R02: arretrato su febbraio, differenza rispetto all'esito pagato: 6 righe, netto -19.94
  - R03: 3 importi, lordo 2424.12
  - R03: performance di competenza 2025: 600.00, pagamento fisiologico dichiarato dal corpus fittizio
  - R04: 2 importi, lordo 1048.14
  - R05: 3 importi, lordo 1350.87
  - R05: tredicesima_istruttori dell'anno 2026: 403.93, 73 giorni su 365
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
  - versione 2: 134 righe di composizione, valuta prevista 2026-03-27, 12 rapporti
  - netto R01: 2087.76
  - netto R02: 1832.96
  - netto R03: 2171.47
  - netto R04: 882.99
  - netto R05: 1285.06
  - netto R06: 713.70
  - netto R07: 1941.95
  - netto R08: 3617.51
  - netto R09: 3323.42
  - netto R10: 2243.33
  - netto R11: 1120.13
  - netto R12: 752.49
  - righe di proposta (11): U.1.01.01.01.002 01.01 imp 2026/1 9951.65; U.1.01.01.01.002 01.02 imp 2026/2 12727.26; U.1.01.01.01.004 01.02 imp 2026/4 600.00; U.1.01.02.01.001 01.01 imp 2026/5 2945.33; U.1.01.02.01.001 01.02 imp 2026/6 3840.32; U.1.01.02.01.003 01.01 imp 2026/7 495.55; U.1.01.02.01.003 01.02 imp 2026/8 89.28; U.1.02.01.01.001 01.01 imp 2026/9 1118.15; U.1.02.01.01.001 01.02 imp 2026/10 1263.42; U.1.03.02.01.001 01.01 imp 2026/11 3000.00; U.1.03.02.12.003 01.02 imp 2026/14 1500.00
  - conguaglio fiscale sull'ultimo pagamento: R05 -109.93
- Fermi: nessuno
- Su dati fittizi:
  - esito della verifica 48-bis di R08 simulato: non inadempiente
  - esito della verifica 48-bis di R09 simulato: non inadempiente
  - gli impegni automatici sono fatti contabili simulati dal percorso, con disponibilita' molto alta
  - categorie di reddito, ritenuta, conguaglio e dichiarazioni di composizione sono del corpus fittizio (valori fiscali finti)
- Note:
  - avviso acconto_senza_base: R02, R03, R04, R06, R07, R08, R09, R10, R11, R12
  - avviso mensilita_aggiuntiva_nel_conguaglio: R05
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
  - esito pagato 2: 134 righe, valuta 2026-03-27
- Fermi: nessuno
- Su dati fittizi:
  - l'evento di pagamento eseguito e' simulato dal percorso, con valuta uguale alla prevista

**Prospetto paga**

- Riuscito:
  - R01: prospetto del pagamento del 2026-03-27 (esito 2), posizione 0FZEQF, 9 righe sul netto, netto 2087.76, 3 senza effetto sul netto; consegnato, esito dichiarato 3
  - R02: prospetto del pagamento del 2026-03-27 (esito 2), posizione 0FZEQF, 14 righe sul netto, netto 1832.96, 3 senza effetto sul netto; consegnato, esito dichiarato 4
  - R03: prospetto del pagamento del 2026-03-27 (esito 2), posizione 0OEESP, 10 righe sul netto, netto 2171.47, 4 senza effetto sul netto; consegnato, esito dichiarato 5
  - R04: prospetto del pagamento del 2026-03-27 (esito 2), posizione 0OP000, 8 righe sul netto, netto 882.99, 3 senza effetto sul netto; consegnato, esito dichiarato 6
  - R05: prospetto del pagamento del 2026-03-27 (esito 2), posizione 0IR000, 10 righe sul netto, netto 1285.06, 3 senza effetto sul netto; consegnato, esito dichiarato 7
  - R06: prospetto del pagamento del 2026-03-27 (esito 2), posizione 0OEESP, 8 righe sul netto, netto 713.70, 3 senza effetto sul netto; consegnato, esito dichiarato 8
  - R07: prospetto del pagamento del 2026-03-27 (esito 2), posizione 0IR000, 8 righe sul netto, netto 1941.95, 3 senza effetto sul netto; consegnato, esito dichiarato 9
  - R08: prospetto del pagamento del 2026-03-27 (esito 2), posizione -, 9 righe sul netto, netto 3617.51, 3 senza effetto sul netto
  - R09: prospetto del pagamento del 2026-03-27 (esito 2), posizione -, 9 righe sul netto, netto 3323.42, 3 senza effetto sul netto
  - R10: prospetto del pagamento del 2026-03-27 (esito 2), posizione sindaco, 2 righe sul netto, netto 2243.33, 2 senza effetto sul netto; consegnato, esito dichiarato 10
  - R11: prospetto del pagamento del 2026-03-27 (esito 2), posizione -, 4 righe sul netto, netto 1120.13, 2 senza effetto sul netto
  - R12: prospetto del pagamento del 2026-03-27 (esito 2), posizione 0OP000, 8 righe sul netto, netto 752.49, 3 senza effetto sul netto; consegnato, esito dichiarato 11
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
  - R05: 1 quadri, contributi nei quadri 506.26; contributi trattenuti uguali ai dovuti
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
  - riga F 100E: debito 4733.17, credito 0.00
  - riga F 170E: debito 0.00, credito 500.00
  - riga F 175E: debito 0.00, credito 1072.29
  - riga F 179E: debito 80.39, credito 0.00
  - riga R 380E: debito 2381.57, credito 0.00
  - riga S 385E: debito 3.30, credito 0.00
  - riga Q CXX: debito 1053.96, credito 0.00
  - riga Q P201: debito 7686.68, credito 0.00
  - riga Q P607: debito 524.26, credito 0.00
  - riga Q P608: debito 584.83, credito 0.00
  - riga Q P909: debito 82.32, credito 0.00
  - saldo 15558.19
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
  - esito versato 13: 96 righe, 18702.77 versati il 2026-04-16
  - righe ancora da versare nel mese: 0
- Fermi: nessuno
- Su dati fittizi:
  - l'addebito e' simulato dal percorso, alla data di versamento scelta

### Dicembre 2026 (conguaglio)

**Calcolo**

- Riuscito:
  - R01: 3 importi, lordo 4420.37
  - R01: tredicesima_funzionari dell'anno 2026: 2192.02, 365 giorni su 365
  - R02: 3 importi, lordo 4420.37
  - R02: tredicesima_funzionari dell'anno 2026: 2192.02, 365 giorni su 365
  - R03: 3 importi, lordo 3620.72
  - R03: tredicesima_operatori_esperti dell'anno 2026: 1796.60, 365 giorni su 365
  - R04: 3 importi, lordo 2082.67
  - R04: tredicesima_operatori dell'anno 2026: 1034.53, 365 giorni su 365
  - R06: 5 importi, lordo 3227.83
  - R06: riduzione_tfr_tredicesima dell'anno 2026: -28.65
  - R06: tredicesima_operatori_esperti dell'anno 2026: 1432.36, 291 giorni su 365
  - R07: 4 importi, lordo 4071.32
  - R07: tredicesima_istruttori dell'anno 2026: 2019.63, 365 giorni su 365
  - R07: rimborso del 730-4: 150.00, anno dei redditi dichiarati 2025
  - R08: 3 importi, lordo 5385.06
  - R09: 3 importi, lordo 4769.68
  - R10: 2 importi, lordo 3000.00
  - R11: 1 importi, lordo 1500.00
  - R12: 5 importi, lordo 1718.32
  - R12: riduzione_tfr_tredicesima dell'anno 2026: -17.24
  - R12: tredicesima_operatori dell'anno 2026: 862.11, 365 giorni su 365
- Fermi: nessuno
- Su dati fittizi:
  - tabelle e parametri del corpus reale
- Note:
  - R05: non in servizio nel mese, nessun importo

**Versione di proposta**

- Riuscito:
  - versione 3: 105 righe di composizione, valuta prevista 2026-12-18, 8 rapporti
  - netto R01: 4324.55
  - netto R02: 4745.49
  - netto R03: 3560.58
  - netto R04: 1543.08
  - netto R06: 2452.50
  - netto R07: 4120.20
  - netto R10: 2376.67
  - netto R12: 1283.83
  - righe di proposta (7): U.1.01.01.01.002 01.02 imp 2026/2 23508.43; U.1.01.02.01.001 01.01 imp 2026/5 528.51; U.1.01.02.01.001 01.02 imp 2026/6 6150.52; U.1.01.02.01.003 01.02 imp 2026/8 241.71; U.1.02.01.01.001 01.01 imp 2026/9 255.00; U.1.02.01.01.001 01.02 imp 2026/10 2006.63; U.1.03.02.01.001 01.01 imp 2026/11 3000.00
  - conguaglio fiscale sull'ultimo pagamento: R01 -988.07, R02 -1258.39, R03 -790.83, R04 0.00, R06 -55.91, R07 -903.90, R10 -133.34, R12 0.00
- Fermi:
  - R08: caso non modellato, conguaglio annuo di contributo_aggiuntivo in 2026-12 (già esposto nel periodo 2026-03-01/2026-03-31)
  - R09: caso non modellato, conguaglio annuo di contributo_aggiuntivo in 2026-12 (già esposto nel periodo 2026-03-01/2026-03-31)
  - R11: manca il fatto attestazione_prestazione per 2026-12-10/2026-12-10: l'importo resta calcolato ma non entra in una versione di proposta (prassi:immedia:nota:2026-11-07;10)
- Su dati fittizi:
  - esito della verifica 48-bis di R01 simulato: non inadempiente
  - esito della verifica 48-bis di R02 simulato: non inadempiente
  - esito della verifica 48-bis di R03 simulato: non inadempiente
  - esito della verifica 48-bis di R07 simulato: non inadempiente
  - gli impegni automatici sono fatti contabili simulati dal percorso, con disponibilita' molto alta
  - categorie di reddito, ritenuta, conguaglio e dichiarazioni di composizione sono del corpus fittizio (valori fiscali finti)
- Note:
  - avviso mensilita_aggiuntiva_nel_conguaglio: R01, R02, R03, R04, R06, R07, R12
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
  - esito pagato 14: 105 righe, valuta 2026-12-18
- Fermi: nessuno
- Su dati fittizi:
  - l'evento di pagamento eseguito e' simulato dal percorso, con valuta uguale alla prevista

**Prospetto paga**

- Riuscito:
  - R01: prospetto del pagamento del 2026-12-18 (esito 14), posizione 0FZEQF, 12 righe sul netto, netto 4324.55, 3 senza effetto sul netto; consegnato, esito dichiarato 15
  - R02: prospetto del pagamento del 2026-12-18 (esito 14), posizione 0FZEQF, 10 righe sul netto, netto 4745.49, 3 senza effetto sul netto; consegnato, esito dichiarato 16
  - R03: prospetto del pagamento del 2026-12-18 (esito 14), posizione 0OEESP, 11 righe sul netto, netto 3560.58, 3 senza effetto sul netto; consegnato, esito dichiarato 17
  - R04: prospetto del pagamento del 2026-12-18 (esito 14), posizione 0OP000, 11 righe sul netto, netto 1543.08, 3 senza effetto sul netto; consegnato, esito dichiarato 18
  - R06: prospetto del pagamento del 2026-12-18 (esito 14), posizione 0OEESP, 11 righe sul netto, netto 2452.50, 3 senza effetto sul netto; consegnato, esito dichiarato 19
  - R07: prospetto del pagamento del 2026-12-18 (esito 14), posizione 0IR000, 12 righe sul netto, netto 4120.20, 3 senza effetto sul netto; consegnato, esito dichiarato 20
  - R10: prospetto del pagamento del 2026-12-18 (esito 14), posizione sindaco, 3 righe sul netto, netto 2376.67, 2 senza effetto sul netto; consegnato, esito dichiarato 21
  - R12: prospetto del pagamento del 2026-12-18 (esito 14), posizione 0OP000, 12 righe sul netto, netto 1283.83, 3 senza effetto sul netto; consegnato, esito dichiarato 22
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
  - riga F 100E: debito 1338.34, credito 0.00
  - riga F 150E: debito 0.00, credito 150.00
  - riga F 170E: debito 62.50, credito 0.00
  - riga F 175E: debito 0.00, credito 1687.28
  - riga R 380E: debito 2261.63, credito 0.00
  - riga S 161E: debito 0.00, credito 3.30
  - riga Q CXX: debito 528.51, credito 0.00
  - riga Q P201: debito 7707.85, credito 0.00
  - riga Q P607: debito 901.32, credito 0.00
  - riga Q P608: debito 241.71, credito 0.00
  - riga Q P909: debito 82.62, credito 0.00
  - saldo 11283.90
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
  - esito versato 24: 70 righe, 14965.06 versati il 2027-01-18
  - righe ancora da versare nel mese: 0
- Fermi: nessuno
- Su dati fittizi:
  - l'addebito e' simulato dal percorso, alla data di versamento scelta

## Difetti del nucleo trovati

Nessuno trovato.

## Non esercitato dal mese

- La tredicesima del comparto e' calcolata sul solo tabellare dell'area (ADR 0038): differenziali, assegni personali, RIA e posizione delle EQ non sono istituti del corpus. La ritenuta a parte delle mensilita' aggiuntive (art. 23 c. 2 lett. b D.P.R. 600/1973) non e' modellata: la tredicesima passa solo nel pagamento che porta il conguaglio, con un avviso; pagata a parte prima dell'ultimo pagamento fermerebbe il rapporto. Le assenze che riducono o tolgono i ratei non sono nel nucleo. Dirigente e segretario hanno il tabellare su tredici mensilita' e nessuna tredicesima a parte.
- Le addizionali regionale e comunale sono calcolate al conguaglio di dicembre sul domicilio fiscale delle persone (comune e regione di fantasia) e trattenute a rate dal 2027: nel mese di prova si vede solo l'acconto comunale di R01, che ha il reddito 2025 dalla CU (le rate del saldo, la cessazione e la restituzione a credito sono nei test). Per le altre persone, senza conguaglio 2025 ne' CU, niente acconto e un avviso. 381E, 384E, 385E, 160E e 161E hanno nel catalogo fittizio una forma assunta, da verificare.
- Il contributo aggiuntivo dell'1% scatta in almeno un quadro, e non ha una causale nel catalogo.
- L'acconto IRAP e' calcolato all'8,5% sulla base di ogni pagamento e versato col 380E, una riga per regione. Nessun rapporto del mese ha una sede di lavoro: vale la regione dell'ente, un fatto dell'ente. Il codice regione e' del corpus reale, da riscontrare sulla tabella AdE. Comando e convenzione: l'IRAP segue l'ente che utilizza il dipendente, sul rimborso versato; i rimborsi tra enti non sono modellati (la convenzione di segreteria ferma gia' il calcolo del rapporto).

## File prodotti

- `f24ep-2026-03.txt`
- `f24ep-2026-12.txt`
- `lista-pos-pa-2026-03.xml`
