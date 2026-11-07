# Part-time nella ListaPosPA: quali elementi chiede l'INPS

Ticket: #72. Data: 2026-11-07.

## Domanda

Quali elementi chiede la ListaPosPA (UniEmens, sezione gestione pubblica) per un periodo in part-time? Tipo, percentuale e, per verticale e misto, giorni e ore: nomi esatti, formato, livello (periodo, mese, giorno), regole di compilazione.

## Metodo e legenda

Marcature come negli altri documenti di `docs/research/`: **norma certa** (istruzione ufficiale INPS letta sul testo, vincola la compilazione), **prassi-interpretazione**, **da verificare**.

Tutti i PDF sono stati scaricati da inps.it e convertiti con `pdftotext`: lettura diretta del testo, non di un riassunto.

## Fonti lette

- **[DT]** Documento tecnico UniEmens (individuale) versione 4.33 del 29/09/2026, pp. 182-185 (elementi `InquadramentoLavPA` e `PartTimePA`), tabella delle revisioni. https://www.inps.it/content/dam/inps-site/pdf/prestazioni-e-servizi/uniemens-enti-amministrazioni/UniEMENSind.pdf
- **[AT]** Allegato tecnico 4.33.1 del 30/10/2026 (schema di validazione 4.33.1), Appendice B, p. 244 (`TipoPartTime`) e tabella `TipoImpiego`. https://www.inps.it/content/dam/inps-site/pdf/prestazioni-e-servizi/uniemens-aziende-private/UniemensInd_AllegatoTecnico.pdf
- **[MAN]** Manuale operativo UniEmens/ListaPosPA v1.0 del 13/02/2018, pp. 16-17 (quadro E0), pp. 22-23 (controlli), esempi di compilazione 13 e 14. https://www.inps.it/content/dam/inps-site/pdf/prestazioni-e-servizi/uniemens-enti-amministrazioni/937KEY-manuale_lista_pospa_v1-13_02_2018.pdf
- **[C74]** Circolare INPS 74 del 04/05/2021, par. 3 (flusso privato) e par. 9. https://servizi2.inps.it/CircolariZIP/Circolare%20numero%2074%20del%2004-05-2021.pdf
- **[M2162]** Messaggio INPS 2162 del 03/06/2021 (solo flusso privato). https://servizi2.inps.it/MessaggiZIP/Messaggio%20numero%202162%20del%2003-06-2021.pdf

**Non letto:** lo schema XSD (non scaricato), il testo dell'art. 62 CCNL (non pertinente a questa ricerca). I nomi dei campi e i valori sono quindi letti dai documenti tecnici, non dall'XSD.

## Esito

### Dove stanno i dati: livello periodo

Nella ListaPosPA il part-time sta nel **periodo**, non nel mese né nel giorno: `E0_PeriodoNelMese / InquadramentoLavPA / PartTimePA` (e uguale in `V1_PeriodoPrecedente`). [DT p. 185; AT p. 244] **norma certa**.

Ogni periodo è delimitato da `GiornoInizio` e `GiornoFine`. Se nel mese varia uno degli elementi di `InquadramentoLavPA`, compreso il part-time, si compila un nuovo `E0_PeriodoNelMese` che inizia il giorno dopo la fine del precedente. [MAN p. 18] **norma certa**. Un cambio di percentuale a metà mese produce quindi due periodi.

### Elementi

| Elemento | Contenuto | Regole | Marcatura |
|---|---|---|---|
| `TipoPartTime` | `P` orizzontale, `V` verticale, `M` misto | Obbligatorio se `TipoImpiego` di `InquadramentoLavPA` è 8 (part-time a tempo indeterminato) o 18 (part-time a tempo determinato), errore 00027I. Valori in Appendice B. Da non compilare per il personale supplente scolastico. [DT p. 185; AT p. 244; MAN p. 17, p. 23] | norma certa |
| `PercPartTime` | percentuale part-time, **espressa in millesimi** (100 % = 100000) | Elemento obbligatorio dentro `PartTimePA`. Se il tipo è `P`: maggiore di 0 e minore di 100000, errore 00106I. Se il tipo è `V` o `M`: da 0 a 100000. Zero solo per `V` o `M`, errore 00026I. «Da indicare 0 nel caso di part time verticale con assenza di attività lavorativa.» [DT p. 185; MAN p. 17, p. 23] | norma certa |

