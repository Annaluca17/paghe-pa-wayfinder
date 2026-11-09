# Carichi di famiglia: un fatto per familiare, detrazione a mese

Le detrazioni per carichi di famiglia (art. 12 TUIR; dal 2027 art. 12 D.Lgs. 117/2026) sono **detrazioni a richiesta**: la persona le chiede registrando un **familiare a carico** per ogni familiare. È un fatto della persona con relazione, codice fiscale, data di nascita, percentuale, validità e documento di origine (art. 23 c. 2 lett. a D.P.R. 600/1973). Una variazione è un nuovo fatto datato. Il fatto non si registra senza codice fiscale valido.

- **Relazioni.** Coniuge, figlio, figlio con disabilità, ascendente convivente, e figlio in luogo del coniuge (casella «C» della CU), solo al 100%. Per il figlio in luogo del coniuge la convenienza la sceglie la persona: il modello non confronta.
- **A mese.** Le detrazioni sono «rapportate a mese» (c. 3, **norma certa**). In ogni periodo di paga la ritenuta applica 1/12 della detrazione annua per ogni familiare a carico nel mese di paga. Un mese conta intero se il fatto copre anche un solo giorno. Il conguaglio ricalcola mese per mese sull'imponibile dell'anno e somma i mesi a carico. Il criterio di 1/12 per mese è **da verificare**: nessuna fonte letta lo scrive per i carichi. Le detrazioni per carichi non si rapportano ai giorni di servizio, ma al conguaglio contano solo i mesi con almeno un giorno di servizio presso l'ente: chi cessa a giugno non riceve i carichi da luglio (**prassi**: istruzioni CU 2026, «in relazione al periodo di lavoro»; scelta di Luca nella rilettura).
- **Età.** Il modello ricava l'età dalla data di nascita. Il figlio dà detrazione dal mese del 21° compleanno al mese prima del 30°. Il figlio con disabilità la dà dal mese del 21° compleanno, senza limite (**prassi**: circ. AdE 4/E 2025 § 1.3). Fuori fascia il familiare resta registrato e non dà detrazione, con un avviso.
- **Reddito del familiare.** Il sostituto non lo conosce: registrare il fatto è l'attestazione della persona. Il modello non lo controlla.
- **Reddito complessivo R.** È lo stesso dell'art. 13: l'imponibile del periodo moltiplicato per i periodi nella ritenuta, l'imponibile dell'anno nel conguaglio. La soglia dei figli sale di 15.000 euro per ogni figlio dopo il primo che dà diritto alla detrazione nello stesso mese.
- **Versioni.** Gli importi 2026 e 2027 sono identici. Ci sono due versioni datate: la seconda dal 01/01/2027 cita l'art. 12 del testo unico. Il correttivo D.Lgs. 148/2026 non tocca le detrazioni del c. 1.

Scelto da Luca il 09/11/2026 nel grilling del ticket #98, domande 1-7. Precisa l'ADR 0019 sulla dichiarazione del sostituito. Fonti nella ricerca `docs/research/carichi-di-famiglia.md`.

## Considered Options

- **Giorni a carico su 365, come l'art. 13:** la norma dei carichi parla di mese.
- **Mese di competenza:** più preciso sugli arretrati in corso d'anno, ma il conguaglio li corregge comunque.
- **Elenco dei familiari dentro un'unica dichiarazione:** ogni variazione riscriverebbe tutto l'elenco e perderebbe la data della singola variazione.
- **Mesi a carico indicati solo dalla persona, senza controllo dell'età:** un figlio che compie 30 anni resterebbe a carico finché nessuno chiude il fatto.
- **Familiare senza codice fiscale registrato senza detrazione:** lascerebbe fatti a metà; la norma chiede il codice.
- **Reddito annuo stimato come per la somma esente:** due redditi diversi per due detrazioni dello stesso mese.

## Consequences

- Restano fuori, con un ticket proprio se servono: l'esclusione dei familiari residenti all'estero per chi non è cittadino italiano, UE o SEE (c. 2-bis); la richiesta di fruire dei carichi per l'intero anno con un rapporto più breve (codice AC della CU); i campi della CU.
- Restano **da verificare**: il criterio di 1/12 per mese, il troncamento del rapporto alla quarta cifra decimale (si usa lo stesso dell'art. 13), le detrazioni sulle mensilità aggiuntive.
- **Trattamento integrativo.** Tra 15.000 e 28.000 euro il trattamento integrativo (ADR del ticket #95) confronta con l'imposta lorda la somma delle detrazioni, che comprende quelle dell'art. 12 (D.L. 3/2020 art. 1 c. 1, secondo periodo: elenco degli articoli **da verificare** sul testo, non riletto in questo ticket). La formula del corpus legge i carichi dello stesso periodo come `fisco.carichi`.
