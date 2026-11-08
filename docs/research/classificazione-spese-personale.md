# Classificazione contabile delle spese di personale

Complemento di `integrazione-contabile.md` (non ripete: parte da U.1.01.01.01.002 e U.1.01.02.01.001 e chiude IRAP, Titolo 9, Titolo 7, transazione elementare, punto 5.2). Data: 2026-11-08.

## Domande

1. Codici di V livello (allegato 6/1 D.Lgs. 118/2011) per le voci di personale.
2. Titolo 9 (entrata) e Titolo 7 (spesa) per le ritenute; come si contabilizzano sul mandato dello stipendio.
3. Missione/programma delle spese di personale.
4. Elementi della transazione elementare (allegato 7) e obbligatorietà per il personale.
5. Punto 5.2 dell'allegato 4/2: arretrati, oneri, IRAP, accessorio, residui e FPV.

## Legenda e limiti del metodo

- **norma certa**: testo di un allegato o di una norma, letto riga per riga nel documento citato.
- **prassi**: lettura corrente, non scritta nel testo o non riscontrata sull'allegato.
- **da verificare**: non riscontrato in questa sessione.

Limiti dichiarati, da leggere prima dei codici:

- `arconet.rgs.mef.gov.it` non è risolvibile da questa macchina (errore DNS) e le pagine di `rgs.mef.gov.it` per il piano dei conti non sono state individuate; gli archivi web non hanno restituito copie. Quindi **non ho letto l'allegato 6/1 nella versione Arconet vigente**.
- I testi sono stati letti sulle copie pubblicate da Presidenza del Consiglio (`governo.it`) dello schema di D.Lgs. integrativo e correttivo (poi D.Lgs. 126/2014) con i suoi allegati: 4/2, 6/1, 7 e glossario missioni/programmi (allegato 14). Il decreto nel testo del file cita la deliberazione preliminare del Consiglio dei ministri del 31 gennaio 2014: è la versione di partenza, non quella coordinata di oggi. Il piano dei conti è poi stato aggiornato più volte con decreti MEF/Arconet.
- Il punto 5.2 è stato riscontrato anche su un secondo documento (estratto con art. 3, comma 4, e punti 3.3, 3.6, 3.10, 5.2, 9.1 dell'allegato 4/2, pubblicato dal consiglio regionale della Calabria) e coincide con la copia di `governo.it`.
- Un decreto interministeriale del 16 marzo 2026 aggiorna gli allegati 4/1, 4/2 e 9 (attuazione del comma 659 della legge di bilancio 2026; la novità segnalata riguarda le previsioni di cassa): https://www.quotidianopiu.it/dettaglio/15240867/enti-locali-aggiornati-i-principi-contabili . Il testo del decreto **non è stato letto**: se tocchi il punto 5.2 è **da verificare**.

Conseguenza: i codici sotto sono quelli del testo di partenza; prima di entrare nella specifica vanno riconfrontati con il file Arconet corrente (xlsx o pdf del piano dei conti).

## Sintesi

1. Tutte le voci stipendiali principali hanno un codice di V livello proprio nel Titolo 1, macroaggregato 101 (U.1.01.01.01.001-.008): tempo indeterminato e determinato, straordinario, indennità e compensi, arretrati per anni precedenti. L'IRAP è U.1.02.01.01.001. Oneri a carico ente: U.1.01.02.01.001 (obbligatori), .002 (previdenza complementare), .003 (indennità di fine rapporto).
2. Le ritenute sul lavoro dipendente hanno codici gemelli: entrata E.9.01.02.01.001 (erariali), E.9.01.02.02.001 (previdenziali e assistenziali), E.9.01.02.99.999 (altre); spesa U.7.01.02.01.001, U.7.01.02.02.001, U.7.01.02.99.999. Il sostituto d'imposta è conto terzi per definizione del principio 4/2; la sequenza mandato-reversale-versamento è prassi.
3. Il programma 01.10 «Risorse umane» **non** contiene le spese di personale: il glossario lo dice in negativo («non comprende le spese relative al personale direttamente imputabili agli specifici programmi»).
4. Gli elementi della transazione elementare sono nove (a-i); per un cedolino di un comune ne servono cinque come dati e uno derivato; CUP, perimetro sanitario e politica regionale unitaria non si applicano.
5. Arretrati da rinnovo: impegno nell'anno di firma del CCNL, con oneri riflessi ed effetti retroattivi. IRAP e oneri sull'accessorio: il testo non li cita; che seguano la retribuzione è prassi/da verificare.

## Findings

### 1. Codici di V livello (allegato 6/1)

Fonte: Allegato n. 6/1 al D.Lgs. 118/2011, «Piano dei conti finanziario», copia in https://www.governo.it/sites/governo.it/files/76572-9657.pdf (testo di partenza; vedi limiti). L'impaginazione del pdf sfalsa codici ed etichette in alcune tabelle: ho riallineato per ordine di successione e ho riscontrato che il numero di codici e di etichette coincide per ciascun blocco usato; dove l'abbinamento resta un'inferenza lo dico.

| Voce | Codice V livello | Etichetta | Note |
|---|---|---|---|
| Arretrati anni precedenti, tempo indeterminato | `U.1.01.01.01.001` | **norma certa** | |
| Voci stipendiali, tempo indeterminato | `U.1.01.01.01.002` | **norma certa** | già nota |
| Straordinario, tempo indeterminato | `U.1.01.01.01.003` | **norma certa** | |
| Indennità e altri compensi (esclusi rimborsi missione), tempo indeterminato | `U.1.01.01.01.004` | **norma certa** | |
| Arretrati anni precedenti, tempo determinato | `U.1.01.01.01.005` | **norma certa** | |
| Voci stipendiali, tempo determinato | `U.1.01.01.01.006` | **norma certa** | |
| Straordinario, tempo determinato | `U.1.01.01.01.007` | **norma certa** | |
| Indennità e altri compensi, tempo determinato | `U.1.01.01.01.008` | **norma certa** | |
| Buoni pasto | `U.1.01.01.02.002` | **norma certa** | abbinamento per ordine nel blocco (.001 asili/benessere, .002 buoni pasto, .999 altre) |
| Contributi obbligatori per il personale | `U.1.01.02.01.001` | **norma certa** | già nota; INAIL v. sotto |
| Contributi previdenza complementare | `U.1.01.02.01.002` | **norma certa** | |
| Contributi per indennità di fine rapporto | `U.1.01.02.01.003` | **norma certa** | voce per TFR/IFR a carico ente |
| IRAP | `U.1.02.01.01.001` (IV livello `U.1.02.01.01.000`) | **norma certa** | |
| Indennità organi istituzionali (amministratori) | `U.1.03.02.01.001` | **norma certa** | Titolo 1, macroaggregato 103 (acquisto di servizi), non 101 |
| Compensi a organi di revisione, controllo e altri incarichi istituzionali | `U.1.03.02.01.008` | **da verificare** | abbinamento per ordine, non letto con riga unica |
| Collaborazioni coordinate e a progetto (co.co.co.) | `U.1.03.02.12.003` | **norma certa** | sotto «Lavoro flessibile, quota LSU e agenzie interinali» (`U.1.03.02.12.000`) |

Punti che non hanno un codice esplicito nel testo letto:

- **Fondo risorse decentrate (accessorio e produttività)**: il piano non ha una voce «produttività» o «fondo»; il candidato naturale è `U.1.01.01.01.004` (indennità e altri compensi). **prassi / da verificare** sul glossario Arconet delle voci di V livello (non letto).
- **INAIL**: nel piano c'è solo «Contributi obbligatori per il personale» `U.1.01.02.01.001`; che includa il premio INAIL è **da verificare** sul glossario. Al contrario, la voce «Altri contributi sociali effettivi n.a.c.» `U.1.01.02.01.999` è un'alternativa da escludere o confermare con il glossario.
- **TFS**: l'indennità di fine servizio erogata direttamente dal datore di lavoro è un contributo figurativo, `U.1.01.02.02.003`; non è il TFR.
- **Contributi e oneri sull'indennità degli amministratori**: nessun codice individuato. **da verificare**. L'IRAP sulle indennità segue lo stesso `U.1.02.01.01.001`.
- Non letti: voci del macroaggregato 103 per formazione, mensa o altri rimborsi che potrebbero toccare un cedolino; non ripresi.

### 2. Titolo 9, Titolo 7 e contabilizzazione delle ritenute

Codici (stessa fonte, Allegato 6/1):

| Ritenuta | Entrata (Titolo 9) | Spesa di versamento (Titolo 7) | Etichetta |
|---|---|---|---|
| Erariali su redditi da lavoro dipendente | `E.9.01.02.01.001` (IV: `E.9.01.02.01.000`) | `U.7.01.02.01.001` (IV: `U.7.01.02.01.000`) | **norma certa** |
| Previdenziali e assistenziali su redditi da lavoro dipendente | `E.9.01.02.02.001` (IV: `E.9.01.02.02.000`) | `U.7.01.02.02.001` (IV: `U.7.01.02.02.000`) | **norma certa** |
| Altre ritenute al personale dipendente per conto di terzi | `E.9.01.02.99.999` (IV: `E.9.01.02.99.000`) | `U.7.01.02.99.999` (IV: `U.7.01.02.99.000`) | **norma certa** |
| Ritenute su lavoro autonomo (erariali, previdenziali, altre) | `E.9.01.03.01/.02/.99.xxx` | `U.7.01.03.01/.02/.99.xxx` | **norma certa**; utile per co.co.co. e professionisti |

Lettura del layout: le tabelle del pdf sfalsano di una riga codice ed etichetta; l'abbinamento è stato ricostruito per successione (13 codici e 13 etichette in Titolo 9 per questo gruppo; stessa verifica per il Titolo 7) e coincide con i codici già riportati nella ricerca precedente per il Titolo 7 (U.7.01.02.01/02/99.000). Il codice di V livello del Titolo 9 è l'unico dato nuovo rispetto a quella ricerca.

Contabilizzazione:

- **norma certa** Principio 4/2, punto 7.1: servizi per conto terzi e partite di giro sono le transazioni fatte per conto di altri «in assenza di qualsiasi discrezionalità ed autonomia decisionale da parte dell'ente, quali quelle effettuate come sostituto di imposta»; non hanno natura autorizzatoria. Fonte: https://www.governo.it/sites/governo.it/files/76572-9653.pdf (allegato A/2, testo di partenza).
- **norma certa** Punto 7.2: le obbligazioni di partite di giro e conto terzi sono imputate all'esercizio in cui l'obbligazione è perfezionata, non a quello di esigibilità (deroga al principio generale della competenza potenziata): quindi la ritenuta e il suo versamento seguono l'esercizio del mandato di stipendio.
- **norma certa** Il punto 11.7 dello stesso allegato richiede che gli ordini di incasso e pagamento riportino i codici della transazione elementare nei campi liberi dell'ente (riconferma nell'art. 5, comma 3-bis, nel testo del decreto correttivo).
- **prassi** La sequenza concreta (impegno e liquidazione del lordo in Titolo 1; mandato del lordo, con quietanza al dipendente per il netto e reversale per le ritenute in Titolo 9 con regolazione contabile; successivo mandato di versamento in Titolo 7 verso Erario/INPS, di norma via F24EP) non è descritta nel punto 7 per le ritenute sul personale: il testo letto descrive la regolazione contabile solo per le entrate riscosse per conto terzi. È la lettura coerente con la struttura `ritenute` del mandato OPI già documentata in `integrazione-contabile.md`. **da verificare** presso le FAQ Arconet o il regolamento di contabilità dell'ente quale sia la variante ammessa (mandato lordo con reversali collegate o mandato netto con ritenute a compensazione).

