# Parametri e regole fiscali 2026-2027 sulla fonte primaria

Ticket: #47 · Branch: `ticket-47-ricerca-fisco` · Data: 2026-11-07 · Serve a: ADR 0019 (sezione «Da verificare»), ADR 0023 (fermo `debito_negativo`)

## Domanda

Quali sono, sul testo vigente, i parametri e le regole fiscali che il corpus deve contenere per gli anni d'imposta 2026 e 2027? L'ADR 0019 ha deciso la struttura della ritenuta e del conguaglio e lascia senza fonte i valori. Il ticket chiede sette temi (scaglioni, detrazioni, recuperi a rate, addizionali, sostitutiva del 15%, aliquota media, 730-4). Si aggiungono due temi nati dal lavoro sul mese di prova: la rilettura dell'art. 51 c. 2 TUIR e del suo successore dal 01/01/2027 (tema 8), e come il sostituto recupera un conguaglio a credito che supera le ritenute del mese nella delega F24EP di dicembre (tema 9).

## Legenda e come sono state lette le fonti

- **norma certa**: testo di legge o regolamento letto in questa sessione, oppure provvedimento dell'amministrazione titolare (risoluzione istitutiva di codici, istruzioni dei modelli) per ciò che dice del modello stesso.
- **prassi-interpretazione**: parere AdE (risposta a interpello, istruzioni, FAQ), oppure lettura ricavata da più fonti concordi.
- **da verificare**: non confermato su fonte primaria in questa sessione.

Aperti e letti per intero, il 07/11/2026:

- **Normattiva** (portale, pagina dell'articolo): TUIR artt. 11, 12, 13, 19, 21, 51 con `!vig=2026-11-07`; D.Lgs. 117/2026 (testo unico imposte sui redditi, in vigore dal 04/07/2026, applicazione dal 01/01/2027 per l'art. 377): scaricati tutti i 391 articoli e cercati per parola (trattamento integrativo, addizionali, aliquota media), letti per intero gli artt. 11, 12, 13, 21, 23, 53, 376, 377; D.L. 3/2020 artt. 1-2; L. 207/2024 art. 1 commi 1-100; L. 199/2025 art. 1 commi 1-100 e 201-300; D.Lgs. 360/1998 art. 1; D.Lgs. 446/1997 art. 50; D.P.R. 600/1973 art. 23; D.P.R. 445/1997 art. 1; D.Lgs. 175/2014 art. 15; D.Lgs. 241/1997 art. 20; D.M. 164/1999 artt. 19-20; D.Lgs. 33/2025 artt. 33 e 243 dell'allegato; D.Lgs. 141/2026 (05/08/2026) artt. 73 e 83.
- **Agenzia delle Entrate** (PDF): risoluzione 4/E del 29/01/2026; risoluzione 103/E del 09/12/2015; circolare 23/E del 20/04/2007; tabella codici F24EP aggiornata al 01/10/2026; istruzioni Modello 770/2026; istruzioni Modello 730/2026; istruzioni CU 2026.
- **Risposte a interpello 173/2026 e 186/2026**: testo letto su copie PDF ospitate da siti terzi (lentepubblica.it, studiopizzano.it); l'originale sul sito AdE non è stato aperto. Il testo della 173 dice di essere stata pubblicata il 15/09/2026; la data della 186 (ottobre 2026) viene dai risultati di ricerca, non dal testo.

Note sul metodo:

- Per le leggi e il testo unico la pagina di Normattiva mostra il testo consolidato più recente: include già le abrogazioni dal 01/01/2027 (per esempio L. 207/2024 c. 6 e L. 199/2025 c. 9 compaiono come «abrogato dal D.Lgs. 117/2026»). Per il TUIR si è usato `!vig=2026-11-07`, che mostra il testo del 2026.
- **Aliquote e importi con seconda fonte indipendente (ADR 0003)**: dove la riga dice «due fonti» sono stati confrontati due atti distinti (per esempio testo di legge e istruzioni AdE). Dove manca, lo dice la riga. Per i valori 2027 la seconda fonte non esiste ancora: l'AdE non ha istruzioni per i redditi 2027.
- **Il vault-pa** è stato usato solo come pista (pagine su ris. 4/E 2026, risposta 173/2026 e tabella F24EP). Nessuna affermazione si regge sul vault.
- Nessun dato reale, nessun nome di ente.
- Il disegno di legge di bilancio 2027 (testo bollinato del 30/10/2026, secondo i risultati di ricerca) non è stato letto: ogni punto che può cambiare con la legge di bilancio è marcato **da verificare**.

## Sintesi

