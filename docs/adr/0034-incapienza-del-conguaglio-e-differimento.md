# 0034. Incapienza del conguaglio e richiesta di differimento

Data: 2026-11-09. Ticket #99. Segue l'ADR 0019.

## Contesto

Fino a oggi un conguaglio IRPEF a debito che portava il netto del pagamento sotto zero fermava il rapporto
(«netto negativo»). L'art. 23 c. 3 D.P.R. 600/1973 (dal 2027 art. 33 c. 4 D.Lgs. 33/2025) regola il caso: se le
retribuzioni non bastano, la persona può chiedere per iscritto di trattenere il resto nei periodi di paga successivi
con l'interesse dello 0,50% mensile; l'importo non trattenuto al termine del periodo d'imposta, per cessazione o
incapienza, si comunica alla persona, che lo versa entro il 15 gennaio. **norma certa** (ricerca
`parametri-fiscali-2026-2027.md`, tema 7).

## Decisione

- **Capienza** del conguaglio = netto del pagamento dopo tutte le altre righe (contributi, ritenuta, rate delle
  addizionali, benefici, trattenute a terzi). Il conguaglio IRPEF a debito si trattiene fino a portare il netto a
  zero; il resto è **incapienza**.
- Solo il conguaglio IRPEF. Il residuo delle addizionali trattenuto in chiusura, se il netto non basta, resta un
  fermo («netto negativo»).
- **Senza richiesta di differimento** il resto è **non trattenuto**: un importo del conguaglio che la vista CU legge.
- **Con la richiesta di differimento** (fatto della persona, datato) il resto è un **resto differito**, che non è un
  fatto: ogni pagamento successivo lo ricava dal precedente, come il riporto dei recuperi. Ogni pagamento trattiene
  resto più interesse fino a capienza.
- **Interesse**: semplice, 0,50% per ogni mese di differimento sul resto aperto, parametro datato nel corpus; è un
  importo a sé. Il codice tributo F24EP dell'interesse sta nel corpus: se manca, il calcolo si ferma con nome.
- **Fine del differimento**: all'ultimo pagamento di dicembre dell'anno in cui si trattiene, o alla cessazione se
  viene prima. Il resto ancora aperto passa a non trattenuto. Lettura nostra di «al termine del periodo d'imposta»:
  **da verificare**.

## Conseguenze

- «Netto negativo» non ferma più un rapporto per il solo conguaglio IRPEF; resta per gli altri casi.
- Da verificare: il codice tributo F24EP dell'interesse e la lettura della fine del differimento.