### 3. Missione e programma delle spese di personale

- **norma certa** Il glossario missioni/programmi (allegato 14, testo di partenza) descrive il programma 01.10 «Risorse umane» come amministrazione e funzionamento delle attività a supporto delle politiche generali del personale (formazione, reclutamento, dotazione organica, contrattazione decentrata e relazioni sindacali, sicurezza sul lavoro) e conclude: «Non comprende le spese relative al personale direttamente imputabili agli specifici programmi di spesa delle diverse missioni». Fonte: https://www.governo.it/sites/governo.it/files/76572-9665.pdf (stesso testo in 9669).
- Quindi lo stipendio va al programma dove il dipendente lavora; al 01.10 vanno solo i costi di gestione del personale (e il personale che lavora all'ufficio personale). La ripartizione tra programmi dipende dall'assegnazione del dipendente al servizio, un dato di organizzazione dell'ente, non del cedolino. Il principio 4/2 non contiene una regola di riparto del personale per programma (non ne ho trovata): la regola è nel glossario.
- **norma certa** Il D.Lgs. 126/2014 consente solo alle **Regioni**, per difficoltà gestionali motivate e per non più di due esercizi, di usare 01.10 in modo strumentale per la spesa di personale, con disaggregazione in allegato (nuovo art. 14, comma 3-bis, D.Lgs. 118/2011): non vale per i comuni. Fonte: https://www.governo.it/sites/governo.it/files/76572-9650.pdf .
- **norma certa** I programmi sono raccordati al COFOG di secondo livello nel glossario (art. 14, comma 1, lett. b, come sostituita; comma 3-ter): per il 01.10 il gruppo è 01.3 «Servizi generali».
- Conseguenza per Paghe PA: la riga di proposta ha bisogno di un attributo «programma del dipendente» (dato di organizzazione). Conto terzi: la missione 99 «Servizi per conto terzi - Partite di giro» (programma 01) ha come descrizione le ritenute previdenziali, erariali e altre al personale; **norma certa** (glossario, stessa fonte).

### 4. Transazione elementare (allegato 7)

Fonte: Allegato n. 7 al D.Lgs. 118/2011, «Codifica della transazione elementare» (art. 6, comma 1), copia in https://www.governo.it/sites/governo.it/files/76572-9658.pdf (testo di partenza). **norma certa**. Elenco completo, lettere a-i:

| Lett. | Elemento | Per la spesa di personale di un ente locale |
|---|---|---|
| a | Codice funzionale: missione e programma (solo spese) | obbligatorio; dal programma del dipendente |
| b | Codice economico: piano dei conti integrato (allegato 6), dal 2016 | obbligatorio; V livello |
| c | COFOG al secondo livello (solo spese) | obbligatorio, derivato dal programma tramite glossario |
| d | Codice UE: 1-2 entrate; 3-8 spese (8 = spese non correlate a finanziamenti UE) | obbligatorio; di regola 8, salvo personale finanziato da fondi UE (3-7) |
| e | Codice SIOPE (campo apposito nei titoli di pagamento) | obbligatorio; dal 2017 coincide con il codice di piano dei conti (DM 9/6/2016, v. `integrazione-contabile.md`) |
| f | CUP (solo spese di investimento) | non applicabile al personale; unica eccezione teorica di personale capitalizzato: **da verificare** |
| g | Entrata/spesa ricorrente e non ricorrente: 1 e 2 entrate; 3 spese ricorrenti, 4 spese non ricorrenti | obbligatorio; spesa a regime = 3; è non ricorrente per testo (punto 5) la spesa per consultazioni elettorali o referendarie locali: il lavoro straordinario elettorale è quindi 4 |
| h | Perimetro sanitario (solo regioni, art. 20) | non applicabile |
| i | Programma della politica regionale unitaria (solo regioni) | non applicabile |

Note: l'aggiornamento dell'allegato avviene per decreto MEF con validità dall'esercizio successivo (art. 6, comma 1-bis); la versione attuale dell'allegato 7 e di ogni tabella di valori è **da verificare** su Arconet. Il punto 5 dell'allegato elenca per le spese solo cinque ipotesi di spesa non ricorrente: nessuna ricomprende le retribuzioni ordinarie.

### 5. Punto 5.2 allegato 4/2

Fonti: https://www.governo.it/sites/governo.it/files/76572-9653.pdf (allegato intero, testo di partenza) e https://www.consiglioregionale.calabria.it/upload/istruttoria/2%20Allegato%20n%204.2%20e%204.4%20D.%20Lgs.%20n.%20118-2011.pdf (estratto con art. 3 c. 4). Il testo è lo stesso. Etichetta: **norma certa** per quanto riportato, con la riserva sul decreto del 16 marzo 2026.

- **Trattamenti fissi e continuativi** (dinamica predefinita da legge o CCNL): impegno automatico a inizio esercizio per l'intero importo, anche per gli esercizi del bilancio di previsione; a rendiconto si cancellano gli impegni privi di obbligazione formalizzata.
- **Rinnovi contrattuali, arretrati**: impegno «nell'esercizio in cui è firmato il contratto collettivo nazionale per le obbligazioni derivanti da rinnovi contrattuali del personale dipendente, compresi i relativi oneri riflessi a carico dell'ente e quelli derivanti dagli eventuali effetti retroattivi del nuovo contratto, a meno che gli stessi contratti non prevedano il differimento degli effetti economici». Gli arretrati stessi sono la voce `U.1.01.01.01.001`/`.005` (anni precedenti). Per l'ente che paga gli arretrati l'anno dopo la firma o il differimento: l'impegno resta nell'anno di firma e la liquidazione segue l'esigibilità. L'accantonamento nelle more è facoltativo («si auspica») e l'importo non utilizzato confluisce nel risultato di amministrazione; non si accantona in caso di blocco legale senza recupero.
- **Accessorio e premiante liquidato l'anno dopo**: stanziato e impegnato nell'esercizio cui si riferisce; con la firma dell'integrativo si impegnano le obbligazioni imputandole agli esercizi di esigibilità; in assenza di integrativo a fine anno, con delibera di costituzione del fondo e certificazione dei revisori, le risorse sono vincolate e le economie vanno nella quota vincolata del risultato di amministrazione. La spesa del fondo è stanziata per intero nell'esercizio del fondo; la parte da liquidare l'anno successivo è coperta dal fondo pluriennale vincolato.
- **Oneri riflessi e IRAP sull'accessorio**: il punto 5.2 nomina gli oneri riflessi solo per i rinnovi contrattuali. Non c'è una frase esplicita su oneri e IRAP dell'accessorio. La lettura corrente è che seguano l'imputazione della retribuzione cui accedono, perché sono obbligazioni nate dalla stessa liquidazione: **prassi / da verificare** (nessuna FAQ Arconet letta in questa sessione). Per Paghe PA: proporre oneri e IRAP con lo stesso esercizio di imputazione e lo stesso flag FPV della riga di retribuzione, marcando la regola come ipotesi da confermare.
- **Residui e FPV a fine anno**: art. 3, comma 4: sono conservate tra i residui passivi le spese impegnate, liquidate o liquidabili nell'esercizio ma non pagate; le spese impegnate non esigibili sono reimputate all'esercizio di esigibilità, incrementando il fondo pluriennale di spesa. Quindi: un cedolino già esigibile e non pagato al 31/12 diventa residuo passivo; l'accessorio esigibile l'anno dopo non è residuo ma reimputazione con FPV.
- **IRAP, rimborsi**: nel punto 5.2 un passaggio separato tratta il credito IRAP dell'ente con metodo commerciale (accertamento nell'esercizio della richiesta di rimborso): non riguarda il cedolino.