1. **Scaglioni**: 23% fino a 28.000, 33% da 28.000 a 50.000, 43% oltre, **uguali nel 2026 e nel 2027**. Per il 2026 vengono da L. 199/2025 art. 1 c. 3 (35% → 33%); per il 2027 dall'art. 11 c. 1 del D.Lgs. 117/2026. Per il 2025 l'AdE mostra ancora il 35%.
2. **Detrazioni artt. 12 e 13**: gli importi del TU 2027 sono identici a quelli del TUIR 2026 (confronto numerico). Cambia il comma: l'**ulteriore detrazione** della L. 207/2024 c. 6 (abrogato) è dal 2027 l'art. 13 c. 10 del TU. La **somma esente** (L. 207/2024 c. 4) e il **trattamento integrativo** (D.L. 3/2020 art. 1) restano nelle loro leggi.
3. **Recuperi a rate oltre 60 euro**: 8 rate per il trattamento integrativo, **10 rate** per la somma esente **e** per l'ulteriore detrazione. Ora hanno la fonte di legge (non solo le istruzioni CU).
4. **Addizionali**: acconto comunale 30% (aliquota e soglia dell'anno precedente), al massimo 9 rate da marzo; regionale senza acconto; saldo da conguaglio in al massimo 11 rate; alla cessazione in unica soluzione. D.Lgs. 360/1998 e 446/1997 **non sono abrogati** dal D.Lgs. 117/2026 né citati come abrogati dal D.Lgs. 141/2026.
5. **Sostitutiva 15% sull'accessorio**: vale **solo per il 2026** (testo della legge). Tetto 800 euro per anno, reddito di lavoro dipendente del 2026 fino a 50.000 (comprese pensioni e più rapporti), assimilati esclusi, eccedenza a tassazione ordinaria. Una proroga al 2027 è nel disegno di legge di bilancio, non ancora legge.
6. **Aliquota media**: il ticket e l'ADR parlano di art. 19 TUIR, ma il «reddito del biennio» è nell'**art. 21 TUIR** (art. 23 del TU). L'art. 19 (art. 21 del TU) riguarda il TFR, con l'aliquota dell'anno di maturazione e la riliquidazione dell'ufficio sui cinque anni.
7. **730-4**: rate da 2 a 6 (5 per i pensionati), da concludere con la retribuzione di novembre; interesse 0,33% mensile sulle rate successive e 0,4% mensile sul residuo per incapienza; nessuna operazione sotto 12 euro; per i cessati il sostituto non opera i debiti e avvisa. Il 730-4 con credito che eccede le ritenute ha una regola propria (D.M. 164/1999 art. 19 c. 2).
8. **Art. 51 c. 2 TUIR → art. 53 c. 2 TU** (tema 8): stesso contenuto, **lettere rinumerate**. L'unica differenza di importo è formale: il TUIR 2026 ha ancora «lire 4 milioni» alla lettera g), il TU «euro 2.065,83» alla lettera l).
9. **Conguaglio a credito oltre le ritenute** (tema 9): la fonte c'è. Il credito va in righe **a credito** (155E, 160E, 161E), mai come debito negativo su 100E; si compensa contro tutto il debito della delega; il saldo del modello non può essere negativo; l'eccedenza oltre il debito della delega **non si espone** e passa alle deleghe successive come credito del sostituto. Il fermo `debito_negativo` dipende dalla rappresentazione scelta nel modello, non da una lacuna di legge.

## Tema 1. Scaglioni e aliquote IRPEF 2026 e 2027

| Punto | Esito | Marcatura e fonte |
|---|---|---|
| Aliquote 2026: 23% fino a 28.000 euro; 33% oltre 28.000 e fino a 50.000; 43% oltre 50.000 | Il secondo scaglione passa da 35% a 33% | **norma certa**: art. 11 c. 1 TUIR vigente al 07/11/2026 (`((33 per cento))`) e L. 199/2025 art. 1 c. 3, in vigore dal 01/01/2026. Seconda fonte: **art. 11 c. 1 del D.Lgs. 117/2026**, atto distinto, stessi valori |
| La riduzione è strutturale, non per un solo anno | Sì: la L. 199/2025 sostituisce le parole nel testo del TUIR, senza termine | **norma certa**: art. 1 c. 3 L. 199/2025. La legge non dice «dal periodo d'imposta 2026»: l'effetto dal 2026 discende dall'entrata in vigore dal 01/01/2026 (**prassi-interpretazione**) |
| Il 2025 resta al 35% | Il 33% non vale per i redditi 2025 | **norma certa** (L. 207/2024 art. 1 c. 2 lett. a, con 35%); coerente con le **istruzioni 730/2026** per i redditi 2025, che mostrano ancora «6.440,00 + 35%» sopra 28.000 |
| Aliquote 2027 | Identiche: 23/33/43, stessi limiti | **norma certa**: art. 11 c. 1 D.Lgs. 117/2026. Applicazione dal 01/01/2027 (art. 377). Seconda fonte indipendente: **assente** (nessuna istruzione AdE per il 2027) |
| Imposta lorda ai limiti | 6.440 euro a 28.000; 7.260 euro nel secondo scaglione (22.000 × 33%); 13.700 euro a 50.000 | Calcolo aritmetico sul testo; il 6.440 coincide con la tabella delle istruzioni 730/2026 |
| La legge di bilancio 2027 può cambiare gli scaglioni | Non risulta nulla in questo senso nelle fonti lette | **da verificare** quando la legge sarà pubblicata |
| Riduzione di 440 euro delle detrazioni per oneri sopra 200.000 euro di reddito (L. 199/2025 c. 4, art. 16-ter c. 5-bis) | Fuori dal perimetro delle ritenute mensili | **norma certa** (testo letto). Nel conguaglio degli enti locali tocca solo i redditi sopra 75.000 (art. 16-ter, art. 18 del TU): **da verificare** se serve nel corpus |

**Come si applicano alla ritenuta.** L'art. 23 c. 2 lett. a) D.P.R. 600/1973 (art. 33 c. 3 lett. a del D.Lgs. 33/2025 dal 2027) chiede gli scaglioni «ragguagliati al periodo di paga» e le detrazioni degli artt. 12 e 13 «rapportate al periodo stesso»: **norma certa**, già in ADR 0019.

## Tema 2. Detrazioni artt. 12 e 13, ulteriore detrazione, somma esente, trattamento integrativo

### Valori 2026 e 2027

| Voce | Formula e limiti | Marcatura e fonte |
|---|---|---|
| **Art. 13 c. 1** (lavoro dipendente), 2026 | a) 1.955 euro fino a 15.000 (minimo 690; **tempo determinato: minimo 1.380**); b) 1.910 + 1.190 × (28.000 − R) / 13.000 da 15.000 a 28.000; c) 1.910 × (50.000 − R) / 22.000 da 28.000 a 50.000. Rapportata al periodo di lavoro | **norma certa**: art. 13 c. 1 TUIR vigente al 07/11/2026. Seconda fonte: **tabella delle istruzioni 770/2026** (1.955; 1.910 + 1.190 × …; 1.910 × …) |
| **+65 euro** | Se il reddito complessivo è sopra 25.000 e fino a 35.000 | **norma certa**: art. 13 c. 1.1 TUIR; due fonti (istruzioni 770/2026, nota 4 della tabella) |
| Art. 13 c. 1, 2027 | Importi identici | **norma certa**: art. 13 c. 1 e 2 del D.Lgs. 117/2026 (confronto numerico con il TUIR: stessi numeri) |
| Pensioni (c. 3-4 TU) e altri redditi (c. 5-7 TU) | Identiche nei due testi | **norma certa**: confronto numerico art. 13 TUIR/TU. Fuori dal perimetro dei dipendenti, ma servono per i pensionati e gli assimilati |
| Arrotondamento del rapporto | Si assume nelle prime quattro cifre decimali | **norma certa**: art. 13 c. 6 TUIR (c. 8 del TU). Coincide con `arrotondamenti-norma.md` |
| **Art. 12** (carichi di famiglia) | Coniuge 800 − 110 × R/15.000; 690 tra 15.000 e 80.000 con riduzione; 950 euro per figlio dai 21 ai 30 anni o disabile; ripartizione al 50% | **norma certa**: art. 12 TUIR e art. 12 TU. Confronto numerico: **importi identici**; le differenze sono solo note e rinvii |
| **Ulteriore detrazione** (lavoro dipendente, esclusi i pensionati) | 1.000 euro se il reddito complessivo è sopra 20.000 e fino a 32.000; 1.000 × (40.000 − R) / 8.000 sopra 32.000 e fino a 40.000. Rapportata al periodo di lavoro | **norma certa**: dal 2027 **art. 13 c. 10 D.Lgs. 117/2026**; per il 2026 L. 207/2024 art. 1 c. 6 (oggi mostrato come abrogato, testo ripreso dal TU). Seconda fonte: istruzioni CU 2026 punto 368, stessi valori |
| **Somma esente** (L. 207/2024 art. 1 c. 4-5) | Reddito complessivo fino a 20.000: percentuale sul reddito di lavoro dipendente: **7,1%** fino a 8.500; **5,3%** da 8.500 a 15.000; **4,8%** oltre 15.000. Il reddito è rapportato all'intero anno solo per scegliere la percentuale | **norma certa**: art. 1 c. 4-5 L. 207/2024, nel testo consolidato più recente (non è nell'elenco delle abrogazioni dell'art. 376 D.Lgs. 117/2026). Seconda fonte: istruzioni CU 2026. Il testo **non ha termine**: vale anche nel 2027. **da verificare** nella legge di bilancio 2027 |
| **Trattamento integrativo** (D.L. 3/2020 art. 1) | 1.200 euro (dal 2021) se il reddito complessivo non supera 15.000 e l'imposta lorda supera la detrazione dell'art. 13 c. 1 **diminuita di 75 euro** rapportati al periodo (L. 207/2024 c. 3). Da 15.000 a 28.000: pari alla differenza fra la somma delle detrazioni elencate e l'imposta lorda, al massimo 1.200 | **norma certa**: art. 1 c. 1 D.L. 3/2020 vigente. Non è nell'elenco delle abrogazioni del D.Lgs. 117/2026. Seconda fonte: istruzioni CU 2026 (punto 393 e commento) |
| Rinvii dei testi 2026 ai vecchi articoli | Il D.L. 3/2020 e la L. 207/2024 citano gli artt. 49, 50 e 13 TUIR | **norma certa**: art. 376 c. 2 D.Lgs. 117/2026: i rinvii alle norme abrogate valgono per le «corrispondenti disposizioni» del TU, salvo diversa previsione e fuori dei casi di abrogazione per incompatibilità |

