# IRAP: base per titolo, regione della sede di lavoro, scadenza della delega

L'**IRAP** col metodo retributivo (art. 10-bis D.Lgs. 446/1997) è un istituto a carico dell'ente. L'**acconto mensile** si calcola sugli emolumenti pagati nel mese e si versa nella delega F24EP del mese dopo, codice 380E. Il fermo dichiarato «irap» dell'ADR 0023 sparisce: restano solo fermi mirati.

**Scadenza.** È la scadenza della delega: il 16 del mese dopo il pagamento, con lo slittamento dei festivi (art. 32-ter DL 185/2008 fino al 2026, art. 4 D.Lgs. 33/2025 dal 2027, **norma certa**). Il D.M. 421/1998, il decreto dell'art. 30 c. 5, dice il 15: nessun testo letto concilia le due date, **da verificare**.

**Riferimento del 380E.** Mese di pagamento delle retribuzioni (`00MM`) e anno. La norma conta gli emolumenti «corrisposti nel mese precedente» (art. 30 c. 5, **norma certa**).

**Regione.** La regione di un rapporto viene dalla **sede di lavoro**, fatto datato sul rapporto (art. 4 c. 2, **norma certa**). Se il fatto manca vale la regione dell'ente. Ogni rapporto versa nella regione della sua sede nel mese di pagamento: una riga 380E per regione, con il codice regione. Un cambio di sede da meno di tre mesi dà un avviso: la soglia dei tre mesi è un conto annuale che riguarda il saldo, fuori ambito.

**Aliquota.** 8,5% come parametro datato nazionale (art. 16 c. 2, con le istruzioni IRAP come seconda fonte). Una regola regionale datata può sostituirla, perché le Regioni possono ridurre o azzerare l'aliquota, non aumentarla (art. 16 c. 3; art. 5 D.Lgs. 68/2011).

**Base per titolo.**
- **Dipendenti:** imponibile previdenziale del pagamento, per cassa: gli arretrati entrano nel mese in cui si pagano (ris. AdE 29/E/2010, **prassi**). TFR e TFS non entrano.
- **Co.co.co.:** compenso al netto della quota di gestione separata a carico del collaboratore. Scelta di Luca: la fonte non è leggibile, **da verificare**.
- **Amministratori:** importo imponibile IRPEF delle indennità e dei gettoni; gli oneri dell'art. 86 TUEL restano fuori (ADR 0016). Fine mandato al netto di 309,87 € per anno di mandato (ris. AdE 29/E/2010, **prassi**).
- **LSU:** solo l'integrazione pagata dall'ente. È una deduzione dalla ris. 378/E/2008, **da verificare**.
- **Esclusione dalla base IRAP:** fatto datato sul rapporto con il motivo (disabile, apprendista, CFL). L'acconto si calcola senza quella persona (art. 11 c. 1 lett. a n. 5; istruzioni IRAP, rigo IK4, **prassi**). La deduzione dell'art. 11 c. 4-octies e quella per ricerca e sviluppo non valgono per il metodo retributivo.

**Fermi.** Comando e convenzione (segretario) fermano l'IRAP del rapporto. La direzione è «paga chi eroga, e chi rimborsa sulla quota rimborsata», come il distacco nelle istruzioni, ma i rimborsi tra enti non sono ancora modellati. Gli enti che versano fuori dall'F24EP (codice 3858) sono fuori ambito.

Scelto da Luca l'08/11/2026 nel grilling del ticket #81, sulla ricerca `docs/research/irap-scadenza-riparto.md`. Chiude i punti aperti dell'ADR 0023 su scadenza, riparto per regione, LSU, co.co.co. e fine mandato.

## Considered Options

- **15 del D.M. 421/1998:** regolamento contro legge, e una seconda scadenza nella stessa delega.
- **Fermo quando le regioni del mese sono più di una:** più prudente, ma ferma un caso che ha già una regola naturale, la sede.
- **Regione dal domicilio del dipendente:** errore noto, l'art. 4 c. 2 conta la sede.
- **Co.co.co. al lordo:** suggerito dalla ricerca come prudente, scartato da Luca.
- **Comando subito a chi eroga:** richiede i rimborsi tra enti, che il modello non ha.

## Consequences

- Nuovi fatti sul rapporto: sede di lavoro (con regione) ed esclusione dalla base IRAP.
- Il codice regione entra nella delega per il 380E: oggi un codice con `codice_campo = "regione"` ferma la delega.
- Da verificare: il 15 contro il 16; il mese del riferimento A su un F24EP reale; i co.co.co. al netto; LSU; comando e convenzione; il testo intero dell'art. 11 c. 1 lett. a n. 5; il TFS per analogia col TFR.
