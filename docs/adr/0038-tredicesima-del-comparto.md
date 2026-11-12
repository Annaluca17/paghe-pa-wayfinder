# Tredicesima del comparto: annuale sul tabellare, pesata sul part-time, ferma senza conguaglio

Il corpus calcola la tredicesima mensilità delle quattro aree del comparto Funzioni Locali. È un importo annuale (ADR 0004), un istituto per area (`tredicesima_funzionari`, `tredicesima_istruttori`, `tredicesima_operatori_esperti`, `tredicesima_operatori`), con queste regole:

- **Base.** Il tabellare mensile dell'area dell'ultimo giorno di servizio dell'anno: dicembre, oppure l'ultimo mese per chi cessa. Chi cambia area nell'anno prende tutta la tredicesima sull'area nuova.
- **Maturazione.** Giorni di servizio dell'anno diviso 365, con tetto a 1; intera con servizio continuativo dal 1° gennaio, anche negli anni bisestili. I giorni senza il fatto di servizio non maturano. Un solo arrotondamento al centesimo, sull'importo finale.
- **Part-time.** Proporzionale. Ogni giorno di servizio conta per la sua percentuale, 100 a tempo pieno: se il part-time cambia, inizia o finisce nell'anno, i periodi si pesano a giorni (nota di prassi 12).
- **Regime TFR.** La tredicesima porta la sua riduzione del lordo (`riduzione_tfr_tredicesima`), calcolata come quella del mese e riservata a chi è in regime TFR nell'ultimo giorno di servizio.
- **Basi.** Concorre per intero a CPDEL, Fondo Credito, TFS e IRAP nel mese in cui è pagata; non è un ulteriore elemento TFR; è reddito di lavoro dipendente.
- **Pagamento.** Il nucleo calcola l'importo e non sceglie la data: l'Ufficio personale lo mette in un pagamento. Il corpus dichiara la finestra del contratto (10-18 dicembre); fuori finestra, per chi è in servizio, la proposta porta un avviso. Al cessato si paga con il pagamento finale.
- **Ritenuta.** La tredicesima è dichiarata **mensilità aggiuntiva**. La ritenuta a parte che la norma chiede non è modellata: se il pagamento porta anche il conguaglio si procede con un avviso, altrimenti il calcolo fiscale di quel rapporto si ferma e nomina il caso.

Scelto da Luca l'11/11/2026 nel grilling, cinque domande. Fonti e certezza di ogni punto sono in `docs/research/tredicesima-comparto.md`.

## Perché

Serve al passo successivo: la ritenuta del mese deve calcolare le detrazioni su un reddito annuo proiettato (pagato da inizio anno, mesi che restano, tredicesima). Il confronto con il gestionale in uso su un ente reale (ottobre 2026) ha mostrato che il nucleo usava l'imponibile del mese per 12, cioè un reddito senza tredicesima.

L'importo atteso della tredicesima di un rapporto è `calcola_annuale(registro, corpus, rapporto, anno)`: con i fatti noti, un servizio senza fine vale fino al 31 dicembre. Con `fino_al` la stessa funzione dà il maturato a una data.

## Considered Options

- **Ratei mensili in dodicesimi:** non è il testo dell'art. 75, e l'ADR 0004 li aveva già scartati.
- **Un importo da atto per le voci che mancano** (differenziali, assegni, RIA, posizione EQ): un numero scritto a mano, da togliere quando arriveranno gli istituti.
- **Percentuale di part-time di dicembre su tutto l'anno:** è la lettura letterale del c. 2, ma contraddice il parere ARAN CFL188.
- **Fermo se il part-time cambia nell'anno:** più prudente, ma lascia senza tredicesima un caso ordinario.
- **Ritenuta a parte subito:** manca una fonte su come dividere fra mese e tredicesima i contributi del lavoratore, e il passo successivo riscrive la ritenuta.
- **Tredicesima sommata al mese con un solo avviso:** fuori dal conguaglio la ritenuta sarebbe una stima.
- **Fermo fuori dalla finestra 10-18 dicembre:** un pagamento il 19 dicembre non partirebbe.

## Consequences

**Norma certa**

- Art. 75 CCNL 16/11/2022, ancora vigente: il CCNL 28/10/2026 non lo disapplica (art. 2 c. 8) e rinvia ancora all'art. 74 c. 2 lett. c).
- Importo pari alla retribuzione individuale mensile di dicembre o dell'ultimo mese, 365esimi sui giorni di servizio, pagamento tra il 10 e il 18 dicembre (art. 75 c. 1, 2, 3, 5).
- TFS: la legge nomina la tredicesima (L. 152/1968 art. 11). CPDEL e IRAP: come il tabellare.
- Mensilità aggiuntive tassate con gli scaglioni annui ragguagliati a mese: art. 23 c. 2 lett. b) D.P.R. 600/1973.

**Prassi-interpretazione**

- Divisore 365 negli anni bisestili e arrotondamento finale al centesimo.
- Pesatura a giorni del part-time che cambia nell'anno: parere ARAN CFL188, letto di seconda mano (**da verificare**, nota di prassi 12).
- Riduzione del lordo TFR sulla tredicesima (nota di prassi 5).

**Da verificare**

- Assenza di una disapplicazione dell'art. 75 nel CCNL 23/02/2026, letta sulle note del vault.
- Comma e lettera dell'art. 33 D.Lgs. 33/2025 che dal 2027 sostituiscono la lett. b): il corpus cita l'articolo.

**Conseguenze sul modello**

- **Motore annuale.** Una regola annuale con condizione `tipo=codice` matura sui giorni del fatto di servizio del corpus e vale se la condizione è vera nell'ultimo giorno. Una regola annuale può leggere importi annuali e ne deriva senza quota. Le altre regole annuali non cambiano.
- **Dichiarazione `[[mensilita_aggiuntiva]]`** del corpus, per istituto, con date, riferimento e finestra di pagamento.
- **La formula della riduzione TFR del mese non cambia:** le voci utili al TFS sono divise fra la riduzione del mese e quella della tredicesima, e un test le tiene allineate.
- **Limiti nominati.** La base è il solo tabellare: differenziali, assegni personali, RIA e posizione delle EQ entreranno quando saranno istituti. Le assenze che tolgono o riducono i ratei (art. 75 c. 7-10) non sono nel nucleo; la retribuzione ridotta ferma già il calcolo. La cessazione per motivi disciplinari non ha un fatto. Il cambio di regime di fine servizio nell'anno resta un quadro fermo della ListaPosPA (ADR 0011).
- **Tredicesima pagata a parte prima dell'ultimo pagamento dell'anno:** ferma il rapporto finché la ritenuta a parte non è modellata. Oggi passa insieme al pagamento che porta il conguaglio.
- **Dirigenti e segretari** restano com'erano: tabellare annuo su tredici mensilità, nessuna tredicesima a parte (nota di prassi 9).