**Differenza da tenere presente.** La condizione del secondo periodo del trattamento integrativo guarda a oneri «sostenuti fino al 31 dicembre 2021» (mutui contratti fino a quella data): il corpus deve portarla come condizione datata, non come formula generale.

**Rapportare al periodo.** Il testo di L. 207/2024 c. 4 dice che la somma si applica «al reddito di lavoro dipendente del contribuente». Come si ripartisce nei periodi di paga dell'anno non è scritto: sostituti «riconoscono in via automatica» (c. 7) e verificano al conguaglio. **da verificare** il criterio mensile (prassi dei programmi paga, nessun testo letto).

## Tema 3. Recuperi a rate oltre 60 euro nel conguaglio

| Punto | Esito | Marcatura e fonte |
|---|---|---|
| Trattamento integrativo non spettante: recupero dal sostituto; se l'importo supera 60 euro, **otto rate** di pari ammontare **dalla retribuzione che sconta gli effetti del conguaglio** | Sì | **norma certa**: D.L. 3/2020 art. 1 c. 3, testo letto su Normattiva. Seconda fonte: istruzioni CU 2026 («otto rate di pari ammontare») |
| Somma esente **o** ulteriore detrazione non spettante: oltre 60 euro, **dieci rate** di pari ammontare dalla prima retribuzione su cui incide il conguaglio | La regola copre **entrambe**: il testo dice «la somma di cui al comma 4 o la detrazione di cui al comma 6» | **norma certa**: L. 207/2024 art. 1 c. 7. Seconda fonte: istruzioni CU 2026 (due passaggi). **Correzione per l'ADR 0019**: le dieci rate non valgono solo per l'ulteriore detrazione |
| Compensazione dei crediti maturati dal sostituto con l'erogazione di trattamento integrativo e somma | Sì, ex art. 17 D.Lgs. 241/1997 (art. 3 D.Lgs. 33/2025 dal 2027) | **norma certa**: D.L. 3/2020 art. 1 c. 4; L. 207/2024 art. 1 c. 8 |
| La soglia di 60 euro: per beneficio o sommata fra i benefici | Il testo dice «il predetto importo» riferito a «la somma … o la detrazione»; non chiarisce se si sommano | **da verificare** (nessun testo AdE letto lo chiarisce) |
| Recupero se il rapporto cessa prima di finire le rate | Nessun testo letto | **da verificare** |
| Dal 2027: il c. 7 rinvia a «la detrazione di cui al comma 6», che è abrogato | Per l'art. 376 c. 2 D.Lgs. 117/2026 il rinvio diventa l'art. 13 c. 10 del TU | **norma certa** per la clausola generale; **da verificare** che nessuna prassi dica altro |

## Tema 4. Addizionali regionale e comunale

| Punto | Esito | Marcatura e fonte |
|---|---|---|
| **Comunale: acconto** | 30% dell'addizionale calcolata sul reddito imponibile dell'anno precedente, con aliquota e soglia di esenzione **dell'anno precedente** | **norma certa**: art. 1 c. 4 D.Lgs. 360/1998. Seconda fonte: circolare AdE 23/E del 2007 (rinvia alla circolare 15/E del 2007, **non letta**) |
| Acconto del sostituto: **al massimo nove rate mensili a partire da marzo** | Sì | **norma certa**: art. 1 c. 5 D.Lgs. 360/1998 |
| **Comunale: saldo** | Determinato al conguaglio; trattenuto in **al massimo 11 rate**, dal periodo di paga successivo, **non oltre quello delle ritenute versate a dicembre** | **norma certa**: art. 1 c. 5 D.Lgs. 360/1998 |
| **Regionale** | **Nessun acconto**: l'addizionale è determinata al conguaglio e trattenuta in **al massimo 11 rate**, con lo stesso limite di dicembre | **norma certa**: art. 50 c. 4 D.Lgs. 446/1997 |
| **Cessazione del rapporto** | L'addizionale residua è prelevata **in un'unica soluzione** (comunale), «nel periodo di paga in cui sono svolte le operazioni di conguaglio» (regionale) | **norma certa**: art. 1 c. 5 D.Lgs. 360/1998; art. 50 c. 4 D.Lgs. 446/1997 |
| Esenzione comunale e acconto | Se in base al reddito dell'anno precedente il percipiente rientra nella soglia deliberata, **l'esenzione vale anche per l'acconto** e il sostituto la applica da sé, senza richiesta; se poi il reddito supera la soglia, la ritenuta si opera senza sanzioni e interessi | **prassi-interpretazione**: circolare AdE 23/E del 20/04/2007 (testo letto). È del 2007: **da verificare** che non sia stata superata |
| Chi è il destinatario dell'aliquota | **Comunale**: domicilio fiscale al 1° gennaio dell'anno di riferimento. **Regionale**: la determinazione parla di residenza (c. 2), il versamento di domicilio fiscale al 1° gennaio (c. 5) | **norma certa**: art. 1 c. 4 D.Lgs. 360/1998; art. 50 c. 2 e c. 5 D.Lgs. 446/1997. Il testo regionale ha una **discrepanza interna** («residenza» / «domicilio»): **da verificare** quale vale per la ritenuta |
| Aliquote regionali | 1,23% di base; ogni regione può maggiorare con **legge regionale pubblicata entro il 31 dicembre dell'anno precedente**; i dati vanno inviati per la pubblicazione sul sito informatico entro il 31 gennaio | **norma certa**: art. 50 c. 3 D.Lgs. 446/1997. La banca dati per regione non è stata letta: **da verificare** (fonte, formato, aggiornamenti) |
| Aliquote comunali | Variate con regolamento comunale ex art. 52 D.Lgs. 446/1997, entro 0,8 punti sopra l'aliquota di compartecipazione; la deliberazione ha effetto **dalla pubblicazione** sul sito indicato dal decreto del Dipartimento politiche fiscali **31/05/2002** | **norma certa**: art. 1 c. 3 D.Lgs. 360/1998. Il sito (portale del federalismo fiscale del MEF) e il formato dei dati non sono stati aperti: **da verificare** |
| Soglia di esenzione comunale | Stabilita dallo stesso regolamento «in ragione di specifici requisiti reddituali» | **norma certa**: art. 1 c. 3-bis D.Lgs. 360/1998 |
| Presupposto | L'addizionale è dovuta se per lo stesso anno l'IRPEF, al netto delle detrazioni e dei crediti, risulta dovuta; base: reddito complessivo al netto degli oneri deducibili | **norma certa**: art. 1 c. 4 D.Lgs. 360/1998; art. 50 c. 2 D.Lgs. 446/1997 |
| **Dal 01/01/2027** | Nessun cambiamento: i due decreti **non sono nell'elenco delle abrogazioni** del D.Lgs. 117/2026 (art. 376) e il D.Lgs. 141/2026 li cita come fonti vive (art. 50 c. 4 D.Lgs. 446/1997 e art. 1 c. 5 D.Lgs. 360/1998) | **norma certa** (assenza di abrogazione nell'atto letto); il D.Lgs. 360/1998 art. 1, letto con `!vig=2027-01-02`, risulta invariato. Restano i rinvii testuali agli «articoli 49 e 50 TUIR» (e agli «artt. 46 e 47» nel testo regionale, già oggi superati): valgono per l'art. 376 c. 2 come rinvii agli artt. 51 e 52 TU |
| Codici F24EP | 384E (comunale saldo), 385E (acconto), 381E (regionale); rimborsi 153E e 154E; eccedenze 160E e 161E | **norma certa**: tabella AdE 01/10/2026; `versamenti-f24ep.md`; ris. 103/E 2015 |

