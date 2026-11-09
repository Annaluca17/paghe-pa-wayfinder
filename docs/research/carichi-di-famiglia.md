# Carichi di famiglia: art. 12 TUIR 2026, art. 12 del TU 2027 e applicazione da parte del sostituto

Ticket: #98 · Branch: `98-carichi-famiglia` · Data: 2026-11-09 · Serve a: le regole delle detrazioni dell'art. 12 nella ritenuta mensile e nel conguaglio (ADR 0019, voce «fuori dal ticket #93»)

## Domanda

Quali sono, sul testo vigente, le detrazioni per carichi di famiglia che il modello deve calcolare per gli anni d'imposta 2026 (art. 12 TUIR) e 2027 (art. 12 del D.Lgs. 117/2026)? Che cosa cambia con il correttivo D.Lgs. 148/2026? Come le applica il sostituto: dichiarazione, mesi, percentuali, conguaglio? Come interagiscono con la riduzione delle detrazioni per redditi alti (art. 16-ter) e che reddito entra nelle formule?

## Legenda e come sono state lette le fonti

Stessa legenda di `parametri-fiscali-2026-2027.md`:

- **norma certa**: testo di legge o regolamento letto in questa sessione, oppure provvedimento dell'amministrazione titolare (istruzioni dei modelli) per ciò che dice del modello stesso.
- **prassi-interpretazione**: parere o istruzione AdE su come si applica la norma, oppure lettura ricavata da più fonti concordi.
- **da verificare**: non confermato su fonte primaria in questa sessione.

Aperti e letti il 09/11/2026:

