# Sintassi del campo `riferimento`: identificativi di norme, CCNL, prassi e atti dell'ente

Ticket: #17 (mappa #1). Branch: research/riferimenti-normativi. Data: 2026-11-06.

## Domanda

URN NIR ed ELI sono identificativi stabili e risolvibili fino ad articolo e comma per norme statali e regionali? Esiste un identificativo stabile per CCNL (codice CNEL, ARAN), circolari e messaggi INPS, risoluzioni e circolari AdE? Quale sintassi adottare nel campo `riferimento` di `paghe/corpus.py`, oggi testo libero non vuoto?

## Metodo e legenda

Legenda:

- **norma certa**: specifica o testo primario aperto, oppure risultato osservato con la prova indicata.
- **prassi-interpretazione**: uso di fatto, lettura o scelta progettuale argomentata; non stabilita da una fonte.
- **da verificare**: non aperto direttamente, o aperto solo in parte.

A differenza delle ricerche #3 e #4, stavolta i domini istituzionali erano raggiungibili. Le prove sono del 06/11/2026, con richieste HTTP dirette e lettura dell'HTML o del PDF. I risultati valgono per quel giorno.

**Aperti direttamente**

- Normattiva: portale, FAQ, pagina Utilità, guida e FAQ del motore regionale.
- API open data di Normattiva: specifica PDF (rev. 10 del 10/03/2026) e chiamate reali.
- AgID: Circolare 2/2019 e circolare AIPA/CR/35.
- `ELI_implementation_in_Italy.pdf` (dati.normattiva.it).
- RFC 9676 e registro IANA dei namespace URN.
- Francesconi et al., articolo su xmLeges (CNR).
- CNEL: pagine dell'archivio e file `ccnl-settore-pubblico.xlsx`.
- ARAN: pagine `documento_pubblico` e PDF dei CCNL.
- INPS: PDF di circolare e messaggio, feed RSS, redirect.
- AdE: PDF e pagine d'archivio.
- Raccolta normativa della Regione Toscana.

**Non aperti o aperti solo in parte**

- `www.normeinrete.it` e `www.nir.it`: timeout di connessione. La grammatica originale URN NIR (Spinosa 2001 e v. 1.3) quindi non è stata letta.
- Registro ELI su EUR-Lex: pagina senza contenuto leggibile.
- Pagine di dettaglio INPS: l'HTML scaricato non mostra il testo dell'atto, che viene caricato lato client. L'esistenza dell'atto è provata dal PDF.
- `indicepa.gov.it`: risponde, ma è un'applicazione lato client. Il formato del codice IPA è letto solo da estratti di ricerca.
- ARAN, percorsi storici `/comunicati/...`: rispondono 403, come anche un percorso inventato. Da uno script non si distingue una pagina assente da un blocco.
- Archivio di ricerca CNEL: applicazione lato client. Le API dedotte dal suo JavaScript hanno risposto 404.
- Lombardia e altre regioni: non provate. Un URL di Emilia-Romagna ricordato a memoria ha dato 404, e non è una prova di nulla.

Le prove negative usano URN volutamente errati. Sono indicate come tali e non corrispondono ad atti da citare.

## Sintesi

1. **URN NIR è l'identificativo giusto per le norme statali, ma si ferma all'articolo.** Normattiva risolve articolo, allegato e vigenza a una data. Il comma ha una notazione di fatto, `~art2-com18`, che Normattiva usa nei propri link. Il portale però non si posiziona sul comma e l'API lo rifiuta.
2. **Il portale non verifica nulla.** Risponde sempre HTTP 200, corregge data e tipo sbagliati e può aprire un atto diverso. Un articolo inesistente porta silenziosamente all'art. 1. **L'API è invece severa** e va usata per la validazione.
3. **Senza `!vig=` il portale può mostrare un testo futuro.** Oggi TUIR art. 11 e 51 e D.P.R. 600/1973 art. 23 appaiono abrogati «dal 1-1-2027». Con la data giusta il testo vigente c'è. Un link senza data è quindi fuorviante.
4. **ELI esiste in Italia solo a livello di atto.** Il permalink si basa su data di pubblicazione e codice redazionale. I tentativi di puntare all'articolo danno 404 o 409, e la proposta di estensione del 2018 ha le sezioni vuote.
5. **Le regioni non sono coperte da Normattiva, se non tramite un motore di ricerca.** La Toscana risolve URN NIR a livello di atto sul proprio sito, ma nei link interni scrive l'articolo come `:art2` e rifiuta `~art2`.
6. **Per il CCNL il codice CNEL esiste: S105 per il comparto Funzioni Locali.** Identifica però la linea contrattuale, non il singolo contratto. Serve codice più data di sottoscrizione.
7. **INPS e AdE non hanno un identificativo ufficiale oltre a tipo, numero e data.** Gli ID negli URL funzionano ma non sono documentati, e i numeri ripartono ogni anno.
8. **Proposta:** una stringa logica, senza URL, con quattro schemi e una partizione comune. Il link di consultazione è derivato o registrato a parte.

```
urn:nir:stato:legge:1995-08-08;335~art2-com18
ccnl:S105:2022-11-16~art14-com1
prassi:inps:circolare:2026-01-30;6~par6
ente:c_x000:delibera.cc:2026-03-10;45~art3-com2     (esempio fittizio)
```

**Fatto da segnalare fuori ticket.** Il D.Lgs. 117/2026 (testo unico imposte sui redditi) abroga dal 1/1/2027 gli articoli del TUIR provati in questa ricerca, e il D.Lgs. 33/2025 abroga dalla stessa data l'art. 23 D.P.R. 600/1973. ARAN pubblica inoltre un CCNL Funzioni Locali 2025-2027 firmato il 28/10/2026, non citato nei documenti di questo repo ma già presente nel vault `vault-pa`. Entrambi incidono sui riferimenti che il corpus dovrà contenere.

## Tabella per tipo di fonte