Nota sull'imponibile: la circolare 23/E del 2007 dice che la base dell'addizionale è il reddito complessivo al netto dei **soli oneri deducibili** dell'art. 10 TUIR, perché le deduzioni per carichi di famiglia sono state sostituite dalle detrazioni (**prassi-interpretazione**, 2007).

## Tema 5. Sostitutiva del 15% sull'accessorio (L. 199/2025 c. 237)

| Punto | Esito | Marcatura e fonte |
|---|---|---|
| Ambito | Compensi per il trattamento economico accessorio, comprese le indennità di natura fissa e continuativa, del **personale non dirigenziale** delle amministrazioni dell'art. 1 c. 2 D.Lgs. 165/2001, incluso quello in regime di diritto pubblico | **norma certa**: art. 1 c. 237 L. 199/2025 |
| Aliquota e tetto | 15% sostitutiva di IRPEF e addizionali; **entro 800 euro** | **norma certa**: c. 237. Seconda fonte: risposta 173/2026, che cita il testo |
| Durata | **Solo il 2026** («per l'anno 2026»). Nessuna previsione per il 2027 nel testo vigente | **norma certa**: c. 237; la risposta 173/2026 conferma che l'efficacia è «espressamente circoscritta al solo periodo d'imposta 2026» |
| Limite di reddito | Titolari di reddito di lavoro dipendente **non superiore a 50.000 euro** | **norma certa** (testo del c. 237) |
| **Anno su cui si misura** | Il **2026**, lo stesso periodo d'imposta; in assenza di una previsione diversa non conta il 2025 | **prassi-interpretazione**: risposta AdE 173/2026 (15/09/2026), confermata dalla 186/2026 |
| **Che cosa conta come reddito** | Redditi di lavoro dipendente del 2026 «anche se derivanti da più rapporti di lavoro»; **comprese le pensioni** e gli assegni dell'art. 49 c. 2 TUIR | **prassi-interpretazione**: risposta 186/2026 |
| Tetto di 800 euro | **Complessivo annuo**; i compensi oltre 800 sono tassati in via ordinaria | **prassi-interpretazione**: risposte 173 e 186/2026 |
| Assimilati | **Esclusi**: la norma parla di «redditi di lavoro dipendente», non dell'art. 50 TUIR | **prassi-interpretazione**: risposta 186/2026 |
| Esclusioni espresse | Personale delle Forze di polizia e Forze armate con le agevolazioni dell'art. 45 c. 2 D.Lgs. 95/2017; per il personale SSN delle misure D.L. 73/2024 e L. 207/2024 c. 354 il beneficio **si aggiunge** | **norma certa**: c. 237. Dirigenti: esclusi in quanto il testo parla di personale «non dirigenziale» |
| Rinuncia | Salvo espressa rinuncia scritta del prestatore; con la rinuncia i compensi vanno a **tassazione separata** art. 17 c. 1 lett. a) TUIR «al ricorrere delle condizioni ivi previste» | **norma certa** per la rinuncia; **prassi-interpretazione** per l'effetto (risposta 186/2026) |
| Codici F24EP | **179E** (180E e 181E per la Valle d'Aosta): sezione Erario (F), colonna a debito; riferimento A = mese della trattenuta (`00MM`), riferimento B = anno d'imposta; «codice» ed «estremi» non compilati. Per F24: 1077, 1314, 1611, 1934, 1935 | **norma certa**: risoluzione AdE 4/E del 29/01/2026, letta sul sito AdE; coincide con la tabella del 01/10/2026 |
| Se il sostituto può applicarla in corso d'anno su una **proiezione** del reddito | Il quesito dell'istante (risposta 173) lo proponeva; l'AdE risponde solo sull'anno e non sulla proiezione | **da verificare** |
| Rapporto con il conguaglio e con la tassazione separata | Se il reddito supera 50.000 a fine anno, la sostitutiva già applicata va recuperata: nessun testo letto fissa le modalità | **da verificare** |
| **Proroga 2027** | Il disegno di legge di bilancio 2027 (testo del 30/10/2026, art. 65 secondo i risultati di ricerca) prevederebbe la stessa misura per il 2027 | **da verificare**: è un disegno di legge, non legge. Si legge solo da sintesi secondarie |

**Nota sulle maggiorazioni notturne e festive.** Il c. 10 della L. 199/2025 (15% su 1.500 euro per notturno e festivo) riguarda i lavoratori del settore privato; il c. 7 (5% sugli incrementi da rinnovi contrattuali) vale per il settore privato con reddito 2025 fino a 33.000 euro (**norma certa**, testo letto). Non toccano il personale degli enti locali.

## Tema 6. Aliquota media della tassazione separata

**Il ticket e l'ADR citano l'art. 19 TUIR, ma ci sono due regole diverse.**

| Regola | Testo | Marcatura e fonte |
|---|---|---|
| **TFR e indennità equipollenti**: l'imposta si applica con l'aliquota dell'anno di maturazione del diritto, calcolata sull'importo diviso per gli anni di commisurazione e moltiplicato per dodici; gli uffici **riliquidano** con l'aliquota media dei **cinque anni precedenti**, iscrivendo a ruolo o rimborsando | **norma certa**: art. 19 c. 1 TUIR (vigente 2026); dal 2027 **art. 21 c. 1 TU** (stesso testo) |
| Se negli anni di riferimento non c'è reddito imponibile, l'aliquota media si calcola sugli anni con reddito; se in nessuno, vale l'aliquota del primo scaglione | | **norma certa**: art. 19 c. 1-bis TUIR; art. 21 c. 2 TU |
| **Altri redditi tassati separatamente** (arretrati, ecc.): l'aliquota corrisponde alla **metà del reddito complessivo netto del contribuente nel biennio anteriore** all'anno in cui è sorto il diritto, oppure all'anno di percezione per alcune lettere | | **norma certa**: **art. 21 c. 1 TUIR**; dal 2027 **art. 23 c. 1 TU** |
| Se in uno dei due anni non c'è reddito imponibile si usa la metà del reddito netto dell'altro; **se in nessuno dei due**, l'aliquota del **primo scaglione** | Il testo prevede una regola, non un fermo | **norma certa**: art. 21 c. 3 TUIR; art. 23 c. 3 TU |
| Arretrati: l'imposta si riduce delle detrazioni degli artt. 12 e 13 c. 1 non fruite negli anni di competenza, su dichiarazione del percipiente | | **norma certa**: art. 21 c. 4 TUIR (art. 23 c. 4 TU) |
| Il sostituto applica agli arretrati l'art. 21 (non il 19) con «reddito complessivo netto» = redditi di lavoro dipendente erogati dal sostituto al sostituito **nel biennio precedente** | | **norma certa**: art. 23 c. 2 lett. c) D.P.R. 600/1973 (art. 33 c. 3 lett. c) D.Lgs. 33/2025) |

**Per ADR 0018 e 0019.** Il «reddito del biennio» è l'art. 21 TUIR (art. 23 TU), non l'art. 19. Nell'ADR 0019 l'opzione «aliquota provvisoria per la tassazione separata se manca il reddito del biennio» va distinta: se **il reddito è nullo** nel biennio, la norma dà essa stessa l'aliquota del primo scaglione (23%); se **il dato manca nel sistema** (biennio anteriore al modello), il fermo dell'ADR resta giusto. **da verificare** che il caso «biennio con reddito presso altro sostituto» si risolva con la dichiarazione del sostituito e non con il reddito pagato dal solo sostituto (il testo del D.P.R. 600 parla dei redditi «corrisposti dal sostituto»).

## Tema 7. 730-4: termini, interessi, incapienza, cessati

| Punto | Esito | Marcatura e fonte |
|---|---|---|
| Debito: trattenuto sulla prima retribuzione utile e comunque su quella del mese successivo al ricevimento del prospetto; versato con le ritenute | Sì | **norma certa**: art. 19 c. 1 D.M. 164/1999 (testo letto con le modifiche del D.L. 124/2019). Dal 2027 l'assistenza fiscale dei sostituti è l'art. 83 D.Lgs. 141/2026 (da art. 37 D.Lgs. 241/1997) |
| Credito: rimborsato con riduzione delle ritenute dovute sulla prima retribuzione utile, **usando se necessario tutte le ritenute operate** dal sostituto; se non bastano, **sulle ritenute dei mesi successivi dello stesso periodo d'imposta** | Sì | **norma certa**: art. 19 c. 2 D.M. 164/1999. Per i crediti delle dichiarazioni dell'art. 14, riduzione delle ritenute del **mese di dicembre** (c. 3) |
| Inizio e fine delle trattenute | Da luglio (o dalla prima retribuzione utile); per i pensionati dal secondo mese successivo; le rate si concludono con la retribuzione di **novembre**, versata entro il **16 dicembre** | **prassi-interpretazione**: istruzioni 730/2026 e CU 2026 (il termine segue le modifiche del D.Lgs. 1/2024) |
| Numero delle rate | Da **2 a 6** (massimo 5 per i pensionati); 730 senza sostituto da 2 a 7 | **prassi-interpretazione**: istruzioni 730/2026, colonna 7 |
| **Interessi sulle rate** | **0,33% mensile** sulle rate successive alla prima | **prassi-interpretazione**: istruzioni 730/2026 (due passaggi concordi) |
| **Interessi sul residuo per incapienza** | **0,4% mensile** sulla parte residua trattenuta nei mesi successivi | **prassi-interpretazione**: istruzioni 730/2026 («nella misura dello 0,4 per cento mensile»). Il D.M. 164 art. 19 c. 1 rinvia agli interessi «per il differimento di pagamento delle imposte sui redditi» senza dire la misura: **da verificare** il fondamento normativo dello 0,4% |
| Soglia | Il sostituto non opera debito o credito per ogni singola imposta o addizionale **fino a 12 euro** | **prassi-interpretazione**: istruzioni 730/2026 e CU 2026 |
| **Cessati e aspettativa senza retribuzione** | Se il rapporto cessa (o c'è aspettativa senza retribuzione) prima delle operazioni, il sostituto **non effettua le operazioni a debito** e comunica all'interessato di versare direttamente; per i deceduti, lo comunica agli eredi (art. 65 D.P.R. 600) | **norma certa**: art. 20 D.M. 164/1999 |
| Se per i cessati vale lo stesso per i **crediti** | L'art. 20 nomina solo le operazioni a debito | **da verificare**: nessun testo letto dice se il credito resta al sostituto o va chiesto all'AdE |
| Interessi del conguaglio ordinario in caso di incapienza | **0,50% mensile**, con dichiarazione scritta della persona; l'importo non trattenuto alla fine dell'anno si comunica e si versa entro il 15 gennaio | **norma certa**: art. 23 c. 3 D.P.R. 600/1973; dal 2027 art. 33 c. 4 D.Lgs. 33/2025 |
| Compensazione del rimborso 730 nella delega | F24EP, righe **150E-154E**, nel mese successivo al rimborso, fuori dal limite annuo dei crediti | **norma certa**: art. 15 c. 1 lett. a) D.Lgs. 175/2014; art. 73 c. 1 lett. a) D.Lgs. 141/2026; risoluzione 103/E 2015 |

