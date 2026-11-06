# Arrotondamenti imposti da norma e da istruzioni ufficiali

Ticket: #15 (mappa #1). Branch: research/arrotondamenti-norma. Data: 2026-11-06.

## Domanda

Quali arrotondamenti sono imposti da norma o da istruzioni ufficiali (contributi ex INPDAP e UniEmens/ListaPosPA, IRPEF e conguaglio, addizionali regionali e comunali, F24EP, CU/770), a quale livello (importo, totale per periodo, rata, dichiarazione) e con quale fonte? Quali sono solo prassi? Priorità: fetta CPDEL di un dipendente del comparto fino alla ListaPosPA.

## Metodo e legenda

**Marcature.**
- **norma certa**: testo primario aperto e letto; comprende le istruzioni ufficiali (INPS, Agenzia delle Entrate), indicate come tali perché vincolano la compilazione ma non sono legge.
- **prassi-interpretazione**: prassi, deduzione mia, fonte non ufficiale o documento ufficiale usato per analogia.
- **da verificare**: non letto sulla fonte primaria, anche se riportato altrove.

**Come si è letto.** Le fonti sono identificate da una sigla (sezione Fonti). Tre modalità:
- [T] PDF ufficiale salvato da WebFetch e convertito in testo con `pdftotext`: letto direttamente, pagine = pagine PDF.
- [W] pagina HTML aperta con WebFetch: la lettura passa da un modello estrattore, quindi non è il testo grezzo. Un'assenza ("non parla di arrotondamento") ha peso minore.
- [E] solo estratto del motore di ricerca: marcatura sempre **da verificare**.

**Aperto:** documento tecnico UniEmens 4.33, allegato tecnico 4.33.1, schema XSD 4.33.1, istruzioni e specifiche CU 2026 e 770/2026, specifiche F24 EP, avvertenze F24, istruzioni 730/2026, circolari e messaggi INPS, articoli su Normattiva.

**Non aperto:**
- **Manuale operativo ListaPosPA v1.0 (13/02/2018), che contiene i controlli 00171I/00172I.** Il PDF (10,6 MB) supera il limite di WebFetch (10 MB) e il pannello browser ha rifiutato inps.it. Non l'ho scaricato per altra via perché il download di file richiede un consenso esplicito dell'utente. Ne ho solo estratti di ricerca. Serve la lettura diretta: vedi Domande aperte.
- Regolamento CE 1103/97: EUR-Lex restituisce una pagina vuota.
- Messaggio INPS 4025/2017: URL riportato da fonte secondaria, risposta HTTP 404.
- L. 296/2006, art. 1, c. 168: la pagina Normattiva si ferma ai commi 1-100.
- Testi di D.Lgs. 117/2026 e D.Lgs. 33/2025: nessun articolo letto su Normattiva.

**Normattiva.** L'URL senza data mostra il testo in vigore dal 01/01/2027, con TUIR e art. 23 DPR 600 abrogati. Ho quindi aggiunto `!vig=2026-11-06` per il testo oggi vigente.

**Piste non normative.** Il catalogo `docs/research/conoscenza-tool.md` e il codice di `uniemens-builder-dma2` sono serviti solo a capire cosa cercare. Nessun flusso reale è stato aperto.

## Sintesi

