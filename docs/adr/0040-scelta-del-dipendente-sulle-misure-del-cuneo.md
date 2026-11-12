# Scelta del dipendente sulle misure del cuneo fiscale

Fino all'ADR 0039 il nucleo dava sempre, nel mese, somma esente, ulteriore detrazione e trattamento integrativo. Ora il dipendente può scegliere quando riceverli dal sostituto. Decisioni di Luca del 12/11/2026 (grilling del ticket #125) e sua precisazione su «nessuna».

## Decisioni

1. **Un dato della persona**, fatto datato con validità (dal/al) e documento di origine, stesso schema della dichiarazione del sostituito (`registra_scelta_cuneo`). Tre valori: **«nel mese»** (predefinito: vale anche se il dato non c'è), **«solo a conguaglio»**, **«nessuna»**. Vale dalla data in cui il dipendente lo comunica.
2. **Copre tutte e tre le misure**: somma esente (L. 207/2024 art. 1 c. 4), ulteriore detrazione (c. 6), trattamento integrativo (D.L. 3/2020 art. 1).
3. **Mese per mese** si segue la scelta in vigore nel mese di pagamento: con «solo a conguaglio» e «nessuna» il pagamento non riconosce somma esente né trattamento integrativo e la ritenuta non applica l'ulteriore detrazione.
4. **A conguaglio** (fine anno e fine rapporto) conta la scelta in vigore alla data del conguaglio, per tutto l'anno. Con «nel mese» o «solo a conguaglio» si dà lo spettante sul reddito vero meno il già dato; con «nessuna» lo spettante è zero e si recupera tutto il già dato (a rate oltre la soglia, in unica soluzione alla cessazione). Per l'ulteriore detrazione la differenza passa nell'IRPEF del conguaglio, come ogni detrazione.
5. **Significato di «nessuna»** (Luca): il sostituto non dà mai le misure, né nel mese né a conguaglio; il dipendente le chiede nel 730. Esempio: chi prevede altri redditi nell'anno ma non ne è certo preferisce non averle e vedere in dichiarazione se scattano.

## Fonti e livello di certezza

- **Norma certa, in senso contrario all'opzione**: L. 207/2024 art. 1 c. 7 (letto su Normattiva il 12/11/2026): i sostituti riconoscono la somma «in via automatica» al momento dell'erogazione, la spettanza si verifica a conguaglio. Nei commi 4-8 non c'è alcuna facoltà di rinuncia. Lo stesso per il trattamento integrativo: D.L. 3/2020 art. 1 c. 3, «in via automatica» (dal documento di ricerca, non riaperto il 12/11).
- **Prassi-interpretazione, a favore del recupero in dichiarazione**: circ. AdE 4/E del 16/05/2025 par. 1.2 (PDF letto per intero): se il sostituto non ha riconosciuto somma o ulteriore detrazione in sede di conguaglio, il lavoratore può beneficiarne nella dichiarazione dei redditi; lo stesso per chi non ha un sostituto.
- **Nessuna fonte letta** dà al dipendente la scelta «solo a conguaglio» o «nessuna» verso il sostituto, né dice che debba essere scritta. La circ. 4/E non contiene la frase «il lavoratore può chiedere di non riceverlo, per iscritto» che il documento di ricerca le attribuiva: riga corretta (`docs/research/somma-esente-trattamento-integrativo.md`).
- **Livello di questa regola: prassi operativa di Paghe PA, da verificare.** La ricerca la fa Luca (nota di prassi 14). Finché non c'è una fonte, il predefinito resta «nel mese», cioè l'automatismo di legge.

## Come è fatto

- Registro: tipo `scelta_cuneo`, valori `nel_mese`, `solo_conguaglio`, `nessuna`; un valore diverso o la mancanza del documento di origine è un errore. `scelta_cuneo(persona, giorno, istante)` dà la scelta in vigore e il fatto che la porta (nessun fatto = «nel mese»).
- Ritenuta del mese: l'ulteriore detrazione (la «detrazione automatica» della regola) entra solo con «nel mese». Conguaglio: entra salvo «nessuna». Il fatto della scelta è tra i fatti della derivazione.
- Benefici: `riconosciuti_del_mese` solo con «nel mese»; `al_conguaglio` con «nessuna» pone lo spettante a zero. Le rate di recuperi già decisi continuano comunque.
- Il calcolo dell'ulteriore detrazione «in più» per la soglia di 60 euro guarda la scelta di ogni mese.
- Nessun rapporto dell'ente di prova ha il dato: il mese di prova non cambia.

## Considered Options

- **Solo «nel mese» o «nessuna»:** più vicino a quel che la prassi dice (recupero in dichiarazione), ma Luca vuole anche «solo a conguaglio».
- **Niente scelta finché una fonte non la prevede:** prudente, ma Luca ha deciso la regola operativa e la ricerca la fa lui.
- **Scelta per singola misura:** più flessibile, scartata: un solo dato per le tre misure.

## Consequences

- Con «solo a conguaglio» il netto del mese è più basso e a dicembre c'è un conguaglio più ricco: possibile incapienza o differimento (ADR 0034) da gestire come per ogni conguaglio.
- Con «nessuna» il recupero del già dato dopo un cambio di scelta a metà anno è a rate (oltre 60 euro) e il dipendente può non ritrovarlo in dichiarazione se non soddisfa i requisiti.
- Restano da verificare: la fonte della facoltà, se la scelta debba essere scritta, la decorrenza («dalla data in cui il dipendente lo comunica») e la CU per i casi «nessuna» (punti 724-728, 718).