**Due misure di interesse diverse.** L'incapienza del conguaglio ordinario ha l'interesse dello 0,50% mensile nel testo di legge; il residuo del 730-4 ha lo 0,4% nelle istruzioni. Il modello deve avere due parametri distinti.

## Tema 8. Art. 51 c. 2 TUIR e il suo successore dal 01/01/2027

**Fonte.** TUIR art. 51 c. 2 letto su Normattiva con `!vig=2026-11-07` e D.Lgs. 117/2026, allegato, art. 53 c. 2 (rubrica «Determinazione del reddito di lavoro dipendente», con rinvio all'art. 51 TUIR e alla L. 232/2016 c. 249 e L. 207/2024 c. 390). Applicazione dal 01/01/2027 (art. 377); abrogazione degli artt. da 1 a 191 TUIR dalla stessa data (art. 376 c. 1 lett. e). **norma certa**.

**Esito.** Il contenuto del comma è invariato. **Cambiano le lettere**, perché il TU elimina quelle soppresse o abrogate (b e g-bis) e rinumera di seguito.

| TUIR art. 51 c. 2 (2026) | TU art. 53 c. 2 (2027) | Contenuto |
|---|---|---|
| a) | a) | Contributi previdenziali e assistenziali per legge; assistenza sanitaria integrativa fino a **3.615,20 euro**. Il rinvio cambia: da «art. 10 c. 1 lett. e-ter» a «art. 10 c. 1 lett. i)» |
| b) *(soppressa dal D.L. 93/2008)* | non esiste | |
| c) | **b)** | Vitto: mense; prestazioni sostitutive **4 euro, 10 euro se elettroniche**; indennità sostitutive per i cantieri **5,29 euro** |
| d) | **c)** | Trasporto collettivo |
| d-bis) | **d)** | Abbonamenti al trasporto pubblico locale, regionale e interregionale |
| e) | e) | Compensi reversibili. Il rinvio cambia: «art. 47 c. 1 lett. b) ed f)» → «**art. 52 c. 1 lett. b) e g)**» |
| f) | f) | Opere e servizi per finalità sociali. Il rinvio cambia: «art. 100 c. 1» → «**art. 109 c. 1**» |
| f-bis) | **g)** | Servizi di educazione e istruzione, ludoteche, centri estivi, borse di studio |
| f-ter) | **h)** | Assistenza ai familiari anziani o non autosufficienti |
| f-quater) | **i)** | Contributi e premi per non autosufficienza e gravi patologie |
| g) | **l)** | Azioni offerte alla generalità dei dipendenti: «lire 4 milioni» → «**euro 2.065,83**» (stesso valore); condizione dei tre anni |
| g-bis) *(abrogata dal D.L. 112/2008)* | non esiste | |
| h) | **m)** | Somme trattenute per oneri dell'art. 10 e spese sanitarie |
| i) | **n)** | Mance dei croupiers, 25% |
| i-bis) | **o)** | Quote di retribuzione per rinuncia all'accredito contributivo |