1. **ListaPosPA: imponibile e contributo si espongono entrambi al centesimo, con al massimo 2 decimali e terza cifra 0-4 per difetto, 5-9 per eccesso** (DT p. 31 e p. 188). Vale per CPDEL, TFS, TFR, Fondo Credito e Ente Versante. **norma certa** (istruzione ufficiale).
2. **"Arrotondamento all'unità di euro per i contributi" è vero solo per la gestione privata**, cioè per l'imponibile di `DatiRetributivi` e il DM10 (DT p. 52; Circ. 208/2001). Per la ListaPosPA l'istruzione vigente prevede i centesimi. **norma certa**. Una fonte scolastica del 2004 parlava di unità di euro anche per il personale statale: è storica e non è INPS (B5).
3. **La ListaPosPA ha un solo contributo per periodo, che somma quota ente e quota lavoratore** (DT p. 188). Nessuna fonte aperta dice se si arrotonda il totale o ciascuna quota, e i due metodi differiscono di 1 centesimo in casi reali. **Da decidere:** è il punto che blocca la fetta CPDEL (B3).
4. **00171I e 00172I, stando agli estratti del manuale, sono disuguaglianze sulle somme**: gestione ≥ somma degli Enti Versanti. Non ricalcolano l'aliquota e gli estratti non mostrano tolleranze. **da verificare**. Il controllo a due vie del builder è una scelta del tool, non una regola INPS letta.
5. **Non ho trovato alcuna regola o tolleranza ufficiale sul rapporto tra somma delle denunce e versamento F24 EP.** La specifica F24 EP chiede solo centesimi e la coerenza interna della delega (p. 4, p. 9).
6. **CU e 770: tutti gli importi al centesimo, per legge dal 2012** (art. 3, c. 12, DL 16/2012, che modifica l'art. 1 L. 935/1977). **norma certa**. Le istruzioni del 730 restano invece all'unità di euro.
7. **IRPEF e addizionali: negli articoli letti (art. 11 e 51 TUIR, art. 23 DPR 600, art. 1 D.Lgs. 360/1998, art. 50 D.Lgs. 446/1997) non c'è una regola di arrotondamento** della ritenuta, del conguaglio o della rata (lettura [W]). L'arrotondamento nasce all'esposizione: F24 e dichiarazione.
8. **Le norme citate nel ticket non sono regole payroll.** L'art. 51 D.Lgs. 213/1998 riguarda la conversione delle sanzioni in lire. L'art. 3 D.Lgs. 213/1998 riguarda i calcoli intermedi di conversione. L'art. 3 TUIR è la base imponibile e non arrotonda nulla (lettura [W]).
9. **Soglia pertinente: 12 euro per il 730**, sotto cui il sostituto non versa né rimborsa la singola imposta (730 p. 8). I 30 euro dell'art. 3, c. 10, DL 16/2012 riguardano la riscossione degli uffici, non la busta paga.
10. **Il mezzo per eccesso basta**, se opera sul valore assoluto: lo fa già il `ROUND_HALF_UP` di `paghe/formula.py`. La modalità "per difetto" non serve a nessuna regola trovata. Il nucleo però dovrà poter ripartire un residuo (Implicazioni).
11. **Dal 01/01/2027 cambiano i riferimenti:** D.Lgs. 117/2026 abroga il TUIR e l'art. 23 DPR 600 risulta abrogato (Normattiva). Le regole del nucleo devono citare i riferimenti con vigenza.

## Tabella riassuntiva

| Adempimento | Dato | Livello | Regola | Decimali | Fonte puntuale | Certezza |
|---|---|---|---|---|---|---|
| ListaPosPA | `Imponibile`, `Contributo` di GestPensionistica (CPDEL = cod. 2) | Rapporto, periodo (E0/V1) | Terza cifra 0-4 giù, 5-9 su | Max 2 | DT p. 31, p. 188; XSD `ImportoConDecConSegno`; AT p. 251 ss. per i codici | norma certa (istruzione) |
| ListaPosPA | `Contrib1PerCento` | Periodo | Come sopra; può essere negativo | Max 2 | DT p. 188-189 | norma certa (istruzione) |
| ListaPosPA | `ImponibileTFS`, `ContributoTFS`, `ImponibileTFR`, `ContributoTFR` | Periodo | Come sopra | Max 2 | DT p. 191-193 | norma certa (istruzione) |
| ListaPosPA | `Imponibile`, `Contributo` di GestCredito | Periodo | Come sopra | Max 2 | DT p. 193 | norma certa (istruzione) |
| ListaPosPA | `AltroEnteVersante`, `EnteVersante` | Riga per tipo contributo ed erogazione | Come sopra | Max 2 | DT p. 195, p. 214 | norma certa (istruzione) |
| ListaPosPA | Quota ente e quota lavoratore | Non esposte separatamente | Nessuna regola trovata | n.d. | DT p. 188 | prassi-interpretazione |
| ListaPosPA | 00171I/00172I | Somma EV contro gestione | Gestione ≥ somma EV; nessuna tolleranza negli estratti | n.d. | MAN, estratti | da verificare |
| UniEmens privati (contrasto) | `Imponibile` di DatiRetributivi | Mese | Unità di euro | 0 | DT p. 52; Circ. 208/2001 | norma certa (istruzione) |
| Parametri INPS | Massimale annuo | Parametro | Dato già all'unità di euro | 0 | Circ. 26/2025 p. 6 | norma certa (istruzione) |
| F24 EP | Importi di riga | Riga della delega | Espressi in centesimi | 2 | F24EP p. 4 | norma certa (istruzione) |
| F24 EP | Saldo totale | Delega | Coerente con la somma dei saldi dei record V | 2 | F24EP p. 9 | norma certa (istruzione) |
| F24 ordinario | Importo | Riga | Terza cifra ≥ 5 su, altrimenti giù | 2 | AVV p. 1; scheda F24 [W] | norma certa per F24; per F24 EP prassi-interpretazione |
| F24 EP contro ListaPosPA | Totale denunciato contro versato | Ente, mese | Nessuna regola trovata | n.d. | Solo Q&A non ufficiale | prassi-interpretazione |
| IRPEF | Ritenuta mensile, conguaglio | Rapporto o persona | Nessuna regola negli articoli letti | n.d. | Art. 11 TUIR, art. 23 DPR 600 | norma certa per il contenuto; assenza con riserva [W] |
| Addizionali | Rata | Rata mensile | Max 9 o 11 rate; nessun arrotondamento nel testo | n.d. | Art. 1, c. 5 D.Lgs. 360/98; art. 50, c. 4 D.Lgs. 446/97 | norma certa per le rate; assenza con riserva [W] |
| CU | Tutti gli importi fiscali | Certificazione | Terza cifra ≥ 5 su, altrimenti giù | 2 | CUI p. 17; CUS p. 13; DL 16/2012 art. 3, c. 12 | norma certa |
| CU | Dati previdenziali | Certificazione | Stessa regola | 2 | CUI p. 68 | norma certa (istruzione) |
| 770 | Tutti gli importi | Dichiarazione | Seconda cifra decimale | 2 | 770I p. 7; 770S p. 10; L. 935/77 art. 1, c. 2 | norma certa |
| 730 | Importi in dichiarazione | Dichiarazione | ≥ 0,50 su, altrimenti giù | 0 | 730 p. 16; L. 935/77 art. 1, c. 1 per il principio | norma certa (istruzione) |
| 730 | Debito o credito per singola imposta | Conguaglio | ≤ 12 euro: né versamento né rimborso | n.d. | 730 p. 8 | norma certa (istruzione) |
| Art. 51 D.Lgs. 213/98 | Sanzioni convertite da lire | Conversione | Eliminazione dei decimali | 0 | Normattiva | norma certa; non pertinente |

## Findings per dominio

### A. Regola generale di esposizione in UniEmens

A1. **Importi contributivi con decimali.** Si espongono in unità di euro, virgola e massimo 2 decimali; "1234,567" è un esempio errato. La regola è «per i millesimi da 0 a 4 al centesimo inferiore» e da 5 a 9 al superiore. Fonte: DT v. 4.33 del 29/09/2026, "indicazioni generali", p. 31. **norma certa** (istruzione ufficiale, [T]).

A2. **Lo schema impone il formato ma non calcola.** Il tipo XSD `ImportoConDecConSegno` ammette segno, massimo 9 cifre intere e 1-2 decimali, senza zeri a sinistra né migliaia. Ammette `0` e, ad esempio, `0,50`. Il XSD 4.33.1 respinge "1234,567", ma non può verificare che l'arrotondamento sia giusto. Fonte: XSD 4.33.1. **norma certa** ([T]). Segnalo una divergenza minore: il DT dice lunghezza massima 12, lo schema `maxLength` 13.

A3. **La regola non è nuova.** Compare, secondo un estratto, anche nel documento tecnico allegato alla Circ. INPS 13/2011. **da verificare** ([E]). La data d'origine della regola resta aperta.

A4. **Due copie del DT.** Il percorso `uniemens-enti-amministrazioni` serve la v. 4.33; il percorso `uniemens-aziende-private` serve ancora la v. 4.29 del 28/02/2025. Ho letto la 4.33, indicata dalla scheda INPS come corrente. **norma certa** per le versioni osservate.

### B. CPDEL, TFS/TFR e Fondo Credito in ListaPosPA

B1. **Imponibile al centesimo.** `Imponibile` di `GestPensionistica` segue la regola con decimali (p. 188). Non è previsto l'arrotondamento all'unità di euro. **norma certa** (istruzione). Nell'Allegato al Messaggio 749/2024 compaiono però solo imponibili interi, quindi gli esempi non mostrano un caso con centesimi.

B2. **Contributo al centesimo, riferito al periodo.** Il `Contributo` è il totale dei contributi pensionistici per il periodo, e deve essere minore dell'imponibile (p. 188). **norma certa** (istruzione). CPDEL è il codice gestione 2 (AT, appendice B). **norma certa**.

B3. **Quote ente e lavoratore: nessuna regola trovata.** Il tracciato ha un solo importo. La CU chiede invece i "contributi dovuti" (entrambe le quote, punto 19) e quelli "a carico lavoratore trattenuti" (punto 20): CUI p. 74. **norma certa** per la struttura. Di conseguenza una quota lavoratore arrotondata esiste comunque. Non ho trovato una fonte primaria che scelga tra i due metodi:

| Imponibile | Totale al 32,65% | Ente 23,80% | Lavoratore 8,85% | Somma quote |
|---|---|---|---|---|
| 150,00 | 48,98 | 35,70 | 13,28 | 48,98 |
| 150,10 | 49,01 | 35,72 | 13,28 | **49,00** |
| 2.098,00 | 685,00 | 499,32 | 185,67 | **684,99** |

L'aliquota totale 32,65% è ricavata dagli esempi del Messaggio 749/2024 (2.000 → 653,00; 1.500 → 489,75). La ripartizione 23,80 + 8,85 viene dal catalogo tool ed è solo illustrativa: **da verificare** come parametro. L'esempio ufficiale con 150,00 → 48,98 è compatibile con entrambi i metodi, quindi non decide. **prassi-interpretazione**.

Proposta argomentata: calcolare il totale come `arrotonda(imponibile × aliquota totale, 2)` e la quota lavoratore come `arrotonda(imponibile × aliquota lavoratore, 2)`, con la quota ente come differenza. Così il totale è quello che il tracciato chiede e la ritenuta è determinata in modo autonomo. **prassi-interpretazione** da far confermare con il manuale o con INPS.

B4. **Ripartizione tra periodi e Ente Versante.** Nel V1 causale 5 dell'Allegato al Messaggio 749/2024, caso 1, il contributo totale è 701,98. È la somma di 653,00 e 48,98; anche 2.150 × 32,65% dà 701,975, cioè 701,98. Nel caso 2 il totale è 1.142,75 (653,00 + 489,75). Gli esempi mostrano quindi somma di importi già al centesimo, ma non escludono il ricalcolo perché qui coincidono. **norma certa** per gli esempi, **prassi-interpretazione** per la lettura. Nota: l'allegato scrive «489,75 (6% di 1500,00)», ma 489,75 è il 32,65%: è un refuso evidente del testo ufficiale.

B5. **Unità di euro: origine e contrasto.**
- Gestione privata: DT p. 52 dice che l'imponibile è in unità di euro. **norma certa** (istruzione).
- Circ. INPS 208/2001: imponibili arrotondati all'unità, fino a 49 centesimi per difetto, contributi al centesimo. L'elenco delle gestioni trattate non comprende l'allora INPDAP. **norma certa** ([W]). La base richiamata è la delibera CdA INPS 1123/1998 con la circolare del Ministero del Lavoro 83/2001, che applica in assenza di norma specifica l'art. 5 Reg. CE 1103/97 (lette solo come riportate nella circolare).
- USR Piemonte 2004 (circ. 3839, sintesi per il personale scolastico): base imponibile all'unità di euro e ritenute al centesimo. Non è una fonte INPDAP e riguarda un altro comparto. **prassi-interpretazione**, valore storico ([T]).
- Fonte INPDAP coeva sul comparto Enti Locali: non trovata. **da verificare**.

B6. **Controlli 00171I, 00172I** (MAN v1.0, solo estratti [E]; pagine non note). **da verificare** tutto il punto.
- 00171I (con 00176I, 00181I, 00213I, 00218I): `Imponibile` più `ImportoCong` se positivo, di GestPensionistica, deve essere ≥ somma degli imponibili di `AltroEnteVersante` con tipo contributo 1, 2, 3, 29 o 30.
- 00172I (con 00177I, 00182I, 00183I, 00214I, 00219I): `Contributo`, più `ContribCongPens` se positivo, più `Contrib1PerCento` in somma algebrica, deve essere ≥ somma dei contributi degli stessi tipi.
- Controlli analoghi esistono per TFR, TFS (00192I), ENPDEP, ENAM e credito.
- Estratti non chiari su una soglia di 1,27 euro per contributo zero nel credito (00061I). Non so interpretarla senza il testo.
- Conseguenza se confermata: basta 1 centesimo in più negli EV per l'errore; 1 centesimo in meno non lo fa scattare. Il builder `uniemens-builder-dma2` segnala anche il residuo (`Math.abs(diff) > 0.005`): è più severo, ed è una scelta del tool. Il catalogo tool lo classifica come comportamento osservato del software di controllo. **prassi-interpretazione**.
- Il Software di controllo v. 4.2.0 (manuale v1.9, [T]) non cita questi codici né tolleranze: non è la fonte delle regole.

B7. **Tolleranze INPS: nessuna trovata per la gestione pubblica.**
- CSA (note del 13/05/2019, gestionale universitario, [T]) usa una tolleranza di "0.99 centesimi" quando ricostruisce l'imponibile TFS dal contributo, e riassorbe fino a 99 centesimi di eccedenza negli EV dovuta agli arrotondamenti. Afferma anche che il controllo INPS applica il 9,6 all'imponibile TFS. Sono scelte e affermazioni di un fornitore, non INPS. **prassi-interpretazione**. Danno però due indizi: esiste un confronto contributo/imponibile sul TFS e l'errore da ripartizione proporzionale è reale.
- INPS Filiale di Milano, 16/12/2021 ([T], gestione privata): imponibile 2.098, aliquota 38,82%, 814,4436 si arrotonda a 814,44; averlo portato a 814,45 ha generato una regolarizzazione di 4 centesimi, perché «l'importo della differenza non è rilevante» (dicitura riferita alle proposte Vig). **norma certa** come prassi di sede, solo privati; per il pubblico è un'analogia, **prassi-interpretazione**.
- Note di Rettifica della gestione pubblica: procedura segnalata col Messaggio 4025/2017, letto solo in sintesi di dottrinalavoro.it, nessuna soglia indicata. **da verificare**.
- Il catalogo tool riporta tolleranze interne: 0 contro F24 EP, 0,05 contro CU. **prassi-interpretazione**.

B8. **Rapporto con il versamento.** La causale P201 è "Cassa C.P.D.E.L." e P607/P608/P632/P909 coprono TFS, TFR, ulteriori elementi e credito nella tabella codici F24 EP aggiornata all'01/10/2026 ([T], P201 a p. 30). Nessuna fonte aperta dice come passare dagli importi individuali al totale di causale. **norma certa** per le causali. Una risposta su lapostadelsindaco.it (28/09/2023) sostiene di sommare gli importi non arrotondati e arrotondare in F24 per un caso di cantieristi. **prassi-interpretazione**, non ufficiale. Per la ListaPosPA l'argomento non regge in modo automatico: la denuncia individuale è già al centesimo, e la quadratura di norma si fa contro la somma degli importi dichiarati. Propongo la somma degli importi individuali arrotondati. **prassi-interpretazione**, da confermare (Domande aperte).

B9. **Massimale.** Il massimale annuo per il 2025 è 120.606,90, arrotondato a 120.607,00 (Circ. 26/2025 p. 6; lo stesso valore in CUI). È un valore già arrotondato da INPS: si registra come parametro, non si calcola. **norma certa** (istruzione). Per la circolare 2026 non verificato.

### C. IRPEF e conguaglio

C1. **Art. 11 TUIR** (vigente dal 01/01/2026 al 31/12/2026): scaglioni in euro interi, nessuna regola di arrotondamento nell'estrazione. **norma certa** con riserva [W].

C2. **Art. 3 TUIR** (rubrica "Base imponibile", vigente fino al 31/12/2026): nessuna regola di arrotondamento. La verifica richiesta dà esito negativo. **norma certa** con riserva [W].

C3. **Art. 51 TUIR**: nessuna regola di arrotondamento; contiene soglie già in euro con decimali (258,23; 3.615,20). Si usano come parametri. **norma certa** con riserva [W].

C4. **Art. 23 DPR 600/1973** (vigente dal 21/05/2022 al 31/12/2026): c. 2, lett. a) ragguaglia scaglioni e detrazioni al periodo di paga; c. 3 regola il conguaglio entro il 28 febbraio o alla cessazione. Nessun arrotondamento. **norma certa** con riserva [W]. Non esiste quindi una regola letta su quanti decimali abbia la ritenuta in corso di calcolo. Fino all'esposizione, il calcolo può restare esatto. **prassi-interpretazione**.

