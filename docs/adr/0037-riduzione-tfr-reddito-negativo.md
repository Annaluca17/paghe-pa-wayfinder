# Riduzione del lordo TFR: reddito negativo di lavoro dipendente

La riduzione del lordo di chi è in regime TFR riduce l'imponibile fiscale. Il nucleo la tratta come retribuzione in meno: l'istituto `riduzione_tfr` dichiara nel corpus la categoria di reddito `lavoro_dipendente`, e il suo importo, che è negativo, entra tra i redditi del pagamento. La ritenuta, il conguaglio, il reddito annuo stimato e l'imponibile fiscale della persona si calcolano sul lordo già ridotto.

Corregge l'ADR 0010 e la precisazione dell'ADR 0015, che dicevano «la riduzione resta senza effetti fiscali».

Scelto perché il DPCM 20/12/1999 art. 1 dice due cose (**norma certa** per il testo):

- c. 2: la soppressione del contributo del 2,50% «non determina effetti sulla retribuzione imponibile ai fini fiscali»;
- c. 3: la retribuzione lorda è ridotta in misura pari al contributo soppresso, per assicurare «l'invarianza della retribuzione netta complessiva».

Il contributo soppresso si deduceva dall'imponibile (art. 51 c. 2 lett. a TUIR). Perché imponibile e netto restino quelli di prima, la riduzione deve prenderne il posto anche nel fisco. Con la lettura precedente un dipendente in TFR pagava più IRPEF di uno identico in TFS, e il netto non era invariato. Che la riduzione scenda dall'imponibile è **prassi-interpretazione** (nota di prassi 11): nessuna circolare letta lo scrive.

Trovato con il confronto su un ente reale (ottobre 2026): su tutti i dipendenti in TFR l'imponibile del nucleo superava quello del gestionale in uso esattamente della riduzione.

## Considered Options

- **Dichiarazione di deduzione fiscale, come i contributi del lavoratore:** le deduzioni si sottraggono e sono positive; la riduzione è negativa e servirebbe un segno a parte. Entrerebbe anche tra i contributi letti dalla sostitutiva sull'accessorio, che contributo non è.
- **Cambiare la maturazione della riduzione da `periodo` a una retributiva:** entrerebbe nelle basi e nella denuncia; l'ADR 0010 la vuole fuori da entrambe.
- **Lasciare com'era e correggere al conguaglio:** il conguaglio usa lo stesso imponibile, l'errore resterebbe.

## Consequences

- **Un importo derivato può essere reddito, se l'istituto lo dichiara.** `attribuisci_reddito` congela categoria e anno d'imposta anche su un importo sul periodo o sul mese che ha una dichiarazione `[[reddito]]`; senza dichiarazione resta com'era. Contributi, ritenute e benefici non ne hanno e non cambiano.
- **Nelle basi contributive non cambia nulla:** CPDEL, Fondo Credito, TFS e TFR restano sul lordo prima della riduzione (ADR 0010).
- **CU e 770** leggono i redditi dagli esiti: il reddito di lavoro dipendente certificato scende della riduzione.
- **Dal 2027** la dichiarazione rinvia all'art. 51 del D.Lgs. 117/2026: il rinvio del c. 2 del DPCM al nuovo testo unico è **da verificare**.
- **Seconda fonte.** Una circolare INPDAP, INPS o RGS che scriva l'effetto fiscale porterebbe la regola a norma certa.