- **Normattiva** (pagina dell'articolo): TUIR artt. 10, 12 e 16-ter con `!vig=2026-11-09`; D.Lgs. 117/2026 (allegato) artt. 10 e 12; L. 207/2024 art. 1 commi 10-12; D.P.R. 600/1973 art. 23; D.Lgs. 33/2025 (allegato) art. 33.
- **D.Lgs. 148/2026**: testo integrale (34 pagine, «Vigente al 12-8-2026», GU n. 185 dell'11/08/2026, S.O. n. 30) letto su una **copia PDF ospitata da ance.it**; la pagina della Gazzetta Ufficiale non è stata aperta. L'effetto sull'art. 12 è confermato dalle note di aggiornamento di Normattiva (secondo atto, stesso esito).
- **Agenzia delle Entrate**: istruzioni CU 2026, istruzioni 730/2026, circolare 4/E del 16/05/2025 (§ 1.3), circolare 4/E del 18/02/2022 (§ 1.4).
- **Ministero delle Finanze**: circolare 326/E del 23/12/1997 (§§ 3.3-3.5), letta su una copia PDF ospitata da mefop.it; l'originale non è stato aperto. È del 1997: vedi le riserve nel tema 3.

Note sul metodo:

- **Aliquote e importi con seconda fonte indipendente (ADR 0003)**: sotto, ogni importo dice se la seconda fonte c'è. Dove manca, lo dice la riga. In particolare, per la **formula dei figli (95.000 e +15.000 per figlio) nessun testo AdE letto riporta i numeri**: le istruzioni 730/2026 dicono solo che la detrazione è «teorica» e decresce con il reddito.
- Il **vault-pa non è stato consultato**. Nessuna affermazione si regge su di esso.
- Nessun dato reale, nessun nome di ente.
- Il disegno di legge di bilancio 2027 non è stato letto: ogni punto che può cambiare con esso è marcato **da verificare**.

## Correzioni alle premesse del ticket

- Il D.Lgs. 148/2026 è datato **07/08/2026**, non 11/08: l'11/08 è la data della Gazzetta Ufficiale. Entra in vigore il giorno dopo la pubblicazione, cioè il **12/08/2026** (art. 37). **norma certa**.
- Il «comma 7» dell'art. 12 è quello del **testo unico** (D.Lgs. 117/2026). Il correttivo modifica **due** testi con le stesse parole: il **comma 4-ter dell'art. 12 TUIR** (art. 1 c. 1) e il **comma 7 dell'art. 12 del TU** (art. 1 c. 2). **norma certa**.
- La detrazione per **famiglie numerose** (art. 12 c. 1-bis, 1.200 euro con almeno quattro figli) **non esiste più**: il comma è abrogato.
- La L. 207/2024 art. 1 **c. 11** è il comma che riscrive l'art. 12 (figli 21-30, ascendenti conviventi, comma 2-bis). Il **c. 10** introduce l'art. 16-ter (riordino delle detrazioni per oneri). Sono due cose diverse.

## Sintesi

1. **Coniuge**: 800 − 110 × (R / 15.000) fino a 15.000; **690** da 15.000 a 40.000; **690 × (80.000 − R) / 40.000** da 40.000 a 80.000; oltre, zero. **Maggiorazioni ancora esistenti**: +10, +20, +30, +20, +10 euro tra 29.000 e 35.200.
2. **Figli**: **950** euro per figlio **da 21 a meno di 30 anni** e per i figli **disabili di 30 anni e più**; sotto i 21 anni **zero** (assegno unico). Formula **950 × (95.000 − R) / 95.000**; la soglia sale di **15.000 per ogni figlio dopo il primo**, per tutti. Ripartizione **50%** tra i genitori, o **100%** al genitore con reddito più alto se c'è accordo.
3. **Altri familiari**: solo **ascendenti conviventi**, **750** euro × (80.000 − R) / 80.000, ripartiti in parti uguali tra gli aventi diritto. Gli altri familiari dell'art. 433 c.c. non danno più detrazione.
4. **Familiare a carico**: reddito fino a **2.840,51** euro, **4.000** per i figli fino a 24 anni, al lordo degli oneri deducibili.
5. **Mesi**: le detrazioni sono «rapportate a mese» e spettano dal mese in cui si verificano le condizioni a quello in cui cessano (c. 3 TUIR, c. 4 TU). Il figlio dà detrazione **dal mese del 21° compleanno fino al mese prima del 30°**.
6. **2027**: gli **importi sono identici** (confronto numerico, nessuna differenza). Cambiano la numerazione dei commi e il rinvio dell'abitazione principale (art. 10 c. 5 del TU).
7. **Correttivo 148/2026**: sposta la condizione «convivono o ricevono assegni alimentari» dal primo al secondo periodo del c. 4-ter (TUIR) / c. 7 (TU), limitata alle «altre persone» dell'art. 433 c.c. Vale dal periodo d'imposta in corso al **20/12/2025**, quindi **anche per il 2025 e il 2026**. Non tocca gli importi né la detrazione del c. 1.
8. **Art. 16-ter e 440 euro**: riguardano **oneri e spese**, non i carichi dell'art. 12. I figli a carico entrano solo nel **coefficiente** del tetto agli oneri.
9. **Dichiarazione del sostituito**: serve per i carichi (art. 23 c. 2 lett. a D.P.R. 600/1973; art. 33 c. 3 lett. a D.Lgs. 33/2025): diritto, condizioni, **codice fiscale** del familiare, impegno a comunicare le variazioni; vale anche per gli anni dopo.

## Tema 1. Art. 12 TUIR vigente nel 2026

Testo letto su Normattiva con `!vig=2026-11-09` (consolidato «al 31-12-2026»).

| Punto | Esito | Marcatura e fonte |
|---|---|---|
| **Coniuge** non legalmente ed effettivamente separato, fino a 15.000 | 800 euro, diminuiti del prodotto tra 110 euro e il rapporto R / 15.000 | **norma certa**: art. 12 c. 1 lett. a) n. 1 TUIR. Seconda fonte: istruzioni 730/2026, tabella 3 («800 − 110 × R/15.000») |
| Coniuge, da 15.000 a 40.000 | 690 euro | **norma certa**: lett. a) n. 2. Seconda fonte: 730/2026, tabella 3 |
| Coniuge, da 40.000 a 80.000 | 690 euro per la parte pari a (80.000 − R) / 40.000 | **norma certa**: lett. a) n. 3. Seconda fonte: 730/2026, tabella 3 |
| **Maggiorazione del coniuge** | +10 euro tra 29.000 e 29.200; +20 tra 29.200 e 34.700; +30 tra 34.700 e 35.000; +20 tra 35.000 e 35.100; +10 tra 35.100 e 35.200 (estremo inferiore escluso, superiore incluso) | **norma certa**: lett. b) nn. 1-5. Seconda fonte: 730/2026, tabella 3 (700, 710, 720, 710, 700 euro nelle stesse fasce) |
| **Figli**: importo e chi | 950 euro per figlio, compresi nati fuori del matrimonio riconosciuti, adottivi, affiliati o affidati e figli conviventi del coniuge deceduto, di età **≥ 21 e < 30 anni**; e per ogni figlio **≥ 30 anni con disabilità accertata** (art. 3 L. 104/1992) | **norma certa**: lett. c), nel testo della L. 207/2024 art. 1 c. 11 lett. a) n. 1. Seconda fonte: 730/2026 (tabella 4 e prospetto), CU 2026 (p. 49), circ. 4/E 2025 § 1.3 |
| Figli sotto i 21 anni | **Nessuna detrazione**, comprese le maggiorazioni (minori di tre anni, figli disabili, oltre tre figli): sono cessate con l'assegno unico dal **01/03/2022** | **norma certa**: i tre periodi sono «soppressi dal D.Lgs. 230/2021» (nota 213: dal 01/03/2022). Seconda fonte: CU 2026 (p. 32), circ. 4/E 2022 § 1.4 |
| Figli disabili tra 21 e 30 anni | La detrazione spetta (come per tutti i figli di quell'età) e si cumula con l'assegno unico | **prassi-interpretazione**: CU 2026 (p. 49), 730/2026 |
| **Formula dei figli** | 950 × (95.000 − R) / 95.000. Con più figli che danno diritto, i 95.000 sono **aumentati per tutti di 15.000 per ogni figlio dopo il primo** | **norma certa**: lett. c). Seconda fonte: **assente** (le istruzioni AdE non riportano la formula) |
| **Ripartizione tra genitori** | 50% a ciascun genitore non legalmente ed effettivamente separato; oppure, **previo accordo**, 100% al genitore con reddito complessivo più alto | **norma certa**: lett. c). Seconda fonte: 730/2026 (colonna 7: 100, 50 o 0) |
| Genitori separati o divorziati | In mancanza di accordo, 100% al genitore **affidatario**; affidamento congiunto o condiviso: 50% ciascuno. Se il genitore affidatario non può usarla per i limiti di reddito, passa tutta al secondo, che di regola riversa l'importo all'altro | **norma certa**: lett. c). Seconda fonte: 730/2026 (colonna 8 «100% affidamento») |
| Coniuge a carico dell'altro | La detrazione per i figli spetta per intero all'altro coniuge | **norma certa**: lett. c). Seconda fonte: 730/2026 |
| **Coniuge mancante** («in luogo del primo figlio») | Se l'altro genitore manca o non ha riconosciuto il figlio e il contribuente non è coniugato (o si è separato), o se i figli adottivi, affidati o affiliati sono del solo contribuente: **per il primo figlio** si applicano, se più convenienti, le detrazioni del coniuge (lett. a) | **norma certa**: lett. c), ultimo periodo. **Ancora in vigore**. **prassi-interpretazione** (limite d'età): vale per il primo figlio **da 21 anni** (circ. 4/E 2022 § 1.4; 730/2026); non per il figlio del coniuge deceduto (circ. 4/E 2025 § 1.3; 730/2026, CU 2026) |
| **Ascendenti** | 750 euro per ogni ascendente **che conviva** con il contribuente, ripartiti pro quota tra gli aventi diritto; fattore (80.000 − R) / 80.000 | **norma certa**: lett. d), nel testo della L. 207/2024 c. 11 lett. a) n. 2. Seconda fonte: 730/2026 (tabella 5), circ. 4/E 2025 § 1.3 |
| **Altri familiari** dell'art. 433 c.c. (coniuge separato, generi, nuore, suoceri, fratelli e sorelle, discendenti dei figli) | **Nessuna detrazione dal 2025**, anche se conviventi o con assegni alimentari | **norma certa** (lett. d) senza più il rinvio all'art. 433). Seconda fonte: 730/2026, circ. 4/E 2025 § 1.3 |
| **Famiglie numerose** (1.200 euro) | **Non esiste più**: c. 1-bis abrogato | **norma certa**: Normattiva («comma abrogato dal D.Lgs. 230/2021»). Seconda fonte: CU 2026 (p. 32), circ. 4/E 2022 nota 32 (abrogato dal 01/03/2022) |
| **Limite di reddito del familiare** (c. 2) | Reddito complessivo non superiore a **2.840,51** euro al lordo degli oneri deducibili, anche contando le retribuzioni di enti internazionali, rappresentanze diplomatiche e consolari, Santa Sede; **4.000** per i figli di età non superiore a 24 anni | **norma certa**: art. 12 c. 2. Seconda fonte: 730/2026 e circ. 4/E 2025 nota 27 (stessi importi) |
| Cosa si somma al limite | Oltre al reddito complessivo: cedolare secca sugli affitti, quota esente dei redditi di frontiera, regimi sostitutivi (vantaggio, forfetario), mance con sostitutiva | **prassi-interpretazione**: 730/2026 (cap. «Familiari a carico»), riferita al 2025; **da verificare** che l'elenco valga identico per il 2026 |
| Età fino a 24 anni, quando si misura | Il requisito è rispettato se sussiste anche per una sola parte dell'anno (unitarietà del periodo d'imposta) | **prassi-interpretazione**: 730/2026 (frontespizio, casella «soggetto fiscalmente a carico»). È scritta per la dichiarazione: **da verificare** che valga così per la ritenuta mensile |
| **Familiari residenti all'estero** (c. 2-bis) | Le detrazioni non spettano ai contribuenti **non cittadini italiani, UE o SEE** per i familiari residenti all'estero | **norma certa**: c. 2-bis (L. 207/2024 c. 11 lett. b). Seconda fonte: CU 2026 (p. 49), 730/2026 |
| **Rapportata a mese** (c. 3) | Le detrazioni «sono rapportate a mese e competono dal mese in cui si sono verificate a quello in cui sono cessate le condizioni richieste» | **norma certa**: c. 3. Seconda fonte: circ. 4/E 2022 § 1.4 e 4/E 2025 § 1.3 |
| Quando inizia e finisce la detrazione dei figli | Dal **mese del compimento dei 21 anni** fino al **mese antecedente** al compimento dei 30 | **prassi-interpretazione**: circ. 4/E 2025 § 1.3; 730/2026 (colonna 10: figlio nato ad agosto 2004 e 21 anni ad agosto 2025 → 5 mesi) |
| **Rapporti e arrotondamento** (c. 4) | Rapporto lett. a) n. 1 uguale a 1 → 690; rapporti lett. a) nn. 1 e 3 uguali a zero → non compete; rapporti lett. c) e d) zero, negativi o uguali a uno → non compete; negli altri casi il rapporto «si assume nelle prime quattro cifre decimali» | **norma certa**: c. 4. Il testo non dice se troncare o arrotondare: **da verificare** (la ricerca `arrotondamenti-norma.md` non ha una regola per questo) |
| **Reddito complessivo** (c. 4-bis) | Assunto al netto del reddito dell'abitazione principale e delle pertinenze di cui all'art. 10 c. 3-bis | **norma certa**: c. 4-bis |