Nota sul formato: il documento tecnico 4.33 dice «millesimi» con massimo 100000 (quindi 60 % = 60000). Il manuale 2018 dice «percentuale (%)» con esempi 100 e 0 e con lo stesso limite 100000 nei controlli. Il valore numerico ammesso è quello dei controlli; la lettura 60 % = 60000 è la sola coerente con il limite 100000. Lo schema XSD non è stato aperto. Marcatura: **norma certa** sul limite, **da verificare** sulla scala esatta finché non si legge l'XSD.

`PercRetribuzione` non va più valorizzato nel periodo (circolare 81/2015). [MAN p. 16] Non è un elemento del part-time.

### Giorni e ore: non esistono

Nella sezione ListaPosPA **non c'è nessun elemento di giorni o ore del part-time**, né a livello di periodo, né di mese, né di giorno. [DT pp. 182-186; MAN pp. 16-17; AT App. B] **norma certa** sull'assenza nei documenti letti.

Gli unici elementi di ore sono `OrarioSettimanaleRidotto` e `OrarioSettimanaleCompleto` (due caratteri numerici), che valgono solo per il **personale scolastico a tempo determinato** con orario ridotto. [DT p. 186; MAN p. 17] Non riguardano gli enti locali.

`GiorniDirittoPartTime`, `PercPartTimeMese` e il codice `DR00` di `TipoLavStat` (circolare 74/2021, messaggio 2162/2021) appartengono al flusso `DenunciaIndividuale` dei lavoratori privati, a `FS`, ex Ipost ed Esattoriali; non alla ListaPosPA. Per la gestione pubblica la circolare 74/2021 dice che l'estratto conto UNEX «è già inclusivo» del tempo non lavorato per effetto dell'art. 8 L. 554/1988. [C74, paragrafo sull'estratto conto UNEX e paragrafo 1] **norma certa**. Giorni e ore della programmazione non hanno quindi un campo in cui essere esposti; servono al calcolo di `PercPartTime` nei casi `V` e `M`, e al Conto Annuale (ADR 0026).

### Come si compila la percentuale per verticale e misto

Il manuale 2018 chiarisce, per il part-time verticale, che in ogni mese dichiarato va riportata «la percentuale di lavoro da effettuare e non la percentuale di part-time del contratto»:
- mese con prestazione per l'intero mese: 100; mese senza alcuna prestazione: 0, con `E0_PeriodoNelMese` compilato comunque (esempio 13);
- mese in cui si lavora per metà dei giorni (15 di lavoro e 15 di non lavoro): 50 % (esempio 14).

[MAN p. 17, esempi 13 e 14] **prassi-interpretazione** (è un manuale operativo, non lo schema; è precedente al documento tecnico 4.33, che ha precisato la descrizione di `PercPartTime` ma nel testo letto non dà una formula). Per `P` il manuale e il documento tecnico non dicono che la percentuale sia calcolata sul mese: è la percentuale del contratto. **da verificare**.

**Non determinato con certezza:** la formula esatta della percentuale mensile per `V` e `M` quando il mese è lavorato solo in parte. Gli esempi fanno solo il caso di 15 giorni su 30; non dicono se il rapporto è tra giorni di calendario, giorni lavorabili o ore, né come si tratta il misto (giorni a orario ridotto). **da verificare**.

### Altre regole utili

- `Contratto` e `Qualifica` (tre o quattro e sei caratteri) sono nello stesso gruppo, ma non riguardano il part-time. [DT p. 184]
- Il part-time non cambia l'obbligo di compilare `E0_PeriodoNelMese` anche per i mesi di non lavoro del verticale. [MAN p. 17] **norma certa**.

## Conseguenze per il modello

1. Si possono esporre con certezza `TipoPartTime` (P, V, M) e `PercPartTime` per il tipo orizzontale (percentuale del contratto per 1000), per periodo.
2. Per `V` con nessun giorno lavorativo nel periodo, `PercPartTime` vale 0 (regola scritta). Per `V` e `M` con lavoro nel mese la formula non è determinata: resta bozza non trasmissibile con il caso nominato.
3. Giorni e ore della programmazione non sono campi della ListaPosPA; la programmazione resta necessaria per decidere i casi `V` e `M` e per il Conto Annuale.

## Domande aperte

- Scala esatta di `PercPartTime` nello schema XSD 4.33.1 (millesimi contro percentuale).
- Formula mensile per verticale e misto con lavoro parziale nel mese (giorni o ore; calendario o lavorabili).
- Se il flusso ListaPosPA ammette, per `V` nei mesi lavorati per intero, 100 (manuale 2018) o la percentuale del contratto (come per i privati dal 2021).
