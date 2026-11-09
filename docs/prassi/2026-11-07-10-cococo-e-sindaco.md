# Nota di prassi 10: co.co.co. e sindaco

Riferimento: `prassi:immedia:nota:2026-11-07;10`. Fonte: decisioni di Luca del 07/11/2026 nel grilling del ticket #73 e ricerca `docs/research/regimi-titolo-cifre-2026.md`, sezioni 3 e 4. Corpus: `corpus/funzioni-locali-cpdel.toml`.

## Rata e attestazione

**Input da atto.** Il piano di rate e' un insieme di fatti `rata_collaborazione`, uno per rata, validi nel giorno di scadenza, con il contratto come atto. Ogni rata matura come evento nel giorno della scadenza (ADR 0004).

**Scelta di progetto.** L'attestazione della prestazione e' un fatto `attestazione_prestazione` che deve coprire tutti i giorni dell'importo. Il corpus la dichiara come `condizione_di_proposta` dell'istituto: senza, la rata resta calcolata e visibile tra gli esclusi, e non entra in una versione. Nessuna fonte la richiede: e' una scelta dell'ente, prassi-interpretazione. Il totale del compenso e la durata del piano non sono controllati sulla somma delle rate.

## Gestione separata del collaboratore

**Norma certa** (Circ. INPS 8/2026 par. 1, valori 2026): IVS 33,00% per chi non ha altra copertura e non e' pensionato, 24,00% per pensionati e iscritti ad altra forma obbligatoria (art. 1 c. 79 L. 247/2007); aliquote aggiuntive 0,72% (0,50 + 0,22); DIS-COLL 1,31%. Totale 35,03% senza altra cassa, 33,00 + 0,72 + 1,31. Ripartizione 2/3 committente e 1/3 collaboratore (art. 2 c. 30 L. 335/1995; Circ. 8/2026 par. 4.1).

**Prassi-interpretazione.**

- Il corpus modella la posizione previdenziale con tre codici: `gestione_separata` (solo gestione separata, non pensionato), `pensionato`, `altra_cassa`. L'aliquota si sceglie dal codice, con un istituto di totale per codice.
- Per pensionati e altra cassa il totale e' 24,00 + 0,72 = 24,72%, **senza DIS-COLL**: che la DIS-COLL non sia dovuta a pensionati e altra cassa e' norma certa (circ. INPS 122/2017 e 8/2026). **Aperto:** il totale 24,00% (testo letterale) contro 24,72% resta tale finche' non c'e' una seconda fonte indipendente (ADR 0003, ticket #104).
- Quota del collaboratore: un terzo del totale, arrotondato; quota dell'ente per differenza, come la CPDEL (nota di prassi 3).
- Le aliquote valgono per il 2026: dal 01/01/2027 il calcolo si ferma finche' la circolare 2027 non e' nel corpus.

**Massimale.** 122.295,00 euro nel 2026 (Circ. INPS 8/2026 par. 6.1 e Circ. 14/2026). Lo applica la base: la base del mese e' cio' che resta sotto il massimale, sommando i mesi dell'anno nello stesso ente. Un mese che lo supera contribuisce solo sulla parte sotto, i mesi dopo sono a zero. Un fatto di cumulo con altri committenti (`cumulo_altri_committenti`) ferma il calcolo: il cumulo tra committenti non si modella. Anche piu' rapporti della stessa persona fermano la denuncia (corpus, ADR 0007).

## Categoria di reddito, F24EP e IRPEF

Le categorie di reddito (collaborazione, CU punti 1-2; carica elettiva, CU punto 4), la ritenuta, la deduzione della quota del collaboratore e la composizione stanno solo nel corpus fittizio, con valori finti (ADR 0003): il corpus reale non le dichiara per nessun titolo.

