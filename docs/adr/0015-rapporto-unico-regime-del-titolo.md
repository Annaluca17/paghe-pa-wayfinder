# Rapporto unico per ogni titolo; regime, output e reddito come dichiarazioni

Il **rapporto** resta un solo concetto per ogni **titolo di compenso** (lavoro dipendente, mandato di amministratore, co.co.co., LSU/LPU, incarico). Il titolo è fissato alla nascita: un titolo diverso è un rapporto nuovo, non una variazione. Il rapporto esiste anche senza importi, se un lettore ne ha bisogno, come per l'LSU pagato da INPS che il Conto Annuale chiede in Tab. 2.

Il **regime del titolo** non è un'entità del registro. È l'insieme delle dichiarazioni del corpus per quel titolo: istituti, basi, concorsi, regole, fermi e output. Il motore non ha rami per titolo. Le dichiarazioni nuove seguono lo schema del concorso (ADR 0005), con date e riferimento, e se mancano il calcolo si ferma:

- **Categoria di reddito.** Ogni istituto dichiara una categoria logica del modello, senza articoli nel nome. Il riferimento si sceglie in base all'anno d'imposta a cui il pagamento è attribuito, quindi con la cassa allargata dove vale. Quando una norma è abrogata cambia il riferimento, non la categoria.
- **Classificazione e origine dell'impegno.** Ogni istituto dichiara la classificazione ufficiale e se l'impegno è automatico col bilancio o nasce da un atto del registro.
- **Output obbligatori.** Li dichiara il regime, eventualmente con una condizione su un fatto. Una vista prende i rapporti che il regime le assegna e non conosce i titoli.

Il **controllo di completezza degli output** verifica che ogni importo pagato sia compreso in ogni output dichiarato, o ne sia escluso da una dichiarazione esplicita. Un'assenza non dichiarata ferma l'invio di quell'output, non il calcolo.

Scelto da Luca il 06/11/2026 nel grilling del ticket #19, domande 1, 8, 9, 12, 17 e 19. I meccanismi che servono ai titoli sono gli stessi (frazioni, cassa, esiti, proposte), e un sottotipo li duplicherebbe. Il D.Lgs. 117/2026 e il D.Lgs. 33/2025 cambiano dal 01/01/2027 articoli e lettere di tutti questi redditi (ricerca `regimi-titolo-compenso.md`, sezione 13): una chiave basata sull'articolo andrebbe riscritta ovunque.

## Considered Options

- **Sottotipi di rapporto con struttura propria:** ogni regola, vista e lettore dovrebbe distinguerli.
- **Titolo come fatto datato:** un passaggio da co.co.co. a dipendente sembrerebbe una variazione, ma atti, basi e denunce sono diversi.
- **Non dipendenti come pagamenti a terzi:** escluderebbe questi importi da provenienza, CU e proposte.
- **Rapporto solo se l'ente paga:** la Tab. 2 chiede dati anche su chi non costa nulla.
- **Articolo del TUIR come chiave del reddito:** si riscriverebbe tutto il 01/01/2027 e a ogni riordino.
- **Una sola categoria «assimilati»:** amministratori e collaboratori hanno punti CU e detrazioni diversi (istruzioni CU 2026: punto 4 e art. 13 c. 5; punti 1-2 e art. 13 c. 1).
- **Filtro per titolo in ogni vista:** un titolo nuovo uscirebbe in silenzio dagli output in cui nessuno ha aggiunto il filtro.
- **Dati dedicati al Conto Annuale sul rapporto:** due verità, contro l'ADR 0012.

## Consequences

**Norma certa**

- Piano dei conti: U.1.03.02.01.001 e .002 (organi), U.1.03.02.12.003 (collaborazioni), U.1.03.02.12.002 (LSU), U.1.09.01.01.001 ed E.3.05.02.01.001 (rimborsi di personale).
- Art. 183 c. 2 lett. a) TUEL: l'impegno automatico riguarda il «personale dipendente».
- Circolare RGS 12/2026: co.co.co. in Scheda 1 e L111, LSU in Tab. 2, amministratori non rilevati. Numeratore della Scheda A33 con U.1.01 e U.1.03.02.12.

**Prassi-interpretazione**

- Amministratori e co.co.co. fuori dall'impegno automatico, con impegno all'atto.
- I limiti di spesa sono viste che leggono le classificazioni e non fermano nulla. La vista dell'art. 33 espone il numeratore RGS e, a parte, i rimborsi U.1.09: la Lombardia 125/2020, letta tramite commento, conta la quota degli enti convenzionati, che l'estrazione RGS non prende. La scelta è dell'ente.

**Conseguenze sul modello**

- **Co.co.co.:** compenso da **piano di rate** da atto, ogni rata matura come evento (ADR 0004), con l'**attestazione della prestazione** come condizione della proposta.
- **Gestione separata:** base propria e quote come per la CPDEL (ADR 0007); massimale con cumulo che ferma; **lista collaboratori** come vista propria.
- **LSU/LPU:** l'assegno pagato da altri non è un importo dell'ente. L'integrazione matura sulle presenze.
- **Voci SICO:** mappature datate dell'istituto per anno di rilevazione.

**Da verificare prima del corpus reale**

- Il D.M. 17/03/2020 sul testo e la circolare 13/05/2020.
- L'effetto del d.l. 144/2026 sulla clausola dell'art. 9 c. 28 d.l. 78/2010.
- Contribuzione e flusso sull'integrazione LSU; chi certifica l'assegno INPS.
- Il punto dell'allegato 4/2 per collaboratori e organi.
- Il confronto parola per parola del D.Lgs. 117/2026 e il successore dell'art. 19 c. 2-bis TUIR.
- La causale F24EP (C10 o CXX) per aliquota e l'esposizione della cassa allargata nella lista collaboratori.

**Precisazioni ad altri ADR**

- ADR 0010: la riduzione TFR resta senza effetti fiscali, ma il fiscale non è più fuori dal modello.
- ADR 0012: un tipo di fatto entra con un lettore anche per un rapporto senza importi.
- ADR 0013: l'origine dell'impegno è dichiarata dall'istituto.