**Verifica aritmetica sul testo** (non è una fonte, serve a controllare il codice): coniuge con R = 40.000 → 690; con R = 60.000 → 690 × 20.000 / 40.000 = 345; con R = 80.000 → rapporto zero, non compete. Un figlio con R = 47.500 → 950 × 0,5 = 475; due figli (soglia 110.000) con R = 55.000 → 475 ciascuno. Un ascendente con R = 40.000 → 750 × 0,5 = 375. Dalla formula, il figlio non dà più nulla da 95.000 (da 110.000 con due figli, 125.000 con tre).

## Tema 2. Art. 12 del D.Lgs. 117/2026 e correttivo D.Lgs. 148/2026

Testo letto su Normattiva (`urn:nir:stato:decreto.legislativo:2026-06-19;117:1~art12`), applicazione dal 01/01/2027 (art. 377, già letto il 07/11/2026 in `parametri-fiscali-2026-2027.md`).

**Confronto numerico.** Estratti tutti i numeri dai due testi e messi a confronto: **identici** (800, 110, 15.000, 690, 40.000, 80.000, 10/20/30 e le fasce 29.000-35.200, 950, 95.000, 15.000 per figlio, 750, 80.000, 2.840,51, 4.000, 433). Le uniche differenze sono i numeri delle note di aggiornamento. **norma certa**, confronto fatto in questa sessione sul testo dei due atti. Seconda fonte per il 2027: **assente** (nessuna istruzione AdE per il 2027).