## Domande aperte

1. Allegato 6/1 vigente (Arconet): riconfrontare tutti i codici della tabella e verificare eventuali nuove voci o rinumerazioni dal 2014 ad oggi. Glossario delle voci di V livello per accessorio, INAIL, buoni pasto, contributi su indennità amministratori.
2. Decreto interministeriale 16 marzo 2026: se modifica il punto 5.2 o il punto 7 dell'allegato 4/2.
3. Variante OPI per i mandati di stipendio con ritenute (lordo con reversali o netto) e FAQ Arconet sulla regolazione contabile delle ritenute del personale.
4. Esplicita regola di imputazione di oneri e IRAP dell'accessorio (FAQ Arconet, magistratura contabile).
5. Allegato 14 vigente: conferma che la frase su 01.10 è ancora nel glossario, e programma di destinazione per straordinario elettorale e per le indennità degli amministratori (programma 01.01).

## Tabella riassuntiva

| Codice | Voce | Etichetta |
|---|---|---|
| `U.1.01.01.01.001` | Arretrati per anni precedenti, personale a tempo indeterminato | norma certa |
| `U.1.01.01.01.002` | Voci stipendiali, tempo indeterminato | norma certa |
| `U.1.01.01.01.003` | Straordinario, tempo indeterminato | norma certa |
| `U.1.01.01.01.004` | Indennità e altri compensi, tempo indeterminato (candidato per l'accessorio del fondo) | norma certa per la voce; imputazione del fondo da verificare |
| `U.1.01.01.01.005` | Arretrati per anni precedenti, tempo determinato | norma certa |
| `U.1.01.01.01.006` | Voci stipendiali, tempo determinato | norma certa |
| `U.1.01.01.01.007` | Straordinario, tempo determinato | norma certa |
| `U.1.01.01.01.008` | Indennità e altri compensi, tempo determinato | norma certa |
| `U.1.01.01.02.002` | Buoni pasto | norma certa (abbinamento per ordine nel blocco) |
| `U.1.01.02.01.001` | Contributi obbligatori per il personale (CPDEL/INPS; INAIL da verificare) | norma certa; inclusione INAIL da verificare |
| `U.1.01.02.01.002` | Contributi previdenza complementare | norma certa |
| `U.1.01.02.01.003` | Contributi per indennità di fine rapporto (TFR/IFR a carico ente) | norma certa |
| `U.1.01.02.02.003` | Indennità di fine servizio erogata direttamente (TFS diretto) | norma certa |
| `U.1.02.01.01.001` | IRAP | norma certa |
| `U.1.03.02.01.001` | Indennità organi istituzionali (amministratori) | norma certa |
| `U.1.03.02.01.008` | Compensi a organi di revisione e controllo | da verificare (abbinamento) |
| `U.1.03.02.12.003` | Collaborazioni coordinate e a progetto | norma certa |
| `E.9.01.02.01.001` | Ritenute erariali su lavoro dipendente per conto terzi | norma certa |
| `E.9.01.02.02.001` | Ritenute previdenziali e assistenziali su lavoro dipendente | norma certa |
| `E.9.01.02.99.999` | Altre ritenute al personale dipendente per conto terzi | norma certa |
| `U.7.01.02.01.001` | Versamento ritenute erariali su lavoro dipendente | norma certa |
| `U.7.01.02.02.001` | Versamento ritenute previdenziali e assistenziali su lavoro dipendente | norma certa |
| `U.7.01.02.99.999` | Altri versamenti di ritenute al personale dipendente | norma certa |
| Accessorio: oneri e IRAP seguono la retribuzione | regola di imputazione per esercizio | prassi / da verificare |
| Programma 01.10 non contiene le spese di personale dei programmi | regola di riparto | norma certa (glossario, testo di partenza) |
| Transazione elementare a-i | struttura del codice | norma certa (testo di partenza) |
| Contabilizzazione ritenute: Titolo 1, Titolo 9, Titolo 7 | sequenza dei movimenti | classificazione norma certa; sequenza prassi |
| Codici letti sul testo di partenza, non sulla versione Arconet vigente | tutti i codici | da riconfrontare prima della specifica |