C5. **Dichiarazione del contribuente.** L. 935/1977, art. 1, c. 1: importi delle dichiarazioni dei redditi, escluse quelle dei sostituti, arrotondati a mille lire, con calcoli svolti sugli arrotondati. Il testo è ancora in lire. L'istruzione 730 p. 16 applica oggi l'unità di euro. **norma certa** per i due testi; il collegamento tra i due è **prassi-interpretazione**. Questo riguarda il dipendente, non il calcolo del sostituto; rileva per gli importi del 730-4.

C6. **730-4.** Un estratto delle specifiche 730-4 2009 indica unità di euro. Le specifiche correnti non sono state lette. **da verificare**.

C7. **Soglia 12 euro.** Il sostituto non versa né rimborsa ciascuna imposta o addizionale se l'importo della dichiarazione è ≤ 12 euro (730 p. 8). Si applica al conguaglio da assistenza fiscale. **norma certa** (istruzione). Fonte normativa primaria non letta. **da verificare**.

C8. **Altre soglie non pertinenti.**
- Art. 3, c. 10, DL 16/2012: niente accertamento e riscossione sotto 30 euro, vigente fino al 31/12/2026, abrogato dal 2027 (Normattiva [W]). Vincola gli uffici, non la trattenuta. Non si implementa. **norma certa**, **prassi-interpretazione** sulla non pertinenza.
- Art. 123 D.Lgs. 33/2025 (letto su miolegale.it, non primaria; fonte citata art. 1, c. 168, L. 296/2006): arrotondamento all'unità e minimi per crediti di modesta entità e tributi locali. **da verificare**. Non riguarda la ritenuta del sostituto. **prassi-interpretazione**.