| Fonte | Identificativo | Chi lo gestisce | Stabilità | Granularità | Risolvibilità | Certezza |
|---|---|---|---|---|---|---|
| Norma statale, URN NIR | `urn:nir:stato:<tipo>:<data>;<num>` | Standard AIPA 2001, sostituito da AgID 2/2019; Normattiva (IPZS) lo mantiene | Logico, indipendente dall'URL; standard formalmente superato ma in uso; non registrato in IANA | Articolo, allegato, versione. Comma solo come notazione | Portale tollerante; API severa | **norma certa** (prove); comma **prassi-interpretazione** |
| Norma statale, ELI | `/eli/id/<data GU>/<cod. redazionale>/...` | IPZS | Permalink dichiarato; dipende dalla pubblicazione in GU | Solo atto e versione | Normattiva e GU, con percorsi diversi | **norma certa** |
| Norma regionale | `urn:nir:regione.<nome>:legge:...` | Singoli consigli regionali | Dipende dalla regione | Toscana: atto provato; articolo con `:art2` accettato, visualizzazione non confermata. Altre: non provate | Solo sito regionale; Normattiva dà falsi positivi | **norma certa** per l'atto toscano; articolo e altre regioni **da verificare** |
| CCNL | Codice CNEL + data di sottoscrizione | CNEL (codice), ARAN (testo) | Codice stabile (fonte CNEL); URL ARAN già cambiati | Codice: linea contrattuale. Articolo e comma solo nel testo | Nessun resolver; ancore `#art.N` non uniformi | **norma certa** per S105 e testi; composizione **prassi-interpretazione** |
| INPS, circolari e messaggi | Tipo + numero + data | INPS | Estremi stabili; numero annuale; ID negli URL non documentato | Atto; paragrafi nel testo | `idunivoco` redirige; PDF con percorsi diversi | **norma certa** per le prove; ID ufficiale **da verificare** |
| AdE, circolari, risoluzioni, interpelli, provvedimenti | Tipo + numero + data | AdE | Estremi stabili; URL eterogenei | Atto; punti nel testo | Pagine d'archivio e PDF con UUID | **norma certa** per le prove; stabilità futura **da verificare** |
| Atti dell'ente | Ente + tipo + numero + data | Ente | Dati propri, non globali | Articolo se l'atto li ha | Albo o archivio dell'ente | **prassi-interpretazione** |
| Prassi senza numero | Ente + tipo + data + `sn` | Ente emittente | Solo con copia conservata | Pagina o paragrafo | URL e impronta nel registro | **prassi-interpretazione** |

## Findings

### 1. URN NIR: fonte e sintassi

- **Fonte.** La circolare AIPA/CR/35 del 06/11/2001 istituisce i nomi uniformi, ma rimanda ai siti aipa.it e normeinrete.it per le regole di composizione. Il testo non contiene quindi la grammatica. **norma certa**
- **Stato dello standard.** La Circolare AgID 2/2019 adotta ELI, ECLI 2.0 e URN:LEX, con obbligo di impiegarne almeno uno, sostituisce la AIPA/CR/35 e dà 24 mesi per convertire le banche dati esistenti. **norma certa**
- **In uso nonostante la sostituzione.** La pagina Utilità di Normattiva indica ancora URN:NIR e AIPA/CR/35 come riferimento. La specifica API ha aggiunto `dettaglio-atto-urn` il 10/03/2026, solo per `urn:nir`. **norma certa**
- **Grammatica disponibile.** La specifica API fissa documento, articolo, allegato e versione, e l'articolo di Francesconi conferma autorità, tipo, estremi, annesso e versione. **norma certa**. La grammatica originale non è stata letta. **da verificare**
- **Registrazione.** Il registro IANA contiene `lex` (record del 18/11/2022) e non `nir`. L'RFC 9676 è informativo e non ha il consenso IETF. **norma certa**
- **Equivalenza con URN:LEX.** La circolare AgID definisce URN:LEX come estensione diretta di NIR. L'RFC mostra `urn:lex:it:stato:legge:2003-09-21;456`. La conversione è quindi meccanica: `urn:nir:` diventa `urn:lex:it:`. **prassi-interpretazione**

Forma documentata dalle FAQ di Normattiva e dalla specifica API: **norma certa**.

```
urn:nir:<autorità>:<tipo>:<AAAA-MM-GG>;<numero>[:<allegato>][~art<n>[<estensione>]][@originale | !vig=<AAAA-MM-GG>]
```

Le FAQ coprono anche estensioni latine (`~art16bis`), numeri estesi (`~art314.15`, `~art01`) e romani convertiti in arabi. Avvertono inoltre che le incongruenze nei testi possono produrre risposte inattese e suggeriscono di verificare i link prima di pubblicarli.

### 2. Prove su Normattiva (portale `uri-res/N2Ls`)

Tutti i risultati sono **norma certa** per osservazione. HTTP è sempre 200.

| URN provato | Risultato osservato |
|---|---|
| `urn:nir:stato:decreto.del.presidente.della.repubblica:1973-09-29;600~art23` | Art. 23, «Testo in vigore dal: 1-1-2027», abrogato dal D.Lgs. 33/2025 |
| stesso con `!vig=2026-11-06` | Art. 23 «Ritenute sui redditi di lavoro dipendente», in vigore dal 21-5-2022 al 31-12-2026 |
| `urn:nir:stato:decreto.del.presidente.della.repubblica:1986-12-22;917~art51` | Art. 51, in vigore dal 1-1-2027, abrogato dal D.Lgs. 117/2026 |
| stesso con `!vig=2026-11-06` | Art. 51 «Determinazione del reddito di lavoro dipendente», in vigore dal 12-8-2026 al 31-12-2026 |
| `...;917~art11` | Art. 11, abrogato dal D.Lgs. 117/2026 con effetto dal 1-1-2027 |
| `...;917~art11!vig=2020-01-01` | Testo in vigore dal 1-1-2012 al 31-12-2021; prima fascia fino a 15.000 euro al 23% |
| `urn:nir:stato:legge:1995-08-08;335~art2` | Art. 2 «Armonizzazione», in vigore dal 1-1-2025 |
| `...;335~art2!vig=2020-01-01` | Art. 2 nella versione vigente a quella data |
| `...;335~art2!vig=1990-01-01` | «NON ANCORA ESISTENTE O VIGENTE» |
| `...;335~art2@originale` | Testo originale, art. 2 |
| `urn:nir:stato:decreto.legislativo:2001-03-30;165~art40bis` | Art. 40-bis |
| `urn:nir:stato:costituzione:1947-12-27~art36` | Art. 36 |
| `urn:nir:stato:decreto.legislativo:2026-06-19;117:1~art51` | Art. 51 del testo unico allegato, «Redditi di lavoro dipendente» |