| TUIR 2026 | TU 2027 (D.Lgs. 117/2026) | Contenuto |
|---|---|---|
| c. 1 lett. a), b), c), d) | c. 1 lett. a), b), c), d) | Stessi importi e stessi testi. Differenze solo di forma («euro 800» al posto di «800 euro»; «figli nati fuori del matrimonio» al posto di «figli naturali» nell'ultimo periodo della lett. c) |
| c. 1-bis (abrogato) | non esiste | Famiglie numerose |
| c. 2 | c. 2 | Limiti di reddito 2.840,51 e 4.000 |
| c. 2-bis | **c. 3** | Esclusione dei familiari extra-UE residenti all'estero |
| c. 3 | **c. 4** | Rapportata a mese |
| c. 4 | **c. 5** | Rapporti e quattro decimali |
| c. 4-bis | **c. 6** | Reddito al netto dell'abitazione principale; il rinvio passa da «art. 10 c. 3-bis» a **«art. 10 c. 5»** |
| c. 4-ter | **c. 7** | Familiari fiscalmente a carico e art. 433 c.c. |

**Il comma 7 e il correttivo.** Il testo del c. 4-ter TUIR / c. 7 TU dice: quando una disposizione fiscale richiama le persone dell'art. 12 si considerano, anche senza detrazione, il coniuge non separato, i figli (nati fuori del matrimonio riconosciuti, adottivi, affiliati o affidati, conviventi del coniuge deceduto) e **le altre persone elencate nell'art. 433 c.c.**; se si richiamano anche le condizioni del c. 2, o i «familiari fiscalmente a carico», contano quelle con reddito non superiore ai limiti del c. 2.

Che cosa cambia (D.Lgs. 148/2026 art. 1 c. 1-2):

- **Primo periodo**: si **tolgono** le parole «che convivono con il contribuente o percepiscono assegni alimentari non risultanti da provvedimenti dell'autorità giudiziaria». Prima (testo del D.Lgs. 192/2025, citato dalle istruzioni CU 2026) la condizione di convivenza o di assegni alimentari riguardava le «altre persone» già nel primo periodo.
- **Secondo periodo**: si **aggiunge in fine** «e, limitatamente alle altre persone elencate nell'articolo 433 del codice civile, che convivono con il contribuente o percepiscono assegni alimentari non risultanti da provvedimenti dell'autorità giudiziaria».
- **Da quando**: art. 1 c. 3: dal **periodo d'imposta in corso alla data del 20/12/2025**, cioè dal **2025**. Vale quindi anche per il 2026 e per il 2027. Il D.Lgs. 148/2026 è in vigore dal 12/08/2026 (art. 37).

**norma certa** per il testo e la decorrenza (testo del decreto e note (250) di Normattiva per l'art. 12 TUIR e (3) per il TU).

**Effetto pratico** (**prassi-interpretazione**, lettura mia: nessun testo AdE successivo al 148 è stato letto): le «altre persone» dell'art. 433 c.c. contano come familiari nel senso largo, senza condizione di convivenza, ma contano come «fiscalmente a carico» solo se entro il limite di reddito **e** conviventi o con assegni alimentari. **Le detrazioni del c. 1 non cambiano** (la lett. d) resta ai soli ascendenti conviventi). Cambia dove un'altra norma richiama il c. 4-ter: oneri detraibili e deducibili per i familiari, welfare dell'art. 51 TUIR (art. 53 c. 2 del TU). Le istruzioni CU 2026 riportano ancora la formulazione del D.Lgs. 192/2025, precedente al 148: **da verificare** che la CU 2027 le adegui.

## Tema 3. Come il sostituto applica le detrazioni

| Punto | Esito | Marcatura e fonte |
|---|---|---|
| **Dichiarazione**: serve per i carichi | Le detrazioni dell'art. 12 sono riconosciute **se il percipiente dichiara di avervi diritto, indica le condizioni di spettanza, il codice fiscale dei soggetti per i quali si usufruisce delle detrazioni e si impegna a comunicare tempestivamente le variazioni**; la dichiarazione **ha effetto anche per i periodi d'imposta successivi** | **norma certa**: art. 23 c. 2 lett. a) D.P.R. 600/1973 (letto con `!vig=2026-11-09`); dal 2027 art. 33 c. 3 lett. a) D.Lgs. 33/2025 (stesso testo, rinvio agli artt. 12 e 13 c. 1-9 del TU) |
| Sanzione per omessa comunicazione delle variazioni | Sanzioni dell'art. 11 D.Lgs. 471/1997 | **norma certa** per il 2026 (art. 23 c. 2 lett. a). Nel testo di D.Lgs. 33/2025 art. 33 c. 3 lett. a) letto **la frase non c'è**: **da verificare** dove sia collocata dal 2027 |
| Contenuto della dichiarazione sul «come» | La legge non ha un modulo né elenca i campi oltre a quelli sopra | **norma certa** (assenza nel testo letto). Nel testo del 2026 c'è un periodo «soppresso dalla L. 244/2007» di cui Normattiva non riporta il contenuto: **da verificare** |
| **Percentuale** | La quota di detrazione la dichiara il sostituito. Per i figli, valori 100 (tutta), 50 (ripartita) o 0 (tutta all'altro genitore); «C» sul primo figlio se spetta la detrazione del coniuge; per ascendenti e altri familiari, la percentuale con cui si è obbligati (in parti uguali tra gli aventi diritto) | **prassi-interpretazione**: 730/2026 (colonna 7) e CU 2026 (p. 49). **Riserva sulla circolare 326/E del 1997**: dice che la percentuale è «liberamente indicata» dal sostituito, senza indagini del sostituto. È anteriore alla L. 244/2007 (ripartizione fissa al 50% o 100% con accordo): oggi vale il testo dell'art. 12 c. 1 lett. c) |
| Controlli del sostituto | Nessuna indagine sulle motivazioni della percentuale | **prassi-interpretazione**: circ. 326/E 1997 § 3.4, anteriore alla L. 244/2007. **da verificare** che la regola valga ancora nella parte sul reddito del familiare dichiarato |
| **Periodo di paga e ragguaglio** | L'anno si intende diviso in **12 mesi, 24 quindicine, 52 settimane e 365 giorni** (anche negli anni bisestili) | **prassi-interpretazione**: circ. 326/E 1997 § 3.3 (letta su copia). **da verificare** che sia ancora valida |
| **Mese o 1/12 per i carichi?** | La norma dei carichi (c. 3 TUIR) dice «rapportate a **mese**», per i mesi in cui le condizioni sussistono. Il testo non dice quale importo si trattiene in un mese di paga | **norma certa** per il c. 3. L'applicazione per periodo di paga (1/12 dell'importo annuo per ogni mese a carico) è **da verificare**: **nessuna fonte letta la scrive per i carichi** |
| **Mensilità aggiuntive** (tredicesima, ecc.) | La lett. b) dell'art. 23 c. 2 dice solo di applicare le aliquote ragguagliando a mese gli scaglioni, **senza** citare le detrazioni | **norma certa** per il testo; l'effetto (i carichi non si applicano sulle mensilità aggiuntive e si recuperano al conguaglio) è **prassi-interpretazione**, **da verificare** |
| **Conguaglio** | Entro il 28 febbraio dell'anno dopo o alla cessazione. Si tiene conto delle detrazioni degli artt. 12 e 13 spettanti; il sostituto corregge quelle che variano col reddito | **norma certa**: art. 23 c. 3 D.P.R. 600/1973 (art. 33 c. 4 D.Lgs. 33/2025 dal 2027). **prassi-interpretazione**: circ. 326/E 1997 § 3.5 («detrazioni spettanti e richieste, anche se non considerate nel corso dell'anno») |
| **Rapporto inferiore all'anno** | Il sostituto calcola le detrazioni per carichi di famiglia **in relazione al periodo di lavoro**, salvo richiesta espressa del sostituito di fruirne per l'intero anno; in tal caso informa il percipiente con il codice di annotazione **AC** | **prassi-interpretazione**: istruzioni CU 2026 (p. 32). Non è chiaro come si concilii con la regola dei mesi a carico del c. 3: **da verificare** |
| **Campi dei familiari nella CU 2026** | Grado di parentela: «C» coniuge, «F1» primo figlio, «F» figli successivi, «G» ascendenti, «D» figlio con disabilità, «P» altri familiari; **codice fiscale**; **mesi a carico**; **percentuale** (lettera «C» se al primo figlio spetta la detrazione del coniuge per l'intero anno); casella **affidamento esclusivo, congiunto o condiviso con detrazione al 100%**; **mesi di detrazione per figli da 21 a 29 anni** | **norma certa** (istruzioni CU 2026, p. 49, per ciò che dicono del modello) |
| Dati da indicare anche senza detrazione | Il familiare va indicato **anche se la detrazione non spetta** (figli sotto i 21 o sopra i 30), con il codice fiscale; il codice fiscale del coniuge anche se non è a carico | **norma certa**: CU 2026 (p. 49); 730/2026 (stessa regola) |
| **Minore di tre anni** | **Non esiste più**: la maggiorazione è cessata dal 01/03/2022 | **norma certa**: CU 2026 (p. 32). Il campo non è nel prospetto della CU 2026 |
| Quando va compilata la sezione | Solo se il sostituto eroga redditi di lavoro dipendente, equiparati o assimilati | **norma certa**: CU 2026 (p. 49) |
| **Unione civile** | «Coniuge» e termini equivalenti valgono anche per ciascuna parte dell'unione civile | **norma certa**: L. 76/2016 art. 1 c. 20, come riportato da CU 2026 e 730/2026 (testo della legge **non letto**) |
| Figlio in affido preadottivo | Nel 730 il codice fiscale **non si indica**, si indica solo il numero | **prassi-interpretazione**: 730/2026. Per la CU nessuna regola letta: **da verificare** |
| Familiare senza codice fiscale | La norma chiede il codice fiscale dei soggetti per cui si usufruisce della detrazione | **norma certa** per il requisito; la conseguenza (detrazione non riconosciuta in corso d'anno) è lettura mia, **da verificare** |

## Tema 4. Art. 16-ter e riduzione di 440 euro

Testo letto: art. 16-ter TUIR con `!vig=2026-11-09` e L. 207/2024 art. 1 c. 10.

| Punto | Esito | Marcatura e fonte |
|---|---|---|
| **Che cosa riduce l'art. 16-ter** | Per redditi complessivi **sopra 75.000**, gli **oneri e le spese** per cui c'è una detrazione dall'imposta lorda, considerati complessivamente, sono ammessi fino a un importo base × un coefficiente. Importo base: **14.000** tra 75.000 e 100.000; **8.000** oltre 100.000. Coefficiente: **0,50** senza figli, **0,70** con un figlio, **0,85** con due, **1** con più di due o con almeno un figlio disabile | **norma certa**: art. 16-ter c. 1-3. Seconda fonte: 730/2026, tabella 11 (importi 7.000/9.800/11.900/14.000 e 4.000/5.600/6.800/8.000) |
| **I carichi dell'art. 12 sono dentro il tetto?** | **No**: il testo parla di «oneri e spese». I carichi sono un'altra detrazione (art. 12). Le istruzioni 730/2026 descrivono il tetto sugli «oneri e spese detraibili» e il numero dei figli a carico entra solo come **coefficiente** | **prassi-interpretazione**: lettura del testo e delle istruzioni 730/2026. Non ho trovato una frase AdE che dica esplicitamente che i carichi sono esclusi: **da verificare** |
| **Figli che contano per il coefficiente** | Quelli «presenti nel nucleo familiare» che si trovano nelle condizioni dell'art. 12 c. 2 (cioè entro il limite di reddito), **compresi i minori di 21 anni** | **norma certa**: art. 16-ter c. 1 e 3. Quindi la formula dell'art. 12 dei figli (da 21 a 30) e il coefficiente del 16-ter **contano figli diversi** |
| **440 euro sopra 200.000** (art. 16-ter c. 5-bis, L. 199/2025 c. 4) | Riduce di 440 euro la detrazione per: oneri al 19% (esclusa la spesa sanitaria), erogazioni ai partiti, premi per eventi calamitosi. **Non** riguarda i carichi di famiglia | **norma certa**: c. 5-bis (elenco tassativo nelle lettere a-c). Per ADR 0019 (08/11/2026) **resta fuori dal corpus** |
| **Effetto sulle formule dell'art. 12** | Nessuna interazione diretta. In ogni caso le detrazioni dei carichi **si azzerano da sole** ad alti redditi: coniuge e ascendenti da 80.000, figli da 95.000 (soglia più alta con più figli) | **norma certa**: formule dell'art. 12 c. 1 |
| **Interazione con il trattamento integrativo** | La somma delle detrazioni da confrontare con l'imposta lorda (reddito 15.001-28.000) **comprende le detrazioni per carichi di famiglia** | **prassi-interpretazione**: 730/2026 (elenco a), «Trattamento integrativo»). Fonte di legge: D.L. 3/2020 art. 1 (non riletto per questo punto): **da verificare** |
| **Dal 2027** | L'art. 16-ter diventa l'art. 18 del TU (indicato nella ricerca `parametri-fiscali-2026-2027.md`) | **da verificare** il testo: non riletto in questa sessione |

## Tema 5. Reddito complessivo nelle formule

| Punto | Esito | Marcatura e fonte |
|---|---|---|
| **Di chi è il reddito R** | Le formule usano il reddito complessivo **del contribuente che prende la detrazione** (non quello del familiare). Il reddito del **familiare** serve solo per il limite di 2.840,51 / 4.000 | **norma certa**: art. 12 c. 1 (R = reddito complessivo) e c. 2 (reddito di chi è a carico) |
| **Che cosa include** | Reddito complessivo **al netto del reddito dell'abitazione principale e delle pertinenze** (art. 10 c. 3-bis TUIR; dal 2027 art. 10 c. 5 TU: deduzione fino alla rendita catastale rapportata al periodo e alla quota) | **norma certa**: art. 12 c. 4-bis TUIR (c. 6 TU), letto con l'art. 10 |
| **Cedolare secca** | Il reddito dei fabbricati in cedolare secca si **aggiunge** al reddito complessivo per calcolare le detrazioni per carichi di famiglia | **prassi-interpretazione**: 730/2026 (tabelle 3 e 5, nota 1; capitolo «cedolare secca»). **da verificare** il fondamento di legge: non letto in questa sessione |
| **Che cosa conosce il sostituto** | Solo i redditi che paga e quelli che il sostituito dichiara (redditi di precedenti rapporti con la CU consegnata entro il 12 gennaio, su richiesta: art. 23 c. 4 D.P.R. 600/1973). Non conosce affitti, redditi esteri o d'impresa | **norma certa**: art. 23 c. 4 D.P.R. 600/1973 (letto) |
| **Reddito presunto in corso d'anno** | Per la detrazione del coniuge e per quelle del lavoro dipendente il sostituto, salva diversa indicazione del sostituito, considera il reddito di lavoro dipendente **che nel corso dell'anno corrisponde** | **prassi-interpretazione**: circ. 326/E 1997 § 3.4 (copia, anteriore a molte modifiche). Per **figli e ascendenti** il testo letto non dice lo stesso: **da verificare** che si applichi uguale |
| **Al conguaglio** | Il sostituto somma i redditi di tutti i rapporti dell'anno con lo stesso sostituito, anche senza richiesta, e corregge le detrazioni che dipendono dal reddito | **prassi-interpretazione**: circ. 326/E 1997 § 3.5. Coerente con ADR 0019 («reddito annuo stimato», poi conguaglio) |
| Redditi non conosciuti dal sostituto | Il conguaglio non può recepirli: resta il 730 o il modello Redditi del sostituito | **prassi-interpretazione** (conseguenza dell'art. 23 c. 4): nessun testo letto la scrive |

## Esito per il grilling

Scelte di modello che la norma lascia aperte, in ordine. Dove c'è una raccomandazione, è la lettura più vicina alla fonte.

1. **Come ripartire la detrazione annua nei periodi di paga.** Il c. 3 dice «a mese»; la prassi del 1997 divide l'anno in 12 mesi. Opzioni: (a) 1/12 dell'importo annuo per ogni mese a carico; (b) importo annuo × giorni / 365, come ADR 0019 fa per la detrazione di lavoro dipendente. *Raccomandazione:* (a), perché la norma dei carichi parla di mese, con avviso. Nessun testo letto fissa il criterio mensile della ritenuta.
2. **A quale mese appartiene la condizione.** Mese di paga o mese di competenza? Conta per arretrati, mensilità aggiuntive e figli che compiono 21 o 30 anni a metà anno. *Raccomandazione:* mese di paga per la ritenuta; i mesi veri nel conguaglio.
3. **Mensilità aggiuntive.** Il testo dell'art. 23 c. 2 lett. b) non cita detrazioni. *Raccomandazione:* nessuna detrazione sulle mensilità aggiuntive in corso d'anno; la correzione resta al conguaglio. **da verificare**.
4. **Reddito R in corso d'anno.** Quello presunto del 1997 (redditi pagati dall'ente proiettati sull'anno, più altri redditi dichiarati). Si ricalcola ogni mese o si fissa a gennaio? *Raccomandazione:* ricalcolare ogni mese con la stima di ADR 0019; il conguaglio corregge.
5. **Familiare senza codice fiscale.** La norma lo chiede. *Raccomandazione:* senza codice fiscale la detrazione di quel familiare non si applica in ritenuta, con avviso; il fermo con nome solo se il conguaglio la riconoscerebbe. Eccezione da decidere: figlio in affido preadottivo (730 senza CF).
6. **Dati minimi della dichiarazione per familiare.** Relazione (coniuge, figlio, figlio disabile, ascendente convivente), codice fiscale, mesi a carico (o data di inizio e fine), percentuale (100, 50, 0, «C»), casella affidamento al 100%, dichiarazione di reddito del familiare entro il limite (2.840,51 o 4.000 fino a 24 anni), conviventi per gli ascendenti, residenza all'estero. *Raccomandazione:* questi campi, senza altri; la data di nascita si prende dall'anagrafica.
7. **Coniuge mancante («C» sul primo figlio).** La legge dice «se più convenienti»; la prassi chiede il figlio ≥ 21 anni. Chi sceglie la più favorevole? *Raccomandazione:* la sceglie il sostituito nella dichiarazione; il modello applica quella indicata e il conguaglio non la cambia da solo.
8. **Validità della dichiarazione.** La norma dice che vale anche per gli anni dopo e impone di comunicare le variazioni. *Raccomandazione:* il fatto non scade, ma il modello avvisa quando cambia l'età del figlio (21 o 30 anni) o a gennaio chiede conferma. Nessuna regola di legge sul rinnovo.
9. **Percentuali.** Il modello accetta solo 100, 50 e 0 per i figli, e una quota in parti uguali per ascendenti? Nessun controllo incrociato con l'altro genitore, anche se è dipendente dello stesso ente? *Raccomandazione:* sì; nessun controllo (la circolare del 1997 lo esclude, ma è anteriore alla L. 244/2007).
10. **Versioni 2026 e 2027.** Gli importi sono identici: due versioni datate, la seconda con il riferimento all'art. 12 del TU e la nuova numerazione dei commi (tema 2). La regola datata si sceglie sulla data di pagamento (ADR 0019 e `parametri-fiscali-2026-2027.md`, tema 9 e voce 10). *Raccomandazione:* confermare.
11. **Correttivo 148/2026.** Per le detrazioni del c. 1 non cambia nulla; riguarda oneri e welfare. *Raccomandazione:* nessun intervento ora; verificarlo quando si leggono gli artt. 15 e 53 c. 2 del TU.
12. **Rapporto inferiore all'anno.** La CU dice di calcolare sul periodo di lavoro, salvo richiesta del sostituito per l'intero anno. Il modello lo fa solo al conguaglio? *Raccomandazione:* per i carichi vale già la regola dei mesi a carico; la richiesta dell'intero anno resta un'opzione della dichiarazione, **da verificare**.

## Cosa resta da verificare

- Criterio mensile della ritenuta per i carichi e rapporto con la regola dei giorni su 365 della circolare 326/E del 1997 (che non parla dei carichi in modo specifico).
- Se la circolare 326/E del 1997 è ancora valida nei punti sul reddito presunto e sulla percentuale dichiarata (è anteriore alle modifiche della L. 244/2007 e ai testi attuali).
- Formula dei figli (95.000, +15.000 per figlio): **seconda fonte indipendente assente** nelle istruzioni AdE; per il 2027 non esistono istruzioni.
- Troncamento o arrotondamento del rapporto alla quarta cifra decimale.
- Sanzione per omessa comunicazione delle variazioni dal 2027: dove si trova dopo il D.Lgs. 33/2025.
- Se il limite di 2.840,51 / 4.000 si controlla con il reddito dell'anno o in modo provvisorio in corso d'anno, e il requisito d'età fino a 24 anni.
- Fonte di legge della regola sulla cedolare secca nel reddito per le detrazioni; testo della L. 76/2016 sull'unione civile.
- Art. 16-ter dal 2027 (art. 18 del TU); frase AdE esplicita sull'esclusione dei carichi dal tetto.
- Effetto pratico del correttivo 148/2026 sui richiami al c. 4-ter e istruzioni CU 2027.
- Famiglie con figlio in affido preadottivo nella CU.
- Testo di D.Lgs. 148/2026 letto su copia di ance.it; l'originale di Gazzetta Ufficiale e la ripubblicazione del 04/09/2026 con note non sono stati aperti.
- Risposta a interpello AdE 243/2025 (figli a carico e codice fiscale in CU): download non riuscito, non letta.
- Legge di bilancio 2027: eventuali modifiche all'art. 12.

## Fonti

**Normattiva** (consultate il 09/11/2026)

- TUIR: `urn:nir:stato:decreto.del.presidente.della.repubblica:1986-12-22;917~art12` (e artt. 10 e 16-ter) con `!vig=2026-11-09`.
- D.Lgs. 117/2026: `urn:nir:stato:decreto.legislativo:2026-06-19;117:1~art12` (allegato; anche art. 10).
- D.Lgs. 33/2025: `urn:nir:stato:decreto.legislativo:2025-03-24;33:1~art33` (allegato).
- D.P.R. 600/1973: `urn:nir:stato:decreto.del.presidente.della.repubblica:1973-09-29;600~art23` con `!vig=2026-11-09`.
- L. 207/2024: `urn:nir:stato:legge:2024-12-30;207~art1` (commi 10-12).
- D.Lgs. 148/2026 (07/08/2026, GU n. 185 dell'11/08/2026): copia PDF su [ance.it](https://ance.it/wp-content/uploads/allegati/DLgs_148-2026.pdf), artt. 1 e 37.

**Agenzia delle Entrate e Ministero delle Finanze**

- [Circolare 4/E del 16/05/2025](https://www.agenziaentrate.gov.it/portale/documents/20143/8410823/Circolare+lavoro+dipendente+LB2025+DD+IRPEF+n.+4+del+16+maggio+2025.pdf/36979eaa-9fc5-a4ec-a7aa-136497c53f91), § 1.3.
- [Circolare 4/E del 18/02/2022](https://www.agenziaentrate.gov.it/portale/documents/20143/4169770/Circolare+n.+4+del+18+febbraio+2022.pdf/a83fd984-2bc3-39a9-1e09-79e9a870d401), § 1.4.
- [Istruzioni Modello 730/2026](https://www.agenziaentrate.gov.it/portale/documents/20143/9764684/730_+istruzioni_2026.pdf/2ac8d27a-fa3d-ed9e-ffc1-9bf61457661e?t=1772183775348): cap. «Familiari a carico», «Riordino delle detrazioni», tabelle 3, 4, 5 e 11.
- [Istruzioni CU 2026](https://www.agenziaentrate.gov.it/portale/documents/d/guest/cu_istr_2026_agg-1-): punto 362 (p. 32) e sezione «Familiari a carico» (p. 49).
- Circolare MinFin 326/E del 23/12/1997: copia PDF su [mefop.it](https://www.mefop.it/cms/doc/17705/circolare-ministero-delle-finanze-n-326-e-23-dicembre-1997.pdf), §§ 3.3-3.5. Originale non aperto.