### D. Addizionali regionali e comunali

D1. **Comunale.** Acconto 30% del dovuto; rate fino a 9 per l'acconto da marzo, fino a 11 per il saldo; in unica soluzione alla cessazione (D.Lgs. 360/1998, art. 1, c. 4-5). Nessuna regola di arrotondamento nell'estrazione. **norma certa** con riserva [W].

D2. **Regionale.** Calcolata in sede di conguaglio, trattenuta in max 11 rate dal periodo di paga successivo, unica soluzione alla cessazione (D.Lgs. 446/1997, art. 50, c. 4). Nessuna regola di arrotondamento nell'estrazione. **norma certa** con riserva [W].

D3. **Rata.** Se il totale non è divisibile esattamente, nessuna fonte aperta dice dove va il resto. Assegnarlo all'ultima rata garantisce che la somma trattenuta coincida col dovuto: **prassi-interpretazione**. Il vincolo discende dalla CU, che espone gli importi dovuti e trattenuti (punti 22-29, CUI).

D4. **Esposizione.** Importo dovuto, trattenuto, acconto sono al centesimo nella CU (CUI p. 17). **norma certa** (istruzione).

### E. F24 EP e F24

E1. **F24 EP.** Importi in centesimi di euro (F24EP p. 4); `Saldo totale a debito` con due decimali, coerente con la somma dei saldi dei record V (p. 9). La pagina di Agenzia Entrate elenca solo specifiche tecniche, provvedimento 154279/2015 e tabella codici. La specifica rimanda a "Specifiche di Compilazione" per il tipo riga, non trovate sulla pagina. **norma certa** (istruzione); **da verificare** le Specifiche di Compilazione.