**Comma**

- `~art2-com18` risponde 200 e apre l'art. 2. L'HTML non ha un'ancora per comma. **norma certa**
- `~art2-com999` dà lo stesso risultato: il comma non viene controllato. **norma certa**
- La forma `-com` non è nelle FAQ né nella specifica API. Compare però nei link generati da Normattiva nei testi, per esempio `...;503~art13-com1-letb`, `...;124~art18-com8quinquies` e, per un articolo unico, `...;243~com6-letb`. **norma certa** come osservazione; **prassi-interpretazione** come sintassi.
- Il comma si può comunque controllare nel testo: l'HTML del portale e il campo `articoloHtml` dell'API marcano ogni comma con la classe `comma-num-akn` (34 occorrenze per L. 335/1995 art. 2, 13 per TUIR art. 51). **norma certa** per questi due articoli; copertura su tutti gli atti **da verificare**.

**Prove negative: il portale non è un validatore**

| URN volutamente errato | Risultato sul portale |
|---|---|
| `urn:nir:stato:legge:1995-01-01;335` (data errata) | Apre L. 8 agosto 1995, n. 335 |
| `urn:nir:stato:decreto.legislativo:1995-08-08;335` (tipo errato) | Apre L. 8 agosto 1995, n. 335 |
| `urn:nir:stato:legge:1996-08-08;335` (anno errato) | Apre **un altro atto**: D.L. 25 giugno 1996, n. 335 |
| `urn:nir:regione.toscana:legge:2005-02-24;40` | Apre **un atto statale**: L. 24 marzo 2005, n. 40 |
| `urn:nir:regione.lombardia:legge:2012-02-14;4` | Apre **un atto statale**: D.Lgs. 9 gennaio 2012, n. 4 |
| `...;335~art9999` | Si posiziona sull'art. 1, come dichiarato dalle FAQ |
| `urn:nir:stato:legge:1995-08-08;99999` | Pagina con titolo «Normattiva - Errore», HTTP 200 |
| `urn:nir:stato:decreto.legislativo:2026-06-19;117~art5` (manca `:1`) | Art. 1 del decreto, non l'art. 5 del testo unico |

Dalle prove sembra che il portale cerchi per anno e numero, ignorando autorità e tipo. **prassi-interpretazione** (inferenza dai risultati).