**Causale F24EP della gestione separata (ticket #104), prassi per analogia.** C10 per `pensionato` e `altra_cassa`, CXX per `gestione_separata` e per l'onere dell'art. 86 (circ. INPS 88/2023 sez. 10.1.1, sul lavoro sportivo; ris. AdE 98/E/2010; circ. INPS 23/2013 par. 2.2). Il codice di quota collaboratore e quota ente segue la posizione previdenziale del rapporto; se manca la posizione la delega ha un dato mancante che nomina il rapporto, se non ha causale si ferma. Riferimento A = mese e anno di pagamento (`MMAAAA`). Aperti: la lettura del messaggio INPS 8460/2013 e della tabella AdE dopo il 01/04/2020.

## Lista collaboratori

Vista propria, separata dalla ListaPosPA, per il mese di erogazione. Legge base e contributi della gestione separata e, a parte, la quota forfettaria, che non sta su una base. **I codici del tracciato non sono stati letti sul testo ufficiale**: la vista resta una bozza non trasmissibile e non ne inventa. L'esito dichiarato non e' prodotto finche' la vista e' una bozza.

**Cassa allargata.** Una somma pagata entro il 12 gennaio e attribuita all'anno d'imposta prima fa della lista una bozza: nessuna fonte dice in quale mese di erogazione esporla. Il tracciato la distingue o no: da verificare.

## Sindaco

**Indennita' di funzione.** La misura mensile piena e' un input da atto (ADR 0016), a giorni sul mese di calendario. L'importo atteso per fascia di popolazione non e' una regola: e' nominato (fermo su `fascia_popolazione`). Percentuali e base di 13.800 euro (L. 234/2021 c. 583) non sono nel corpus.

**Dimezzamento.** Art. 82 c. 1 TUEL: dimezzata per il lavoratore dipendente che non ha chiesto l'aspettativa. Una regola sulla condizione lavorativa produce un importo negativo, pari alla meta' dell'indennita' della stessa frazione: se la condizione cambia a meta' mese, dimezza solo i giorni da quel giorno. Una sola fonte (Normattiva): **da verificare**.

**Esclusa da ogni base.** L'indennita' e il suo dimezzamento sono dichiarati esclusi da tutte le basi, gestione separata compresa. **Prassi-interpretazione**: nessun testo INPS letto lo dice in forma espressa; e' una lettura dell'art. 86.

**Quota forfettaria dell'art. 86 c. 2.** Una regola decide il diritto: carica `sindaco`, condizione lavorativa `non_dipendente`, posizione previdenziale `gestione_separata`, tutte e tre insieme (`anche_se`). Se non spetta non nasce nessun importo. Se spetta: minimale 2026 di 18.808,00 euro (Circ. INPS 8/2026 par. 6.2 e Circ. 14/2026) per l'aliquota 33,72% degli amministratori di enti locali (tipo 04, Circ. 8/2026), un dodicesimo, cioe' 528,51 euro al mese, a carico dell'ente. **Prassi-interpretazione:** il D.M. 25/05/2001 art. 2 lett. v) e la Circ. INPS 205/2001 dicono di applicare l'aliquota vigente al minimale; nessuna fonte INPS applica il minimale 2026 all'art. 86 espressamente. Il corpus segue la Cassazione (ord. 24615/2023) contro la Corte dei conti Liguria 21/2019: non guarda se l'amministratore esercita un'attivita' professionale. La quota e' un onere dell'ente (maturazione `onere`): non e' reddito della persona e non concorre a nessuna base.

**Carica diversa dal sindaco.** Misura e quota sono modellate solo per il sindaco: un'altra carica ferma il calcolo (`carica` obbligatoria, valore ammesso `sindaco`). Una posizione previdenziale diversa dalla gestione separata, o assente, ferma il calcolo: la quota verso altre casse e' nominata e non modellata.

## Fermi nominati

Co.co.co.: cumulo con altri committenti, INAIL (`inail_dovuta`), IRAP (`irap_dovuta`; la delega ferma comunque una riga IRAP), posizione previdenziale ignota, cassa allargata nella lista. Sindaco: condizione lavorativa ignota, aspettativa (oneri del c. 1 e rimborsi al datore, art. 80), gettoni e tetto (`presenza_seduta`), rimborsi al datore (`rimborso_datore_lavoro`), fine mandato (`indennita_fine_mandato`), importo atteso per fascia (`fascia_popolazione`), INAIL, carica e posizione fuori dal regime.

## Meccanismi del motore introdotti

Generici e validati nel corpus; nessun ramo per titolo:

- **`condizione_di_proposta`:** un fatto che l'istituto richiede perche' l'importo entri in una versione.
- **`anche_se`:** altre condizioni `tipo=codice` che devono valere insieme ad `applica_se`.
- **Maturazione `onere`:** come `giorni`, ma a carico dell'ente (non reddito, non base).
- **`massimale` della base:** un parametro annuo che limita la base di ogni mese.
- **`output`:** le basi o gli istituti con cui il regime assegna i rapporti a una vista (`rapporti_della_vista`).

## Quando rivedere

Quando un testo INPS dice la causale F24EP della gestione separata, il tracciato della lista collaboratori e il trattamento della DIS-COLL per chi ha altra cassa; quando esce la circolare INPS 2027 su aliquote e massimale; quando un'altra fonte conferma il dimezzamento o applica il minimale 2026 all'art. 86.