E2. **Regola per F24 ordinario.** Sempre due decimali; terza cifra ≥ 5 per eccesso (52,755 → 52,76), altrimenti per difetto (AVV p. 1; scheda intermediari [W]). **norma certa** (istruzione). Non ho trovato un testo che la estenda al F24 EP: **prassi-interpretazione** applicarla anche lì. In pratica è la stessa regola.

E3. **Nessuna base di legge trovata per il centesimo in F24.** Le avvertenze non citano una norma. La connessione con D.Lgs. 241/1997 non è stata letta. **da verificare**. Anche la scheda archivio Unico 2007 ([W]) distingue: importi di dichiarazione all'unità, importi rielaborati (acconti, rate) al centesimo. Regole non correnti.

E4. **Art. 51 D.Lgs. 213/1998.** Riguarda la conversione in euro di sanzioni penali e amministrative espresse in lire; il c. 3 elimina i decimali. Le avvertenze F24 lo richiamano in quel solo senso (AVV p. 1). **Non è una regola su contributi né su F24.** **norma certa**.

### F. CU e 770

F1. **Base di legge.** Art. 3, c. 12, DL 16/2012 sostituisce il c. 2 dell'art. 1 L. 935/1977: per i sostituti, dall'anno d'imposta 2012, importi «espressi in euro mediante arrotondamento alla seconda cifra decimale». **norma certa** ([W], due letture concordi). Il c. 12 non risulta abrogato. Il testo previgente non è stato letto: **da verificare** come si esponevano gli importi prima del 2012.

F2. **CU.** Regola con esempi 55,505 → 55,51; 65,626 → 65,63; 65,493 → 65,49 (CUI p. 17 per i dati fiscali; p. 68 per quelli previdenziali). Specifiche: tutti gli importi alla seconda cifra decimale (CUS §3.2.2.1, p. 13). **norma certa**.

F3. **770.** Regola uguale (770I §4.1, p. 7; 770S §2.5.3, p. 10). **norma certa**.

F4. **Tolleranze dei controlli telematici (non sono regole di calcolo).**
- CU: € 1 per controllo contabile salvo diversa indicazione (CUS p. 17); in vari campi 2, 3 o 4 euro. **norma certa**.
- 770: per somme e sottrazioni il risultato ammette uno scostamento di 0,5 + 0,01 per ciascun addendo o sottraendo (meno 0,01 al massimo); per moltiplicazioni e divisioni ±1 (770S p. 11). **norma certa**.
- Queste tolleranze non vanno usate come margine di calcolo: dicono solo quando un file è respinto. **prassi-interpretazione**.

### G. Cambi di vigenza

G1. **TUIR.** Normattiva mostra il DPR 917/1986 abrogato da D.Lgs. 19/06/2026 n. 117 nel testo in vigore dal 01/01/2027. **norma certa** ([W]). Il carattere compilativo e l'applicazione dal 2027 (art. 377) risultano solo da fonti secondarie. **da verificare**.

G2. **Art. 23 DPR 600.** Abrogato con effetto dall'01/01/2027 dal D.Lgs. 33/2025 come modificato dal DL 200/2025 (Normattiva). **norma certa**. La corrispondenza con l'art. 33 del D.Lgs. 33/2025 viene da miolegale.it. **da verificare**. Quella pagina riporta "in vigore dal 7 agosto 2026", in conflitto con le altre date: da risolvere sul testo.