I limiti in euro (3.615,20; 4; 10; 5,29; 25%) sono **identici**; l'unico valore diverso è la conversione da lire a euro della lettera g)/l), a parità di importo. Il confronto è stato fatto sui numeri dei due testi.

**Fuori dal comma 2, nello stesso articolo.** La franchigia per beni e servizi (258,23 euro) ha nel TU, al c. 4, la deroga **«per i periodi d'imposta 2025, 2026 e 2027»**: limite complessivo di **1.000 euro**, elevato a **2.000 euro** per i lavoratori con figli a carico, anche per utenze domestiche, affitto e interessi sul mutuo della prima casa. Il TUIR vigente a Normattiva (art. 51 c. 3) **non riporta questa deroga**: nel TU è un'incorporazione della L. 207/2024 art. 1 c. 390. **norma certa** per il testo del TU; la fonte originaria (L. 207/2024 c. 390) non è stata letta perché il comma risulta già abrogato nella consolidata.

**Rinvii da altri atti.** L'art. 33 c. 1 D.Lgs. 33/2025 (ritenuta) cita «articolo 53, commi 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11 e 12» del TU, dove l'art. 23 D.P.R. 600 citava l'art. 48 TUIR (per la determinazione del reddito di lavoro dipendente). **norma certa**. L'art. 83 D.Lgs. 141/2026 cita i redditi degli «articoli 51 e 52» TU, cioè i vecchi artt. 49 e 50.

**Per le regole datate del corpus.** Ogni regola che oggi cita una lettera del comma 2 (per esempio buoni pasto, trasporto, welfare) ha bisogno di una **corrispondenza lettera → lettera** con vigenza. La tabella sopra è la corrispondenza completa.

## Tema 9. Conguaglio a credito che supera le ritenute del mese (delega F24EP di dicembre)

**Il fermo da risolvere.** `paghe/delega.py` ferma la delega con `debito_negativo` quando, nel mese di prova (dicembre), il totale a debito del codice 100E diventa negativo perché i conguagli a credito superano le ritenute della delega. L'ADR 0019 e il fermo dicono che «il recupero dell'eccedenza non ha ancora una fonte».

### Che cosa dicono i testi

| Punto | Esito | Marcatura e fonte |
|---|---|---|
| **Rappresentazione nel modello F24EP** | Le somme restituite ai dipendenti in sede di conguaglio di fine anno o per cessazione si compensano con righe **a credito**: codici **155E** (Erario, sezione F), **160E** (addizionale regionale, sezione R con codice regione), **161E** (addizionale comunale, sezione S con codice catastale), nella colonna **«importi a credito compensati»**; riferimento A vuoto, riferimento B = anno d'imposta; modalità **E** (debito e credito). **Non** come debito negativo di 100E | **norma certa**: risoluzione AdE 103/E del 09/12/2015 («nonché le somme restituite in sede di conguaglio di fine anno o per cessazione del rapporto di lavoro»); tabella AdE F24EP 01/10/2026; istruzioni 770/2026 (SX1 col. 7 elenca 155E-161E fra i codici che compensano le somme restituite per conguaglio) |
| **Compensazione orizzontale**: il credito si compensa con i debiti dello stesso modello, non solo con le ritenute | Sì: le eccedenze sono scomputate dai successivi versamenti «**esclusivamente con le modalità di cui all'art. 17 D.Lgs. 241/1997**»; non rientrano nel limite annuo dei crediti compensabili | **norma certa**: art. 15 c. 1 lett. b) D.Lgs. 175/2014; dal 2027 **art. 73 c. 1 lett. b) D.Lgs. 141/2026** (rinvio all'art. 3 D.Lgs. 33/2025) |
| **Limite fisico della delega**: il saldo di ogni modello (record V) non può essere negativo | Un credito non può superare i debiti dello stesso modello | **norma certa**: Allegato 2 delle specifiche F24EP (già in `versamenti-f24ep.md`, tema 3) |
| **Se i crediti superano anche tutti i debiti della delega** | L'eccedenza **non si espone** nel modello. Il sostituto la tiene come **eccedenza** e sceglie fra riporto nei versamenti del periodo successivo e rimborso nella dichiarazione (770); la scelta non risultante dalla dichiarazione vale come riporto; la parte riportata e non utilizzata in compensazione è di nuovo oggetto di scelta | **norma certa**: art. 1 c. 2-4 D.P.R. 445/1997, richiamato dal fatto che l'art. 15 c. 1 lett. b) D.Lgs. 175/2014 lo fa salvo («commi da 2 a 6»); il richiamo sopravvive nell'art. 73 D.Lgs. 141/2026 |
| **Dichiarazione e riporto** | Le somme restituite per conguaglio vanno nel 770, quadro SX rigo **SX1 colonna 1** (anche quelle rimborsate con conguaglio di gennaio-febbraio); la colonna 7 riporta quanto compensato nell'anno; il residuo passa a **SX4** (colonna 4), con scelta fra compensazione (col. 5) e rimborso (col. 6) | **norma certa**: istruzioni AdE 770/2026 |
| **Codice dell'anno dopo** | Il credito che emerge dal 770 «è utilizzabile dal 1.1.2026» (per i redditi 2025) in compensazione con **6781** in F24 e con **166E** in F24EP | **norma certa**: istruzioni 770/2026; risoluzione 103/E 2015 (166E «credito scaturito da ritenute di lavoro dipendente, assimilati e assistenza fiscale derivante dalla dichiarazione del sostituto d'imposta») |
| **Visto di conformità** | L'uso in compensazione di crediti sopra **5.000 euro annui** richiede il visto di conformità sulla dichiarazione da cui il credito emerge, o la sottoscrizione dell'organo di controllo contabile | **norma certa** per il richiamo (istruzioni 770/2026, art. 1 c. 574 L. 147/2013, art. 3 D.L. 50/2017): **da verificare** se si applica al credito da conguaglio e come si applica a un ente locale |
| Gli stessi principi per i rimborsi **730** | Il credito del 730-4 si rimborsa con riduzione delle ritenute del mese e, se non bastano, con quelle dei mesi successivi dello stesso periodo d'imposta (art. 19 c. 2 D.M. 164/1999) | **norma certa**: art. 19 c. 2 D.M. 164/1999. La regola specifica per il solo **conguaglio di fine anno** non è nel D.P.R. 600 (art. 23 non dice nulla sull'eccedenza a credito): è costruita da art. 15 D.Lgs. 175/2014, D.P.R. 445/1997 e istruzioni 770 |
| Il credito di dicembre si usa a gennaio con 155E o con 166E | Fino alla presentazione del 770 il credito non è ancora «da dichiarazione»; le istruzioni 770 fanno partire 166E dalla dichiarazione, la risoluzione 103/E dà 155E per le «eccedenze» | **da verificare**: nessun testo letto dice quale codice usa la delega di gennaio per un credito sorto a dicembre e non assorbito |
| Chi paga la delega di dicembre | La delega delle ritenute operate a dicembre 2026 si versa entro il 16/01/2027: il testo del versamento è quello del D.Lgs. 33/2025, applicabile dal 01/01/2027 (art. 243) | **norma certa** per la decorrenza; **da verificare** se esistono norme transitorie sul periodo di paga e non sulla data |