Due forme per i D.P.R.: `stato:decreto.del.presidente.della.repubblica` è nelle FAQ, mentre `presidente.repubblica:decreto` è quella dei link interni del portale (33 occorrenze nel campione, nessuna dell'altra). Il portale le apre entrambe. **norma certa**

### 3. Prove sull'API open data (`atto/dettaglio-atto-urn`)

Tutti i risultati sono **norma certa** per osservazione.

| URN | Risposta |
|---|---|
| `urn:nir:stato:decreto.legge:2008-11-10;180~art2` (esempio della specifica) | 200, atto e testo |
| `urn:nir:stato:decreto.del.presidente.della.repubblica:1986-12-22;917~art11!vig=2020-01-01` | 200, vigenza articolo 20120101-20211231 |
| `...;917~art51!vig=2026-11-06` | 200, vigenza articolo 20260812-20261231 |
| `urn:nir:stato:decreto.legislativo:2026-06-19;117:1~art51` | 200 |
| `urn:nir:stato:legge:1995;335~art2` (forma solo anno) | 200 |
| `urn:nir:stato:legge:1995-08-08;335~art2` | 200 con `lista` di 2 risultati: originale (GU 190) e ripubblicazione (GU 198) |
| `urn:nir:stato:legge:1995-08-08;335~art2-com18` | **400**, codice 1003 |
| `urn:nir:presidente.repubblica:decreto:1986-12-22;917~art11` | **400**, codice 1003 |
| `urn:lex:it:stato:legge:1995-08-08;335~art2` | **400**, codice 1003 |
| `urn:nir:regione.toscana:legge:2005-02-24;40` | **400**, codice 1003 |
| `urn:nir:stato:legge:1995-01-01;335~art2` | **404**, atto non trovato |
| `urn:nir:stato:decreto.legislativo:1995-08-08;335~art2` | **404**, atto non trovato |
| `urn:nir:stato:legge:1995-08-08;335~art9999` | **404** |

Una chiamata senza intestazioni da browser ha dato anche 500 «riprovare più tardi», poi 200 con intestazioni complete. La specifica riporta l'indirizzo di esercizio `https://api.normattiva.it/t/normattiva.api`. La continuità di questo comportamento e gli eventuali limiti d'uso restano **da verificare**.

Conseguenza: il tipo canonico del D.P.R. è `stato:decreto.del.presidente.della.repubblica`, perché è l'unica forma che funziona sia sul portale sia sull'API.

Il portale accetta anche `urn:lex:it:...`, ma data la sua tolleranza non è un'indicazione di supporto. **prassi-interpretazione**

### 4. ELI

- Il documento IPZS del 16/04/2018 descrive due implementazioni. GU: `/eli/id/<AAAA>/<MM>/<GG>/<cod. redazionale>/<serie>`. Normattiva: `/eli/stato/...`, alias per tipo e numero, e `/eli/id/.../CONSOLIDATED|ORIGINAL/<data>`, indicato come permalink. **norma certa**
- Il capitolo sull'estensione ad articoli e allegati ha solo i titoli delle sezioni. **norma certa**

| URL | Risultato |
|---|---|
| `normattiva.it/eli/id/1995/08/16/095G0382/CONSOLIDATED` | 200, L. 335/1995 |
| `.../CONSOLIDATED/20200101` | 200, metadati ELI con versione 01/01/2020 |
| `normattiva.it/eli/stato/LEGGE/1995/08/08/335/CONSOLIDATED` | 200 |
| `normattiva.it/eli/stato/LEGGE/1995/08/08/335/ORIGINAL` | 200 |
| `gazzettaufficiale.it/eli/id/1995/08/16/095G0382/sg` | L. 335/1995 |
| `normattiva.it/eli/id/1995/08/16/095G0382/sg` | **404** |
| `.../CONSOLIDATED/art2` | **404** |
| `.../CONSOLIDATED~art2` | **409** |

Il portale inserisce metadati ELI nella pagina: per esempio `eli:realizes` `na:id/1986/12/31/086U0917/CONSOLIDATED` per il TUIR. Da un URN si ricava quindi l'ELI. **norma certa**

Valutazione: ELI è utile come metadato di pubblicazione nel registro delle fonti, non come chiave del campo `riferimento`. Non arriva all'articolo e il suo identificativo non si ricava dagli estremi con cui si cita una norma. **prassi-interpretazione**

### 5. Norme regionali

- **Normattiva** contiene gli atti pubblicati in GU e/o nella Raccolta ufficiale. Per le regioni offre un motore federato che rimanda alla banca dati della singola Regione o Provincia autonoma, senza scaricare gli atti. La FAQ ammette che non tutte le regioni siano presenti. **norma certa** per il meccanismo; elenco delle regioni **da verificare**.
- **La Circolare AgID 2/2019** afferma che le banche dati delle assemblee legislative regionali adottano gli standard Normeinrete. **norma certa** come affermazione, non verificata regione per regione.
- **Toscana**, sito `raccoltanormativa.consiglio.regione.toscana.it`:
  - `articolo?urndoc=urn:nir:regione.toscana:legge:2005-02-24;40` apre la L.R. 24 febbraio 2005, n. 40. **norma certa**
  - `...;40:art2` risponde con la pagina della legge, ed è la forma usata nei link interni del sito. **norma certa**. Nel testo estratto non è stato possibile confermare che venga mostrato proprio l'art. 2. **da verificare**
  - `...;40~art2` e `...;99999` danno HTTP 200 con messaggio di caricamento fallito. **norma certa**
- Nessuna prova regionale ha mostrato un comma raggiungibile. La forma della partizione non è uniforme tra Normattiva e Toscana.

### 6. CCNL

**Codice CNEL**

- Il file ufficiale `ccnl-settore-pubblico.xlsx` del CNEL (aggiornato al 30/09/2026) riporta: `S105`, personale del comparto Funzioni Locali, codice comparto PA `FL`, inizio storia 21/02/2018; `S125`, area dirigenziale delle Funzioni Locali. **norma certa**
- Il codice è quindi un identificativo della linea contrattuale: comprende più rinnovi e non distingue il CCNL 2019-21 dal 2022-24. **norma certa** sul file; la lettura è **prassi-interpretazione**.

**Atti verificati su ARAN**

| CCNL | Sottoscrizione | Prova |
|---|---|---|
| Triennio 2019-2021 | 16/11/2022 | PDF aperto; art. 14 «Progressioni economiche all'interno delle aree», comma 1, Tabella A |
| Triennio 2022-2024 | 23/02/2026 | PDF aperto; FP CGIL e CGIL non firmatarie; art. 1 con commi numerati |
| Triennio 2025-2027 | 28/10/2026 | Pagina ARAN aperta; tutte le sigle indicate come firmatarie |

**Stabilità degli URL ARAN** (**norma certa**, osservazioni)

- Vecchio URL del CCNL `/contrattazione/comparti/.../13219-ccnl-2019-2021-...html`: redirige alla pagina generica `/contratti-aran/`. Il collegamento all'atto è perso.
- Stesso CCNL con due PDF: `wp-content/uploads/2022/11/2022_11_16_COMP-FL_2019-2021.pdf` e `wp-content/uploads/2024/06/CCNL-Comparto-Funzioni-Locali-2019-2021-16.11.2022.pdf`. Il primo è stato visto come link nella pagina e non scaricato, il secondo è stato scaricato.
- CCNL 2022-24 con due PDF di impronta diversa: `2026/02/CCNL-Comparto-2022-2024-23-02-26.pdf` e `2026/02/2026-02-23-CCNL-COMPARTO-FL-2022-2024-1.pdf`.
- Pagine `documento_pubblico/...` con ancore `#art.N`: 110 nel 2019-21, 60 nel 2022-24, nessuna nel 2025-27. Nessuna ancora per comma trovata.

**Date.** ARAN pubblica anche un'ipotesi del 03/11/2025 (`wp-content/uploads/2025/11/IPOTESI-FL-03-11-25-OK.pdf`) per un contratto poi sottoscritto il 23/02/2026. La data da citare deve essere quella della sottoscrizione definitiva, perché l'art. 2 del contratto fa decorrere gli effetti dalla stipulazione. Riferimento al testo del 2022-24: **norma certa**. Convenzione: **prassi-interpretazione**.

**Modifiche.** Un CCNL successivo può disapplicare o sostituire articoli di uno precedente: il 2022-24, per esempio, dichiara di sostituire gli artt. 3, 4 e 5 del CCNL 16/11/2022 e modifica la sua Tabella C. Il riferimento va quindi all'articolo del contratto che fonda il valore in quella vigenza. Non esiste multivigenza ufficiale dei CCNL. La pubblicazione in GU richiamata dal contratto è stata letta solo in quella clausola; gli estremi GU non sono stati cercati. **da verificare**

**Forma di citazione.** Nessuna fonte ufficiale aperta definisce una sintassi per articolo e comma di CCNL. `~art14-com1` è una scelta del progetto. **prassi-interpretazione**

### 7. INPS

- **Identificativo ufficiale.** Il documento riporta solo tipo, numero e data. I PDF aperti mostrano «Circolare n. 6», Roma 30/01/2026, e «Messaggio n. 749», Roma 20-02-2024. **norma certa**
- **Numeri non unici.** La circolare n. 6 esiste sia del 19/01/2023 sia del 30/01/2026. Servono quindi tipo, numero e data. **norma certa**
- **`idunivoco`.** `servizi2.inps.it/servizi/CircMessStd/VisualizzaDoc.aspx?tipologia=circmess&idunivoco=<id>` redirige alla pagina di dettaglio: 15151 per la circolare 6/2026, 14482 per il messaggio 749/2024, 14049 per la circolare 6/2023. L'ID è condiviso tra circolari e messaggi. **norma certa**. Che sia un identificativo garantito non risulta da alcuna documentazione trovata. **da verificare**
- **ID inesistente.** `idunivoco=99999999` porta con HTTP 200 all'elenco generale. Un URL di dettaglio con slug alterato o ID inventato risponde comunque 200. Lo stato HTTP non prova l'esistenza. **norma certa**
- **`content/dam`.** `.../circolari-e-messaggi/2026/01/Circolare_15151/Allegati/16546_Circolare-numero-6-del-30-01-2026.pdf` risponde 200. Il prefisso `16546` non si ricava dagli estremi, e anche il messaggio sta in una cartella `Circolare_14482`. `.../Allegati/x.pdf` dà 404. **norma certa**
- **`CircolariZIP` e `MessaggiZIP`.** Funzionano per atti storici già citati dal progetto, per esempio `Circolare numero 122 del 06-09-2019.pdf` e `Messaggio numero 2791 del 05-07-2017.pdf`. Danno 404 per gli atti recenti provati (circ. 6/2026, msg. 749/2024). Il percorso dipende dall'epoca. **norma certa**
- **Altro.** Tutti i link INPS citati nei documenti del progetto hanno risposto 200, con 2 redirect per pagine riorganizzate (open data). **norma certa**. Il feed `www.inps.it/it/it.rss.circolari.xml` espone titolo e link, ultima voce circolare n. 110 del 05-11-2026: è utile per la sorveglianza, non per l'identità. **norma certa**

### 8. Agenzia delle Entrate

- **Atti verificati**
  - Risoluzione 151/E del 13/12/2017: archivio e PDF.
  - Circolare 4/E del 16/05/2025: archivio e PDF.
  - Risposta a interpello n. 468 del 22/09/2022: archivio e PDF.
  - Provvedimento del 15/01/2026 sulla CU 2026, Prot. n. 15707/2026: PDF aperto, conferma il numero che la ricerca #4 dava da fonte secondaria.
  - Comunicato stampa del 16/01/2026: pagina aperta, senza numero.

  **norma certa**
- **Forma degli URL.** Coesistono più famiglie. **norma certa**
  - `/portale/documents/20143/<cartella>/<titolo>/<UUID>[?t=...]`
  - `/portale/documents/d/guest/<nome>`
  - `/portale/-/<slug>`
  - `/portale/web/guest/...` e `/portale/it/...`
- **Ruolo dell'UUID.** Con lo stesso UUID e titolo sostituito da `x.pdf` si ottiene lo stesso file (274.776 byte). Anche senza UUID, con il titolo originale, si ottiene lo stesso file. Sia UUID sia percorso con titolo risolvono, ma nessuno dei due è costruibile dagli estremi. **norma certa**
- **Slug non affidabili.** La pagina delle risposte di settembre 2022 ha l'URL `.../settembre-2022-intepelli`, con un refuso. Gli URL vanno quindi registrati, non costruiti. **norma certa**
- **Tenuta.** Tutti i link AdE già citati dal progetto rispondono 200, con 2 redirect dal dominio senza `www`. **norma certa**. È una sola osservazione, non una garanzia. **da verificare**
- **Numero.** I formati sono diversi: `151/E`, `4/E`, `468`, `15707/2026`. Per i provvedimenti il numero è un protocollo. **norma certa**. Nessun identificativo ufficiale unificato è stato trovato. **da verificare** (assenza di evidenza).

### 9. Atti dell'ente

Non esiste un identificativo nazionale dell'atto. L'ente è identificabile con il codice IPA: estratti di documenti AgID mostrano la forma `c_` più codice, per esempio `c_a035`. La corrispondenza con il codice catastale e la regola generale sono **da verificare** su IndicePA. Per il contratto integrativo esiste la banca dati ARAN-CNEL, ma il suo identificativo non è stato esaminato. **da verificare**

## Sintassi proposta

### Principi

1. La stringa identifica la fonte, **non contiene mai un URL**.
2. Lo schema dichiara il tipo di fonte, e quindi il livello: norma, contratto, prassi, atto dell'ente.
3. Per le norme si usa l'URN NIR **ufficiale così com'è**, in forma canonica.
4. La partizione usa una sola notazione, anche dove l'identificativo ufficiale si ferma prima.
5. Solo `urn:nir` è un identificativo pubblico. `ccnl:`, `prassi:` ed `ente:` sono nomi del progetto, volutamente non costruiti come `urn:`, per non far apparire ufficiale ciò che non lo è.

### Grammatica

```abnf
riferimento  = citazione *( " + " citazione )
citazione    = norma / contratto / prassi / atto-ente / fittizio

norma        = "urn:nir:" autorita ":" tipo ":" data [ ";" numero ] [ ":" allegato ]
               [ partizione ] [ versione ]
contratto    = "ccnl:" codice-cnel ":" data [ partizione ]
prassi       = "prassi:" emittente ":" tipo ":" data ";" numero [ partizione ]
atto-ente    = "ente:" codice-ente ":" tipo ":" data [ ";" numero ] [ partizione ]
fittizio     = "fittizio:" 1*( ALFANUM-MIN / "." / "-" )   ; solo test e demo

partizione   = "~" segmento *( "-" segmento )
segmento     = ( "art" / "com" / "let" / "num" / "par" / "pag" / "all" / "tab" ) valore
valore       = 1*ALFANUM *( "." 1*ALFANUM )                ; 2, 40bis, 8quinquies, 3.1, A
versione     = "!vig=" data / "@originale"

data         = AAAA "-" MM "-" GG                          ; data dell'atto, non di pubblicazione
numero       = 1*ALFANUM *( ( "." / "-" ) 1*ALFANUM )      ; "/" diventa "-": 151/E -> 151-E
                                                           ; senza numero in prassi: "sn" o "sn.<parola>"
allegato     = 1*DIGIT                                     ; posizione, come su Normattiva
codice-cnel  = 4 caratteri, lettera iniziale               ; S105
```

Regole aggiuntive che la sola regex non controlla:

- La data deve esistere.
- Ordine dei segmenti: `all` prima, poi `art`, `par` o `tab`, poi `com`, `let`, `num`. Nessun livello ripetuto.
- `urn:nir` richiede il numero, salvo `costituzione`.
- Rifiutare `presidente.repubblica:decreto`, indicando la forma canonica.
- `versione` è ammessa solo su `urn:nir`.
- Autorità, tipi ed emittenti sono controllati da elenchi chiusi, ampliati quando serve.

### Validatore

Provato il 06/11/2026 sugli esempi di questo documento: 25 stringhe valide accettate, 10 errate rifiutate.

```python
import re
from datetime import date

DATA = r"\d{4}-\d{2}-\d{2}"
TOK = r"[a-z0-9]+(?:\.[a-z0-9]+)*"
NUM = r"[A-Za-z0-9]+(?:[.-][A-Za-z0-9]+)*"
VAL = r"[0-9a-zA-Z]+(?:\.[0-9a-zA-Z]+)*"
SEG = rf"(?:art|com|let|num|par|all|tab){VAL}"
PART = rf"~{SEG}(?:-{SEG})*"
CIT = re.compile(rf"""^(?:
 (?P<nir>urn:nir:(?P<aut>{TOK}):(?P<tipo>{TOK}):(?P<data>{DATA})(?:;(?P<num>{NUM}))?(?::(?P<alleg>\d+))?)(?P<part>{PART})?(?P<ver>!vig={DATA}|@originale)?
|(?P<ccnl>ccnl:(?P<cnel>[A-Z][0-9A-Z]{{3}}):(?P<cdata>{DATA}))(?P<cpart>{PART})?
|(?P<prassi>prassi:(?P<ente>{TOK}):(?P<ptipo>{TOK}):(?P<pdata>{DATA});(?P<pnum>{NUM}))(?P<ppart>{PART})?
|(?P<atto>ente:(?P<ipa>[a-z0-9_]+):(?P<atipo>{TOK}):(?P<adata>{DATA})(?:;(?P<anum>{NUM}))?)(?P<apart>{PART})?
|(?P<fitt>fittizio:[a-z0-9.-]+)
)$""", re.X)
ORD = {"all": 0, "art": 1, "par": 1, "tab": 1, "com": 2, "let": 3, "num": 4}

def valida(r: str) -> str | None:
    """Restituisce None se valido, altrimenti il motivo del rifiuto."""
    if not r or r != r.strip():
        return "spazi"
    for c in r.split(" + "):
        m = CIT.match(c)
        if not m:
            return f"sintassi: {c}"
        d = m["data"] or m["cdata"] or m["pdata"] or m["adata"]
        if d:
            try:
                date.fromisoformat(d)
            except ValueError:
                return f"data: {c}"
        p = m["part"] or m["cpart"] or m["ppart"] or m["apart"]
        if p:
            o = [ORD[s[:3]] for s in p[1:].split("-")]
            if o != sorted(o) or len(set(o)) != len(o):
                return f"ordine partizioni: {c}"
        if m["nir"] and m["aut"] == "presidente.repubblica":
            return f"forma non canonica: {c}"
        if m["nir"] and m["tipo"] != "costituzione" and not m["num"]:
            return f"numero mancante: {c}"
    return None
```

Stringhe rifiutate nella prova:

- `art. 2 L. 335/1995`
- un URL
- data impossibile (`1995-13-08`)
- `urn:nir:presidente.repubblica:decreto:...`
- URN senza numero
- `!vig=` su un CCNL
- prassi senza numero né `sn`
- `151/E` non normalizzato
- partizioni in ordine invertito
- spazi iniziali

### Esempi

Tutti gli atti non fittizi sono stati verificati. L'atto verificato non implica che l'articolo sia il fondamento corretto di un dato parametro: quello va deciso nel corpus.

| Tipo | Riferimento | Fonte citata |
|---|---|---|
| Legge | `urn:nir:stato:legge:1995-08-08;335~art2-com18` | L. 335/1995, art. 2, c. 18 |
| D.P.R. | `urn:nir:stato:decreto.del.presidente.della.repubblica:1986-12-22;917~art51-com1` | TUIR, art. 51, c. 1 |
| D.P.R., versione esplicita | `urn:nir:stato:decreto.del.presidente.della.repubblica:1986-12-22;917~art11!vig=2020-01-01` | TUIR, art. 11, testo a quella data |
| D.Lgs. | `urn:nir:stato:decreto.legislativo:2001-03-30;165~art40bis` | D.Lgs. 165/2001, art. 40-bis |
| Testo unico allegato | `urn:nir:stato:decreto.legislativo:2026-06-19;117:1~art51` | D.Lgs. 117/2026, allegato, art. 51 |
| Regionale | `urn:nir:regione.toscana:legge:2005-02-24;40~art2` | L.R. Toscana 40/2005 (atto verificato); art. 2 mostra solo la forma, testo dell'articolo non letto |
| CCNL, articolo e comma | `ccnl:S105:2022-11-16~art14-com1` | CCNL FL 16/11/2022, art. 14, c. 1 |
| CCNL, tabella | `ccnl:S105:2022-11-16~tabA` | Stesso CCNL, Tabella A |
| CCNL | `ccnl:S105:2026-02-23~art1-com1` | CCNL FL 23/02/2026, art. 1, c. 1 |
| Circolare INPS | `prassi:inps:circolare:2026-01-30;6~par6` | Circ. 6/2026, par. 6, massimale annuo |
| Messaggio INPS | `prassi:inps:messaggio:2024-02-20;749` | Msg. 749/2024 |
| Risoluzione AdE | `prassi:ade:risoluzione:2017-12-13;151-E` | Ris. 151/E/2017 |
| Circolare AdE | `prassi:ade:circolare:2025-05-16;4-E` | Circ. 4/E/2025 |
| Risposta a interpello | `prassi:ade:risposta.interpello:2022-09-22;468` | Risposta 468/2022 |
| Provvedimento AdE | `prassi:ade:provvedimento:2026-01-15;15707-2026~par1.1` | Prot. 15707/2026, punto 1.1 |
| Prassi senza numero | `prassi:ade:comunicato.stampa:2026-01-16;sn` | Comunicato del 16/01/2026 |
| Delibera (**fittizia**) | `ente:c_x000:delibera.cc:2026-03-10;45~art3-com2` | Ente e atto inventati |
| Determina (**fittizia**) | `ente:c_x000:determina:2026-04-02;118` | Ente e atto inventati |
| CCI (**fittizio**) | `ente:c_x000:cci:2025-12-18~art5-com2` | Ente e atto inventati |

**Più fonti.** Il massimale annuo 2026 è fissato dalla circolare, che richiama la legge:

```
prassi:inps:circolare:2026-01-30;6~par6 + urn:nir:stato:legge:1995-08-08;335~art2-com18
```

Convenzione: la **prima** citazione è la fonte che fissa il valore; le successive sono il fondamento o il contesto.

### Identificativo logico e link di consultazione

Il link non sta nel `riferimento`. Lo calcola una funzione o lo fornisce un registro:

| Schema | Come si ottiene il link |
|---|---|
| `urn:nir:stato:*` | `https://www.normattiva.it/uri-res/N2Ls?` + URN senza `-com...` + `!vig=<data>` |
| `urn:nir:regione.toscana:*` | Adattatore: `raccoltanormativa.consiglio.regione.toscana.it/articolo?urndoc=...;40:art2` |
| altre regioni | Registro, finché non sono provate |
| `ccnl:`, `prassi:`, `ente:` | Registro delle fonti |

Registro delle fonti, una voce per atto, senza partizione:

```toml
[[fonte]]
id = "prassi:inps:circolare:2026-01-30;6"
titolo = "Determinazione per l'anno 2026 del limite minimo di retribuzione giornaliera..."
link = "https://www.inps.it/content/dam/inps-site/it/scorporati/circolari-e-messaggi/2026/01/Circolare_15151/Allegati/16546_Circolare-numero-6-del-30-01-2026.pdf"
sha256 = "<impronta del file scaricato>"
acquisita_il = 2026-11-06
```

### Quale versione della norma

- **Senza `!vig=`**, la data si ricava dal contesto: `dal` della `VigenzaParametro` o della `Regola`. In questo modo una regola valida dal 2026-01-01 apre il testo a quella data, non quello del 2027. **prassi-interpretazione** (scelta progettuale fondata sulle prove del finding 2).
- **Con `!vig=`** la citazione è statica: serve quando il testo citato non coincide con la decorrenza della regola.
- **Mai un link senza data** generato dal sistema.

### Fonti di prassi senza identificativo

- **Con numero:** il numero è parte obbligatoria dell'identità.
- **Senza numero** (comunicati, FAQ, pagine web, notizie): `;sn`, oppure `;sn.<parola>` se ce ne sono due dello stesso tipo nella stessa data. La voce nel registro diventa **obbligatoria**, con link, impronta e data di acquisizione, perché senza copia conservata l'identità non regge.
- **Pagine modificabili senza data:** usare la data di acquisizione e conservare la copia. Il sistema deve poterle segnalare come fonte debole. **prassi-interpretazione**
- **Atti dell'ente non ancora numerati o non disponibili:** il riferimento non si inventa. Finché non c'è l'atto non si registra il fatto come derivante da quell'atto.
- **Citazione non classificabile:** rifiutata. Nessuno schema `altro:` di ripiego, altrimenti si torna al testo libero.

## Implicazioni per il nucleo

1. **Nuovo modulo.** Un modulo di riferimento, per esempio `paghe/riferimento.py`, con `valida` e un parse che restituisca schema, atto, partizione e versione. `_riferimento_obbligatorio` in `corpus.py` lo richiama: il controllo oggi verifica solo una stringa non vuota.
2. **Nessuna rete nel calcolo.** La validazione sintattica sta nel caricamento del corpus. La verifica di esistenza è un controllo separato, da eseguire su richiesta o in CI.
3. **La verifica usa l'API, non il portale.** Il portale dà falsi positivi (finding 2). Passi:
   - togliere `-com...`;
   - chiamare `dettaglio-atto-urn`;
   - gestire sia `atto` sia `lista`;
   - confrontare il comma con la classe `comma-num-akn`;
   - segnalare articolo assente, abrogato o con vigenza che non copre la decorrenza.

   Il risultato va registrato, senza bloccare il calcolo se il servizio non risponde.
4. **Avviso sulle vigenze.** L'API restituisce `articoloDataInizioVigenza` e `articoloDataFineVigenza`. Si può quindi segnalare quando una regola senza `al` cita un articolo con fine vigenza nota: è il caso concreto di TUIR e D.P.R. 600 al 31/12/2026.
5. **Test.** Le stringhe `FITTIZIO...` in `tests/` e in `paghe/__main__.py` non sono conformi. Vanno migrate a `fittizio:`. Il test esistente sul riferimento vuoto resta valido e se ne aggiunge uno per stringhe malformate. Decidere se un corpus di produzione deve rifiutare `fittizio:`.
6. **Impronta del corpus.** `_impronta` include `riferimento`: la migrazione cambia l'impronta di ogni corpus. Va trattata come nuova versione del corpus, senza riscrivere gli esiti già registrati.
7. **`Atto` e registro.** `Atto` ha `riferimento` e `data`, e `registro.py` conserva `atto_riferimento`. Con `ente:` la data è già nella stringa: serve un controllo di coerenza, oppure si deriva. Si applica la stessa regola «solo sintassi valida», ma la migrazione dei fatti deve rispettare il vincolo che un fatto si corregge solo con un nuovo fatto.
8. **Tracciabilità.** La stringa va salvata tale e quale nella derivazione dell'importo. Il link può cambiare; l'identità registrata in un esito no.
9. **Glossario.** Può servire definire **fonte** in `CONTEXT.md` e distinguere **riferimento** (stringa, citazione puntuale) da **voce del registro** (metadati dell'atto). Il termine «Fonte» è usato oggi in modo informale.
10. **Punti critici noti.** Rischio dipendenza da NIR: la sostituzione formale con URN:LEX resta possibile. Il cambio di prefisso è meccanico e si può gestire nel parser, tenendo la forma canonica in un solo punto.

## Decisione del 06/11/2026

L'utente ha adottato la sintassi, con il vincolo che le regole seguano la normativa vigente e che si consulti il vault `vault-pa` (ADR 0003). L'implementazione è in `paghe/riferimento.py`. Rispetto al validatore qui sopra aggiunge il segmento `pag`, necessario per citare il documento tecnico UniEmens, e gli elenchi chiusi di autorità, tipi ed emittenti.

## Domande aperte

1. **Grammatica ufficiale NIR.** `normeinrete.it` non risponde. Dove AgID pubblica oggi la documentazione, e se `-com` e `-let` vi sono definiti? La lettera con estensione (per esempio lett. f-bis) non è stata osservata nei link: forma da fissare su casi reali.
2. **URN:LEX o NIR come forma canonica.** Oggi l'API accetta solo `urn:nir`, quindi la proposta è NIR. Da riesaminare se Normattiva o AgID annunciano il passaggio.
3. **Ripubblicazioni.** L'API restituisce due risultati per la L. 335/1995 (originale e ripubblicazione). Il validatore deve scegliere con una regola esplicita: da definire su più casi.
4. **Atti non numerati.** Normattiva non contiene DM e DPCM non numerati. L'articolo di Francesconi mostra `;nir-3` come numero per un decreto senza numero: non è stata provata la risoluzione. Le addizionali comunali e diversi parametri potrebbero dipendere da atti di questo tipo.
5. **Altre regioni.** Provata solo la Toscana. Quali regioni servono al progetto, e con quale adattatore? Il motore federato non espone un resolver documentato per URN.
6. **Codice CNEL fuori dal comparto.** Il personale correlato all'ente comprende dirigenza (`S125`) e segretari. Per i segretari, amministratori, co.co.co. e LSU/LPU il contratto o la fonte applicabile va stabilito caso per caso. Il codice S105 va ricontrollato a ogni aggiornamento del file CNEL.
7. **Estremi GU dei CCNL.** La pubblicazione in GU potrebbe offrire un riferimento ufficiale ulteriore: non cercata.
8. **Codice dell'ente.** Confermare su IndicePA che il codice IPA sia l'identificativo adatto, inclusi unioni, consorzi e province. In alternativa: codice fiscale, con dati da trattare come pubblici dell'ente e non personali.
9. **Giurisprudenza.** Circolare AgID 2/2019 indica ECLI per le sentenze. Se regole o parametri dovessero citare sentenze o deliberazioni della Corte dei conti, servirà un quinto schema: non progettato qui.
10. **Limiti d'uso dell'API.** Autenticazione, quote, stabilità. La specifica indica revisioni frequenti: va previsto che il controllo possa fallire senza invalidare il corpus.
11. **Riferimenti multipli.** ` + ` risolve il caso comune. Se serviranno ruoli più fini (fissa il valore, fondamento, interpreta), un campo strutturato sarebbe migliore. Da rivedere dopo aver trascritto un primo gruppo di parametri reali.

## Fonti aperte

- Normattiva: [Utilità](https://www.normattiva.it/staticPage/utilita), [FAQ](https://www.normattiva.it/staticPage/FAQ), [guida regioni](https://www.normattiva.it/staticPage/guidaAllUso_Regioni), [FAQ motore regionale](https://www.normattiva.it/mfr/static/faq), [specifica API](https://dati.normattiva.it/assets/come_fare_per/API_Normattiva_OpenData.pdf), [ELI in Italia](https://dati.normattiva.it/assets/come_fare_per/ELI_implementation_in_Italy.pdf)
- AgID: [Circolare 2/2019](https://www.agid.gov.it/sites/agid/files/2024-07/Circolare_2-2019_standard_patrimonio_informativo_di_natura_giuridica.pdf), [AIPA/CR/35](https://www.agid.gov.it/sites/default/files/repository_files/circolari/circolare-aipa-6-11-01_0.pdf)
- Standard: [RFC 9676](https://www.rfc-editor.org/rfc/rfc9676.txt), [registro IANA](https://www.iana.org/assignments/urn-namespaces/urn-namespaces.xml), [Francesconi et al.](https://xmleges.igsg.cnr.it/ita/images/stories/francesconiijli06.pdf)
- Regione Toscana: [L.R. 40/2005](https://raccoltanormativa.consiglio.regione.toscana.it/articolo?urndoc=urn:nir:regione.toscana:legge:2005-02-24;40)
- CNEL: [settore pubblico](https://www.cnel.it/archivio-contratti/entra-nell-archivio/contratti-collettivi-del-settore-pubblico), [file CCNL settore pubblico](https://www.cnel.it/media/docs/default-source/archivio-contratti---cartelle-excel/ccnl-settore-pubblico.xlsx?sfvrsn=e2b3bcd0_7)
- ARAN: [CCNL 2019-21](https://www.aranagenzia.it/documento_pubblico/contratto-collettivo-nazionale-di-lavoro-relativo-al-personale-del-comparto-funzioni-locali-triennio-2019-2021/), [CCNL 2022-24](https://www.aranagenzia.it/documento_pubblico/contratto-collettivo-nazionale-di-lavoro-relativo-al-personale-del-comparto-funzioni-locali-triennio-2022-2024/), [CCNL 2025-27](https://www.aranagenzia.it/documento_pubblico/contratto-collettivo-nazionale-di-lavoro-relativo-al-personale-del-comparto-funzioni-locali-triennio-2025-2027/)
- INPS: [circolare 6/2026](https://www.inps.it/content/dam/inps-site/it/scorporati/circolari-e-messaggi/2026/01/Circolare_15151/Allegati/16546_Circolare-numero-6-del-30-01-2026.pdf), [messaggio 749/2024](https://www.inps.it/content/dam/inps-site/it/scorporati/circolari-e-messaggi/2024/02/Circolare_14482/Allegati/14759_Messaggio-numero-749-del-20-02-2024.pdf), [feed circolari](https://www.inps.it/it/it.rss.circolari.xml)
- AdE: [risoluzione 151/E](https://www.agenziaentrate.gov.it/portale/documents/20143/302523/Risoluzione+n+151+del+13+dicembre+2017_RISOLUZIONE+N_151+DEL+13-12-2017.pdf/3fad92a8-5d48-a8cf-e2d7-2c94fed502c1), [circolari maggio 2025](https://www.agenziaentrate.gov.it/portale/maggio-2025-circolari), [interpelli settembre 2022](https://www.agenziaentrate.gov.it/portale/web/guest/settembre-2022-intepelli), [provvedimento CU 2026](https://www.agenziaentrate.gov.it/portale/-/provvedimento-del-15-gennaio-2026-cu), [comunicato 16/01/2026](https://www.agenziaentrate.gov.it/portale/-/comunicato-stampa-del-16-gennaio-2026)