G3. **Nessuna variazione trovata sulle regole di arrotondamento** per il passaggio al 2027, ma i nuovi testi non sono stati letti. **da verificare**.

## Implicazioni per il nucleo

**Modalità.** `arrotonda(valore, 2)` con `ROUND_HALF_UP` copre tutte le regole lette: ListaPosPA, F24, CU, 770. La regola "guarda la terza cifra" e il mezzo per eccesso coincidono su valori positivi, perché le cifre successive non cambiano l'esito (814,4436 → 814,44; 74,955 → 74,96). **prassi-interpretazione** (verifica aritmetica).

**Negativi.** `Decimal.quantize` con `ROUND_HALF_UP` allontana da zero (-1,005 → -1,01). Il tracciato ammette negativi (V1 causale 7, `Contrib1PerCento`) e la specifica CU/770 ha la configurazione VN, ma le fonti non dicono nulla sul mezzo centesimo negativo. L'interpretazione simmetrica sul valore assoluto è coerente col codice attuale. **prassi-interpretazione**. Consiglio un test esplicito su questo caso.

**Modalità aggiuntive.** Nessuna "per difetto" né "dispari" richiesta. `arrotonda(valore, 0)` serve per gli importi del 730 e per la gestione privata, non per la fetta CPDEL.

**Oltre `arrotonda`.** Una primitiva di **ripartizione con residuo** è da valutare, anche se non necessaria per la prima fetta: serve per rate di addizionali, per distribuire su Enti Versanti e, in futuro, per i V1 cumulativi. Il vincolo è che la somma delle parti non superi il totale (00171I/00172I, da confermare). La grammatica attuale non può esprimerla: può diventare un'operazione del motore, non una formula. **prassi-interpretazione**.

**Dove applicare `arrotonda` nella fetta CPDEL.** **prassi-interpretazione**, salvo i formati.

| Importo | Formula di esempio | Note |
|---|---|---|
| Imponibile pensionistico | Somma degli importi di istituto, `arrotonda(..., 2)` se non già al centesimo | Niente unità di euro |
| Contributo CPDEL totale | `arrotonda(importo.imponibile_cpdel * parametro.aliquota_cpdel_totale, 2)` | Valore da esporre; è la proposta B3 |
| Quota lavoratore | `arrotonda(importo.imponibile_cpdel * parametro.aliquota_cpdel_lavoratore, 2)` | Trattenuta in busta, punto 20 CU |
| Quota ente | `importo.contributo_cpdel_totale - importo.quota_cpdel_lavoratore` | Nessun arrotondamento proprio |

Le aliquote devono essere parametri con vigenza (la grammatica ammette solo costanti intere: rispettato).

**Non arrotondare a metà catena.** Le aggregazioni per persona (CU) e per ente (F24 EP) devono sommare importi già arrotondati, senza ricalcolare e arrotondare di nuovo. Così si conserva la quadratura tra le viste. Tutte le viste leggono gli stessi importi. **prassi-interpretazione**.

**Vista ListaPosPA.** Serializzatore separato dal calcolo: virgola decimale, nessuno zero iniziale, massimo 2 decimali, `0` ammesso. Lo schema XSD è un oracolo di formato utile per i test. **norma certa** per il formato.

**Tracciabilità e riferimenti.**
- Ogni regola di esposizione cita DT, versione e pagina.
- Le regole IRPEF citano il riferimento con vigenza, perché dal 2027 cambia. Il ticket #3 (`modelli-temporali.md`) cita TUIR e art. 23: il cambio riguarda anche quei riferimenti.
- Le tolleranze (CU, 770, tool) stanno nei confronti e nelle verifiche, mai nelle formule di calcolo.

## Decisioni del 06/11/2026

- **Contributo CPDEL (B3): deciso dall'utente.** Totale e quota lavoratore si arrotondano ciascuno al centesimo, e la quota ente è la differenza. È una scelta di progetto (**prassi-interpretazione**), non una regola letta: va rivista se il manuale o INPS indicano altro.
- **Aliquote CPDEL.** Il vault `vault-pa` riporta 23,80 + 8,85 = 32,65 dal 01/01/2007 (pagina "Aliquote Contributive Storiche", tabella D INPDAP, `authority: secondaria`, `review_state: da_rivedere`). Il totale è coerente con gli esempi del Messaggio 749/2024; la ripartizione va ancora riscontrata su una fonte primaria prima di entrare nel corpus.
- **Manuale ListaPosPA.** Lettura rinviata dall'utente: i punti che ne dipendono restano **da verificare**.

## Domande aperte

1. **Manuale ListaPosPA v1.0: lettura diretta, rinviata.** Serve il permesso di scaricare il PDF (`937KEY-manuale_lista_pospa_v1-13_02_2018.pdf`, 10,6 MB, da inps.it), oppure che l'utente lo fornisca. Da verificare: testo e pagine di 00171I/00172I/00061I, eventuali tolleranze, eventuale controllo imponibile × aliquota, e se il manuale v1.0 del 2018 è ancora allineato al DT 2026.
2. **Conferma del metodo per il contributo CPDEL (B3), già deciso per la fetta.** Possibili verifiche: il manuale, una richiesta a INPS, oppure il confronto con flussi reali già accettati, che spetta all'utente fare in ambiente protetto.
3. **Imponibile ListaPosPA con centesimi:** le istruzioni lo prevedono. Serve una conferma che non esistano note INPDAP/INPS ancora in vigore che prescrivano l'unità di euro (B5).
4. **Quadratura denunce/F24 EP:** somma degli arrotondati o arrotondamento della somma? Cercare l'eventuale soglia delle Note di Rettifica. Serve il testo del Messaggio 4025/2017 (l'URL noto dà 404).
5. **Art. 5 Reg. CE 1103/97:** non letto; verificare il testo se si vuole citarlo come base generale.
6. **Rate e resto delle addizionali:** nessuna fonte ufficiale trovata. Confermare la scelta dell'ultima rata.
7. **Fonte primaria della soglia 12 euro del 730-4 e specifiche 730-4 correnti** (formato degli importi).
8. **F24 EP:** reperire le "Specifiche di Compilazione" citate dalla specifica tecnica.
9. **Nuovi testi unici dal 2027:** leggere D.Lgs. 117/2026 e D.Lgs. 33/2025 (art. 33, art. 123) e aggiornare i riferimenti delle regole.