### Che cosa significa per il fermo

- Il fermo `debito_negativo` nasce da una **scelta di rappresentazione** (i conguagli a credito riducono 100E) che la fonte non prevede. La fonte prevede righe a credito separate e una compensazione sul totale della delega.
- La somma delle ritenute di dicembre non è l'unico debito della delega: contributi (P201 e altre causali), INAIL, IRAP, addizionali sono debiti compensabili per l'art. 3 D.Lgs. 33/2025. Nel mese di prova i contributi superano di molto i conguagli: con la rappresentazione della fonte **il saldo sarebbe positivo** e la delega non si fermerebbe.
- L'ordine fra i crediti (che cosa si compensa per primo) **non è fissato da nessun testo letto**: è una scelta del modello, già fatta dall'ADR 0023 (prima contro 100E). Il fatto che si compensi prima contro 100E non vieta di compensare l'eccedenza contro altri debiti.
- Il caso residuo, **credito oltre tutti i debiti della delega**, ha la norma (riporto o rimborso, D.P.R. 445/1997 art. 1) ma ha **due punti aperti**: il codice del mese successivo e il visto di conformità.
- La rappresentazione cambia anche il quadro SX del 770, che già l'ADR 0020 vuole come vista: SX1 col. 1 (somme restituite per conguaglio) e col. 7 (utilizzo) nascono dalle righe 155E/160E/161E.

## Esito per il grilling

Decisioni che servono a Luca, in ordine. Dove c'è una raccomandazione, è la lettura più vicina alla fonte.