## Fonti

Letture [T] e [W] come in Metodo. Le pagine sono quelle del PDF.

**INPS**
- **DT** [T]: Documento tecnico UniEmens v. 4.33, 29/09/2026, pp. 31, 52, 176, 188-193, 195, 214: https://www.inps.it/content/dam/inps-site/pdf/prestazioni-e-servizi/uniemens-enti-amministrazioni/UniEMENSind.pdf
- Copia v. 4.29 del 28/02/2025 (solo intestazione letta): https://www.inps.it/content/dam/inps-site/pdf/prestazioni-e-servizi/uniemens-aziende-private/UniEMENSind_Documento_Tecnico.pdf
- **AT** [T]: Allegato tecnico v. 4.33.1, 30/10/2026, appendice B, p. 251: https://www.inps.it/content/dam/inps-site/pdf/prestazioni-e-servizi/uniemens-aziende-private/UniemensInd_AllegatoTecnico.pdf
- **XSD** [T]: schema 4.33.1: https://www.inps.it/content/dam/inps-site/pdf/prestazioni-e-servizi/uniemens-aziende-private/UniEMENSind.zip
- **MAN** [E, non aperto]: Manuale ListaPosPA v1.0, 13/02/2018: https://www.inps.it/content/dam/inps-site/pdf/prestazioni-e-servizi/uniemens-enti-amministrazioni/937KEY-manuale_lista_pospa_v1-13_02_2018.pdf
- Scheda servizio [W]: https://www.inps.it/it/it/dettaglio-scheda.it.schede-servizio-strumento.schede-servizi.50270.trasmissione-uniemens-per-enti-e-amministrazioni.html
- Messaggio 749/2024 [T]: https://www.inps.it/content/dam/inps-site/it/scorporati/circolari-e-messaggi/2024/02/Circolare_14482/Allegati/14759_Messaggio-numero-749-del-20-02-2024.pdf e Allegato 1 [T], casi 1-3: https://www.inps.it/content/dam/inps-site/it/scorporati/circolari-e-messaggi/2024/02/Circolare_14482/Allegati/14760_Messaggio-numero-749-del-20-02-2024_Allegato-n-1.pdf
- Circ. 208/2001 [W]: https://servizi2.inps.it/servizi/Bussola/visualizzadoc.aspx?sVirtuaLURL=%2Fcircolari%2FCircolare+numero+208+del+27-11-2001.htm
- Circ. 26/2025 [T], p. 6: https://www.inps.it/content/dam/inps-site/it/scorporati/circolari-e-messaggi/2025/01/Circolare_14806/Allegati/15874_Circolare-numero-26-del-30-01-2025.pdf
- INPS Filiale di Milano, 16/12/2021 [T], caso 1, ospitato dai consulenti del lavoro di Milano: https://consulentidellavoro.mi.it/wp-content/uploads/2023/06/UniEMens-principali-problemi-e-segnalazioni.pdf
- Manuale software di controllo v1.9 [T]: https://www.inps.it/content/dam/inps-site/software/2026/06/890/allegatisoftware/Manuale%20Operativo%20v1.9.pdf
- Manuale utente GDP v3.0, 2024 [T] (solo virgola decimale, nessuna regola di arrotondamento): https://www.inps.it/content/dam/inps-site/pdf/allegati/Manuale_Utente_GDP_Compilazione_Manuale_Denuncia_Mensile_Ver_3.0_2902_2024.pdf
- Istruzioni operative DMA2, parte prima, v. 1.0 [T], copia non ufficiale, nessuna occorrenza di arrotondamenti: https://www.snalsbrindisi.it/documenti/doc/INPS1.pdf

**Agenzia delle Entrate**
- **CUI** [T]: istruzioni CU 2026, pp. 17, 68, 74: https://www.agenziaentrate.gov.it/portale/documents/20143/9602395/CU_istruzioni_2026.pdf/4184818b-05a3-acce-5956-70811c7d2233
- **CUS** [T]: specifiche CU 2026, pp. 13, 17: https://www.agenziaentrate.gov.it/portale/documents/20143/9602395/Specifiche+tecniche+CU+2026.pdf/8ae9a839-cd72-207d-6100-327884e9ac03?t=1768503443615
- **770I** [T]: istruzioni 770/2026, §4.1, p. 7: https://www.agenziaentrate.gov.it/portale/documents/20143/9771798/770_istr_2026.pdf/6175653a-80b7-42a6-cd77-4e48609d0dfc?t=1772197125449
- **770S** [T]: specifiche 770/2026, §2.5.3, pp. 10-11: https://www.agenziaentrate.gov.it/portale/documents/20143/9771798/Specifiche+770+2026.pdf/6ce9eff6-6f3c-840d-a80d-6c992096e3f3?t=1772197099329
- **730** [T]: istruzioni 730/2026, pp. 8, 16: https://www.agenziaentrate.gov.it/portale/documents/20143/9764684/730_+istruzioni_2026.pdf/2ac8d27a-fa3d-ed9e-ffc1-9bf61457661e
- **F24EP** [T]: specifiche tecniche, dicembre 2016, pp. 4, 6, 9: https://www.agenziaentrate.gov.it/portale/documents/20143/344093/Provvedimento+del+1122015+F24+EP_allegato+2+-+specifiche+tecniche+F24+EP+dicembre+2016+(2).pdf/92a0df69-e9f4-adb5-5339-415ada83da88
- Provvedimento F24 EP 08/11/2007 [T], art. 1: https://www.agenziaentrate.gov.it/portale/documents/20143/347896/Provvedimento+08+11+07+F24+enti+pubblici_Provvedimento_20F24_20EP.pdf/f8d8709d-834a-6fed-65aa-4411497b1289
- Tabella codici F24 EP, 01/10/2026 [T], p. 30: https://www.agenziaentrate.gov.it/portale/documents/d/guest/tabella-codici-tributo-f24ep-aggiornata-al-1-ottobre-2026
- Scheda specifiche F24 EP [W]: https://www.agenziaentrate.gov.it/portale/schede/pagamenti/f24-enti-pubblici-f24_enti_pub/f24_ep_enti-pubblici
- **AVV** [T]: avvertenze F24 (metadati 2013), p. 1: https://www.agenziaentrate.gov.it/portale/documents/20143/250689/Avvertenze+per+la+compilazione+del+modello_Avvertenze+modello+F24.pdf/fa5458b1-c37b-23db-a395-a730fe393fc5
- Scheda F24 intermediari [W]: https://www.agenziaentrate.gov.it/portale/schede/pagamenti/f24/casi-frequenti-f24-intermediari
- Unico PF 2007, archivio [W]: https://www.agenziaentrate.gov.it/portale/archivio/modelli-e-istruzioni/modelli-2008-2016/modelli-di-dichiarazione/2007/unico-pf-2007/fascicolo_1/1_istruzioni_generali/6_come_si_eseguono_i_versamenti.html

**Normattiva** [W], vigente al 06/11/2026 salvo diversa indicazione
- D.Lgs. 213/1998, artt. 3, 51 (testo letto senza `!vig`; ultimo aggiornamento atto 11/11/2015): https://www.normattiva.it/uri-res/N2Ls?urn:nir:stato:decreto.legislativo:1998-06-24;213~art51
- L. 935/1977, art. 1: https://www.normattiva.it/uri-res/N2Ls?urn:nir:stato:legge:1977-12-23;935~art1!vig=2026-11-06
- DL 16/2012, art. 3, cc. 10, 12: https://www.normattiva.it/uri-res/N2Ls?urn:nir:stato:decreto.legge:2012-03-02;16~art3!vig=2026-11-06
- TUIR, artt. 3, 11, 51: https://www.normattiva.it/uri-res/N2Ls?urn:nir:stato:decreto.del.presidente.della.repubblica:1986-12-22;917~art11!vig=2026-11-06
- DPR 600/1973, art. 23: https://www.normattiva.it/uri-res/N2Ls?urn:nir:stato:decreto.del.presidente.della.repubblica:1973-09-29;600~art23!vig=2026-11-06
- D.Lgs. 360/1998, art. 1 (senza `!vig`): https://www.normattiva.it/uri-res/N2Ls?urn:nir:stato:decreto.legislativo:1998-09-28;360~art1
- D.Lgs. 446/1997, art. 50 (senza `!vig`): https://www.normattiva.it/uri-res/N2Ls?urn:nir:stato:decreto.legislativo:1997-12-15;446~art50

**Fonti non primarie** (solo pista o contrasto, mai per **norma certa**)
- USR Piemonte, circ. 3839/2004, sintesi [T]: https://www.info-scuole.it/doc/anni-precedenti/retribuzioni/ritenute/usr-piemonte_circ_3839_2004-sintesi.pdf
- Note CSA del 13/05/2019 [T]: https://mailman.unipa.it/pipermail/operatori_csa/attachments/20190513/a071015d/attachment.pdf e https://mailman.unipa.it/pipermail/operatori_csa/attachments/20190513/26e999c1/attachment.pdf
- La Posta del Sindaco, 28/09/2023 [W]: https://lapostadelsindaco.it/servizi-pubblica-amministrazione/33064/calcolo-dellarrotondamento-in-sede-di-versamento-con-f24-ep
- Dottrina Lavoro su Messaggio 4025/2017 [W]: https://www.dottrinalavoro.it/notizie-c/inps-invio-note-di-rettifica-gestione-pubblica
- Miolegale, art. 123 D.Lgs. 33/2025 [W]: https://miolegale.it/testi-unici/versamenti-riscossione/art-123/ e art. 33 [E]: https://miolegale.it/testi-unici/versamenti-riscossione/art-33/
- D.Lgs. 117/2026, sintesi [E]: https://edotto.com/articolo/nuovo-testo-unico-imposte-sui-redditi-in-gu-cosa-cambia-dal-1-gennaio-2027
- Specifiche 730-4 2009 [E]: https://www.agenziaentrate.gov.it/portale/documents/20143/433460/Allegato+B+-+spectecn+modello+730+4+2009_ALLEGATO_B_Specifiche_730-4_2009.pdf/dd79dea0-848d-dbd5-bb58-c015f8af4c3a
- Allegato 1 alla Circ. INPS 13/2011 [E]: https://servizi2.inps.it/CircolariZIP/circolare%20numero%2013%20del%2028-01-2011_Allegato%20n%201.pdf