1. **Rappresentazione del conguaglio a credito nella delega (sblocca il fermo `debito_negativo`).** La fonte dà righe a credito (155E, 160E, 161E) e compensazione sul totale della delega. Si lascia cadere l'idea di ridurre 100E? *Raccomandazione:* sì; il fermo diventa «credito oltre il debito della delega» e porta il residuo come fatto riportato (ADR 0023).
2. **Credito che supera tutti i debiti della delega: che cosa fa il modello?** Riporto alla delega successiva come fatto con l'origine (riga del 770 SX1/SX4), oppure rimborso a richiesta. *Raccomandazione:* riporto, con rimborso come scelta esplicita dell'ufficio. Servono due punti: il codice della delega di gennaio (155E o 166E) e il visto di conformità sopra 5.000 euro.
3. **Sostitutiva del 15% sull'accessorio.** Va modellata con fine vigenza al 31/12/2026 e nessuna regola 2027 finché la proroga non è legge. *Raccomandazione:* sì. Va deciso anche: il limite di 50.000 si verifica sul reddito 2026 (lavoro dipendente più pensioni, più rapporti, esclusi gli assimilati): serve un fatto della persona «altri redditi 2026», come per il conguaglio. Si applica in corso d'anno sulle proiezioni e si rettifica a dicembre, oppure la regola ferma finché il fatto manca?
4. **Riferimenti TUIR → TU dal 01/01/2027.** Ogni regola datata ha il successore con corrispondenza esplicita di articolo, comma e lettera (tabelle dei temi 1, 2, 4, 6, 8). I valori di scaglioni, art. 12 e art. 13 restano identici. *Raccomandazione:* due versioni datate della stessa regola, non una regola con due riferimenti, così il corpus controlla `dal` e `al`.
5. **Recuperi a rate oltre 60 euro.** Le dieci rate valgono anche per la somma esente, non solo per l'ulteriore detrazione. Resta da decidere: la soglia dei 60 euro vale per ciascun beneficio o per la somma dei benefici da recuperare? E se il rapporto cessa a metà? *Raccomandazione:* soglia per beneficio, residuo in unica soluzione alla cessazione, entrambi da marcare **da verificare** nella regola.
6. **Addizionali.** Il modello usa: acconto comunale 30% su aliquota e soglia dell'anno precedente, al massimo nove rate da marzo; regionale senza acconto; saldo in al massimo undici rate entro dicembre; cessazione in unica soluzione. Resta da decidere la fonte delle aliquote per regione e comune (legge regionale e portale MEF) e se l'esenzione comunale dell'acconto sulla base del reddito dell'anno precedente è già nel modello o richiede un fatto (reddito dell'anno precedente). *Raccomandazione:* aliquote come parametro datato per codice catastale e per regione, caricato da un file importato, non scritto a mano.
7. **Aliquota media.** Il biennio è l'art. 21 TUIR (art. 23 TU), non l'art. 19. Si corregge l'ADR 0019 e l'ADR 0018 sul riferimento? E la regola sul biennio senza reddito (primo scaglione, dalla norma) distingue «reddito nullo» da «dato mancante»? *Raccomandazione:* sì, e il fermo resta solo per il dato mancante.
8. **730-4.** Due misure di interesse diverse (0,33% sulle rate, 0,4% sul residuo per incapienza) contro lo 0,50% del conguaglio ordinario: tre parametri distinti. Per i cessati la regola copre solo i debiti: il credito di un cessato resta senza testo. *Raccomandazione:* tre parametri; per il credito del cessato, fermo con nome fino a una fonte AdE.
9. **Art. 51 c. 2 e franchigia benefit.** La tabella lettera → lettera (tema 8) entra nel corpus come dato di corrispondenza. La deroga 2025-2027 per beni e servizi (1.000 e 2.000 euro, art. 53 c. 4 TU) ha il suo inizio e la sua fine nel testo: la fonte originaria (L. 207/2024 c. 390) va riletta prima di codificarla. *Raccomandazione:* sì per la tabella; la deroga entra solo con la fonte originaria letta.
10. **Delega di dicembre 2026 versata a gennaio 2027.** Il versamento segue il D.Lgs. 33/2025 (dal 01/01/2027), il conguaglio il TUIR e l'art. 23. La regola datata per i versamenti si sceglie sulla data di versamento o sul periodo di paga? *Raccomandazione:* sulla data del versamento, con avviso, finché non si legge un testo transitorio.

## Cosa resta da verificare (sintesi)

- Legge di bilancio 2027: scaglioni, detrazioni, somma esente, sostitutiva 15% (proroga e condizioni).
- Soglia dei 60 euro per i recuperi a rate e recupero alla cessazione.
- Fonte e formato delle aliquote regionali e comunali; discrepanza «residenza / domicilio fiscale» nell'art. 50 D.Lgs. 446/1997; circolare AdE 15/E del 2007 sull'acconto comunale (rinviata da 23/E, non letta).
- Fondamento normativo dello 0,4% mensile del 730-4; credito di un cessato.
- Codice del credito di dicembre non assorbito nella delega di gennaio; applicabilità del visto di conformità; norme transitorie D.Lgs. 33/2025 per il periodo di paga.
- Applicazione della sostitutiva su proiezioni e recupero se il reddito supera 50.000 a fine anno.
- L. 207/2024 art. 1 c. 390 (testo originario, franchigia 1.000/2.000).
- Criterio mensile della somma esente.

## Fonti

**Normattiva** (consultate il 07/11/2026; i testi sono quelli del portale, senza link stabile: ADR 0003)

- TUIR: `urn:nir:stato:decreto.del.presidente.della.repubblica:1986-12-22;917~art11` (e artt. 12, 13, 19, 21, 51) con `!vig=2026-11-07`.
- D.Lgs. 117/2026: `urn:nir:stato:decreto.legislativo:2026-06-19;117:1~art11` (allegato; artt. 11, 12, 13, 21, 23, 53, 376, 377).
- D.Lgs. 33/2025: `urn:nir:stato:decreto.legislativo:2025-03-24;33:1~art33` (allegato, artt. 33, 243).
- D.Lgs. 141/2026: `urn:nir:stato:decreto.legislativo:2026-08-05;141:1~art73` (allegato, artt. 73, 83).
- D.L. 3/2020: `urn:nir:stato:decreto.legge:2020-02-05;3~art1`.
- L. 207/2024: `urn:nir:stato:legge:2024-12-30;207~art1` (commi 1-100). L. 199/2025: `urn:nir:stato:legge:2025-12-30;199~art1` (commi 1-100 e 201-300).
- D.Lgs. 360/1998 `~art1`; D.Lgs. 446/1997 `~art50`; D.P.R. 600/1973 `~art23`; D.P.R. 445/1997 `~art1`; D.Lgs. 175/2014 `~art15`; D.Lgs. 241/1997 `~art20`; D.M. 164/1999 artt. 19-20 (`urn:nir:ministero.finanze:decreto:1999-05-31;164`).

**Agenzia delle Entrate**

- [Risoluzione 4/E del 29/01/2026](https://www.agenziaentrate.gov.it/portale/documents/20143/9674212/RIS_n_4_del_29_01_2026.pdf/5ae5edac-2045-6948-2f27-43a9d2573fb1?t=1769678085324).
- [Risoluzione 103/E del 09/12/2015](https://www.agenziaentrate.gov.it/portale/documents/20143/303271/Risoluzione+n.+103E+del+9+dicembre+2015_Risoluzione+codici+tributo+F24+EP+sostituti+compensazioni.pdf/a5fc4622-b77d-efc1-bda2-f9ee6aa86dfc).
- [Circolare 23/E del 20/04/2007](https://www.agenziaentrate.gov.it/portale/documents/20143/301381/Circolare+n+23+del+20+04+2007_circ_23_2007.pdf/6558470d-aea1-ddb1-e124-950cb2c1bf60).
- [Tabella codici F24EP al 01/10/2026](https://www.agenziaentrate.gov.it/portale/documents/d/guest/tabella-codici-tributo-f24ep-aggiornata-al-1-ottobre-2026).
- [Istruzioni Modello 770/2026](https://www.agenziaentrate.gov.it/portale/documents/20143/9771798/770_istr_2026.pdf/6175653a-80b7-42a6-cd77-4e48609d0dfc).
- [Istruzioni Modello 730/2026](https://www.agenziaentrate.gov.it/portale/documents/20143/9764684/730_+istruzioni_2026.pdf/2ac8d27a-fa3d-ed9e-ffc1-9bf61457661e?t=1772183775348).
- [Istruzioni CU 2026](https://www.agenziaentrate.gov.it/portale/documents/d/guest/cu_istr_2026_agg-1-).
- Risposta a interpello 173/2026: [copia PDF](https://lentepubblica.it/wp-content/uploads/2026/09/Risposta-n.-173_2026.pdf). Risposta 186/2026: [copia PDF](https://www.studiopizzano.it/wp-content/uploads/2026/10/risposta-interpello-2026-186-d4707063.pdf). Originali AdE non aperti.

**Fonti secondarie** (usate solo per indicare dove cercare, non per fondare una regola): [EC News, 04/09/2026](https://www.ecnews.it/lavoro/imposte-contributi-e-premi/tassazione-e-redditi-di-lavoro/modello-f24-chiarimenti-dallagenzia-delle-entrate/) sulle FAQ AdE del 23/06/2026 (compensazione verticale dell'imposta sostitutiva con il codice 1627 e riporto con 6781); [Orizzonte Scuola sul ddl bilancio 2027](https://www.orizzontescuola.it/pa-aliquota-al-15-su-accessori-fino-a-800-euro-nel-2027-per-i-redditi-sotto-i-50mila-e-nella-legge-di-bilancio/) e [Fisco e Tasse sul ddl](https://www.fiscoetasse.com/normativa-prassi/13619-legge-di-bilancio-2027-le-novita-fiscali-del-ddl-articolo-per-articolo.html), non aperti nel testo. Il vault-pa ha pagine su ris. 4/E 2026 e risposta 173/2026 che concordano con i PDF letti.
